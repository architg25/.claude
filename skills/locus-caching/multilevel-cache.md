# Multilevel Cache

Patterns for combining local Caffeine cache with distributed Locus cache.

## Architecture

```
┌─────────────────┐
│   Application   │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Caffeine│  ← L1: In-process, nanosecond latency
    │ (local) │
    └────┬────┘
         │ miss
    ┌────▼────┐
    │  Locus  │  ← L2: Distributed, millisecond latency
    │(remote) │
    └────┬────┘
         │ miss
    ┌────▼────┐
    │ Database│  ← Source of truth
    │(Decibel)│
    └─────────┘
```

## Basic Setup

### Configuration

```hocon
# Locus configuration
memcached {
  locus {
    projectId: "my-project"
    name: "my-service-locus"
    max-outstanding-requests: 20000
  }
}

# Caffeine configuration
caffeine {
  user-cache {
    maximumSize: 10000
    expireAfterWrite: 5m
  }
}
```

### Cache Implementation

```java
public class MultilevelUserCache {
    private final Cache<String, UserData> localCache;
    private final LocusClient locusClient;
    private final UserRepository database;

    @Inject
    public MultilevelUserCache(
            @Named("user-cache") Cache<String, UserData> localCache,
            LocusClient locusClient,
            UserRepository database) {
        this.localCache = localCache;
        this.locusClient = locusClient;
        this.database = database;
    }

    public CompletableFuture<UserData> get(String userId) {
        // L1: Check local cache
        UserData local = localCache.getIfPresent(userId);
        if (local != null) {
            return CompletableFuture.completedFuture(local);
        }

        // L2: Check Locus
        return locusClient.get("user:" + userId, UserData.class)
            .thenCompose(cached -> {
                if (cached.isPresent()) {
                    localCache.put(userId, cached.get());
                    return CompletableFuture.completedFuture(cached.get());
                }

                // L3: Fetch from database
                return database.get(userId)
                    .thenApply(data -> {
                        // Populate both caches
                        localCache.put(userId, data);
                        locusClient.set("user:" + userId, data, Duration.ofHours(1));
                        return data;
                    });
            });
    }
}
```

## TTL Strategy

### Layered TTL

```java
private static final Duration LOCAL_TTL = Duration.ofMinutes(5);
private static final Duration LOCUS_TTL = Duration.ofHours(1);

public void cache(String key, UserData data) {
    // Shorter TTL for local (fresher data)
    localCache.put(key, data);

    // Longer TTL for Locus (reduce DB load)
    locusClient.set("user:" + key, data, LOCUS_TTL);
}
```

### Why Different TTLs?

| Layer | TTL | Reason |
|-------|-----|--------|
| Caffeine | 5 min | Fresh data, limited memory |
| Locus | 1 hour | Reduce DB load, shared across instances |

## Invalidation Patterns

### Write-Through Invalidation

**Use when**: Data changes should immediately invalidate cache

```java
public CompletableFuture<Void> updateUser(String userId, UserData data) {
    return database.put(data)
        .thenCompose(v -> {
            // Invalidate both layers
            localCache.invalidate(userId);
            return locusClient.delete("user:" + userId);
        });
}
```

### Event-Driven Invalidation

**Use when**: Distributed invalidation across service instances

```java
@Subscribe
public void onUserUpdated(UserUpdatedEvent event) {
    String userId = event.getUserId();

    // Invalidate local cache
    localCache.invalidate(userId);

    // Locus invalidation handled by publishing service
}
```

### Background Refresh

**Use when**: Keeping cache warm without blocking requests

```java
public void refreshInBackground(String userId) {
    CompletableFuture.runAsync(() -> {
        try {
            UserData fresh = database.get(userId).join();
            localCache.put(userId, fresh);
            locusClient.set("user:" + userId, fresh, LOCUS_TTL).join();
        } catch (Exception e) {
            log.warn("Background refresh failed for {}", userId, e);
        }
    });
}
```

## Size Configuration

### Caffeine Size Limits

```hocon
caffeine {
  # Hot data cache - small, fast
  hot-cache {
    maximumSize: 1000
    expireAfterWrite: 1m
  }

  # Warm data cache - larger, longer TTL
  warm-cache {
    maximumSize: 50000
    expireAfterWrite: 15m
  }
}
```

### Memory Estimation

| Object Size | Caffeine Size | Memory |
|-------------|---------------|--------|
| 1 KB | 10,000 | ~10 MB |
| 1 KB | 100,000 | ~100 MB |
| 10 KB | 10,000 | ~100 MB |

## Monitoring

### Key Metrics

```java
// Expose cache statistics
@Scheduled(fixedRate = 60_000)
public void recordMetrics() {
    CacheStats stats = localCache.stats();

    metrics.gauge("cache.hit_rate", stats.hitRate());
    metrics.gauge("cache.size", localCache.estimatedSize());
    metrics.counter("cache.evictions", stats.evictionCount());
}
```

### Dashboard Queries

```promql
# L1 hit rate
rate(caffeine_hits_total[5m]) /
(rate(caffeine_hits_total[5m]) + rate(caffeine_misses_total[5m]))

# L2 hit rate (Locus)
rate(locus_hits_total[5m]) /
(rate(locus_hits_total[5m]) + rate(locus_misses_total[5m]))

# Overall hit rate
1 - (rate(database_requests_total[5m]) / rate(cache_requests_total[5m]))
```

## Anti-Patterns

### Avoid: Inconsistent TTLs

Before (avoid):
```java
// Local TTL longer than remote - stale data!
caffeine.expireAfterWrite: 1h
locus.ttl: 5m
```

After:
```java
// Local TTL always shorter
caffeine.expireAfterWrite: 5m
locus.ttl: 1h
```

### Avoid: No Local Cache for Hot Data

Before (avoid):
```java
// Always hits Locus for every request
return locusClient.get(key).thenApply(...);
```

After:
```java
// Check local first
UserData local = localCache.getIfPresent(key);
if (local != null) return CompletableFuture.completedFuture(local);
return locusClient.get(key)...
```

### Avoid: Large Objects in Caffeine

Before (avoid):
```java
// 10MB objects in local cache
caffeine.maximumSize: 1000  // = 10GB heap!
```

After:
```java
// Cache lightweight representations locally
caffeine.maximumSize: 1000  // Small metadata only
// Full objects only in Locus
```
