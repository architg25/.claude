# Migration Patterns

Patterns for migrating to Locus from other caching solutions.

## From Self-Managed Memcached

### Before (Self-Managed)

```hocon
memcached {
  hosts: ["memcached-1:11211", "memcached-2:11211"]
  connection-pool-size: 10
}
```

### After (Locus)

```hocon
memcached {
  locus {
    projectId: "my-gcp-project"
    name: "my-service-locus"
    max-outstanding-requests: 20000
  }
}
```

### Migration Steps

1. **Deploy Locus resource**
   ```yaml
   apiVersion: caching.spotify.com/v1alpha3
   kind: Locus
   metadata:
     name: my-service-locus
   spec:
     regions: [europe-west1, us-central1]
     numShards: 3
     authEnabled: true
   ```

2. **Update client configuration** (see above)

3. **Dual-write during migration**
   ```java
   // Write to both during transition
   public CompletableFuture<Void> set(String key, Object value) {
       return CompletableFuture.allOf(
           oldClient.set(key, value),
           locusClient.set(key, value, TTL)
       );
   }
   ```

4. **Switch reads to Locus**
5. **Remove old Memcached cluster**

## From Redis

### Key Differences

| Feature | Redis | Locus |
|---------|-------|-------|
| Data structures | Rich (lists, sets, hashes) | Key-value only |
| Persistence | Optional | No (cache only) |
| Pub/Sub | Yes | No |
| Transactions | Yes | No |

### Adapting Patterns

**Redis Hash → Locus JSON**

Before (Redis):
```java
// Store hash
redisTemplate.opsForHash().put("user:123", "name", "Alice");
redisTemplate.opsForHash().put("user:123", "email", "alice@example.com");
```

After (Locus):
```java
// Store as JSON object
UserData data = UserData.builder()
    .name("Alice")
    .email("alice@example.com")
    .build();
locusClient.set("user:123", data, TTL);
```

**Redis List → Application-Level**

Before (Redis):
```java
// Push to list
redisTemplate.opsForList().leftPush("queue", item);
```

After:
```java
// Use Pub/Sub or dedicated queue service
// Locus is not suitable for queues
```

## From In-Memory Only (Caffeine/Guava)

### When to Add Locus

- Cache size exceeds single instance memory
- Need shared cache across service replicas
- Want to survive service restarts

### Migration Pattern

```java
// Before: Local only
private final Cache<String, UserData> cache = Caffeine.newBuilder()
    .maximumSize(10000)
    .expireAfterWrite(Duration.ofMinutes(30))
    .build();

// After: Multilevel
public class MultilevelCache {
    private final Cache<String, UserData> localCache;
    private final LocusClient locusClient;

    public CompletableFuture<Optional<UserData>> get(String key) {
        // Check local first
        UserData local = localCache.getIfPresent(key);
        if (local != null) {
            return CompletableFuture.completedFuture(Optional.of(local));
        }

        // Fall back to Locus
        return locusClient.get(key, UserData.class)
            .thenApply(opt -> {
                opt.ifPresent(data -> localCache.put(key, data));
                return opt;
            });
    }
}
```

## Gradual Migration Strategy

### Phase 1: Shadow Reads

Read from old cache, compare with Locus (no impact on traffic).

```java
public CompletableFuture<UserData> get(String key) {
    // Primary: Old cache
    CompletableFuture<UserData> primary = oldCache.get(key);

    // Shadow: Locus (async, for comparison)
    locusClient.get(key, UserData.class)
        .thenAccept(locus -> {
            UserData old = primary.join();
            if (!Objects.equals(old, locus.orElse(null))) {
                metrics.increment("locus.shadow.mismatch");
            }
        });

    return primary;
}
```

### Phase 2: Dual Write

Write to both caches.

```java
public CompletableFuture<Void> set(String key, UserData data) {
    return CompletableFuture.allOf(
        oldCache.set(key, data),
        locusClient.set(key, data, TTL)
    );
}
```

### Phase 3: Read Migration (Percentage)

Gradually shift reads to Locus.

```java
private final double locusReadPercentage = 0.10; // Start at 10%

public CompletableFuture<UserData> get(String key) {
    if (random.nextDouble() < locusReadPercentage) {
        return locusClient.get(key, UserData.class)
            .thenApply(opt -> opt.orElse(null));
    }
    return oldCache.get(key);
}
```

### Phase 4: Full Migration

Switch all reads to Locus, decommission old cache.

## Rollback Planning

### Keep Old Cache Warm

```java
// Continue writing to old cache during migration
public CompletableFuture<Void> set(String key, UserData data) {
    return locusClient.set(key, data, TTL)
        .thenCompose(v -> oldCache.set(key, data));  // Backup write
}
```

### Feature Flag

```java
@Value("${cache.use-locus:true}")
private boolean useLocus;

public CompletableFuture<UserData> get(String key) {
    if (useLocus) {
        return locusClient.get(key, UserData.class)...;
    }
    return oldCache.get(key);
}
```

## Validation Checklist

- [ ] Locus cluster deployed and healthy
- [ ] Auth configured with correct service accounts
- [ ] Client configuration tested in staging
- [ ] Dual-write verified (no data loss)
- [ ] Read latency comparable or better
- [ ] Hit rate maintained or improved
- [ ] Rollback mechanism tested
- [ ] Monitoring dashboards updated
