# Java Client

Patterns for configuring and using the Locus Java client.

## Basic Configuration

**Use when**: Connecting to Locus from an Apollo service

### application.conf

```hocon
memcached {
  locus {
    projectId: "my-gcp-project"
    name: "my-service-locus"
    max-outstanding-requests: 20000
    split-clients: true
  }
}
```

### Apollo Module Setup

```java
import com.spotify.locus.apollo.LocusModule;

public class MyServiceModule extends AbstractModule {
    @Override
    protected void configure() {
        install(LocusModule.create());
    }
}
```

## Client Configuration Options

### Connection Settings

```hocon
memcached {
  locus {
    projectId: "my-gcp-project"
    name: "my-service-locus"

    # Connection pool
    max-outstanding-requests: 20000
    split-clients: true

    # Timeouts
    connect-timeout: 1s
    operation-timeout: 500ms

    # Retry policy
    max-retries: 3
    retry-backoff: 100ms
  }
}
```

### Performance Tuning

```hocon
memcached {
  locus {
    # Increase for high-throughput
    max-outstanding-requests: 50000

    # Reduce for latency-sensitive
    operation-timeout: 200ms

    # Connection management
    max-connections-per-shard: 10
    idle-connection-timeout: 60s
  }
}
```

## Basic Operations

### Get

**Use when**: Fetching a cached value

```java
@Inject
private LocusClient client;

public CompletableFuture<Optional<UserData>> getUser(String userId) {
    return client.get("user:" + userId, UserData.class);
}
```

### Set

**Use when**: Storing a value with TTL

```java
public CompletableFuture<Void> cacheUser(String userId, UserData data) {
    return client.set(
        "user:" + userId,
        data,
        Duration.ofMinutes(30)  // TTL
    );
}
```

### Delete

**Use when**: Removing a cached value

```java
public CompletableFuture<Boolean> invalidateUser(String userId) {
    return client.delete("user:" + userId);
}
```

## Serialization

### JSON Serialization

**Use when**: Caching POJOs

```java
// Automatic JSON serialization with ObjectMapper
UserData data = UserData.builder()
    .userId("user-123")
    .name("Test User")
    .build();

client.set("user:123", data, Duration.ofMinutes(30));
```

### Custom Serialization

**Use when**: Performance-critical or custom formats

```java
public class ProtobufSerializer<T extends Message>
    implements LocusSerializer<T> {

    @Override
    public byte[] serialize(T value) {
        return value.toByteArray();
    }

    @Override
    public T deserialize(byte[] bytes, Class<T> clazz) {
        return clazz.getMethod("parseFrom", byte[].class)
            .invoke(null, bytes);
    }
}
```

## Key Design Patterns

### Namespaced Keys

**Use when**: Avoiding key collisions

```java
private static final String NAMESPACE = "myservice";

private String userKey(String userId) {
    return NAMESPACE + ":user:" + userId;
}

private String sessionKey(String sessionId) {
    return NAMESPACE + ":session:" + sessionId;
}
```

### Versioned Keys

**Use when**: Cache invalidation on schema changes

```java
private static final int CACHE_VERSION = 2;

private String versionedKey(String key) {
    return "v" + CACHE_VERSION + ":" + key;
}
```

## TTL Strategies

### Static TTL

**Use when**: Consistent expiration

```java
client.set(key, value, Duration.ofHours(1));
```

### Dynamic TTL

**Use when**: TTL depends on data

```java
Duration ttl = computeTtl(data);
client.set(key, data, ttl);

private Duration computeTtl(UserData data) {
    if (data.isPremium()) {
        return Duration.ofHours(24);  // Premium users cached longer
    }
    return Duration.ofHours(1);
}
```

### Short TTL for Volatile Data

```java
// Session data - short TTL
client.set("session:" + id, session, Duration.ofMinutes(15));

// Config data - longer TTL
client.set("config:" + key, config, Duration.ofHours(6));
```

## Error Handling

### Graceful Degradation

**Use when**: Cache failures shouldn't break functionality

```java
public CompletableFuture<UserData> getUserWithFallback(String userId) {
    return client.get("user:" + userId, UserData.class)
        .thenCompose(cached -> {
            if (cached.isPresent()) {
                return CompletableFuture.completedFuture(cached.get());
            }
            return fetchFromDatabase(userId);
        })
        .exceptionally(ex -> {
            log.warn("Cache failure, falling back to DB", ex);
            return fetchFromDatabaseSync(userId);
        });
}
```

### Retry Pattern

```java
public CompletableFuture<Optional<UserData>> getWithRetry(String key) {
    return RetryPolicy.builder()
        .maxAttempts(3)
        .backoff(Duration.ofMillis(50))
        .retryOn(LocusTimeoutException.class)
        .build()
        .executeAsync(() -> client.get(key, UserData.class));
}
```

## Batch Operations

### Multi-Get

**Use when**: Fetching multiple keys

```java
public CompletableFuture<Map<String, UserData>> getUsers(List<String> userIds) {
    List<String> keys = userIds.stream()
        .map(id -> "user:" + id)
        .toList();

    return client.getAll(keys, UserData.class);
}
```

### Parallel Sets

**Use when**: Caching multiple values

```java
public CompletableFuture<Void> cacheUsers(Map<String, UserData> users) {
    List<CompletableFuture<Void>> futures = users.entrySet().stream()
        .map(e -> client.set("user:" + e.getKey(), e.getValue(), TTL))
        .toList();

    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
}
```

## Metrics

### Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| Hit rate | < 95% | Review cache keys/TTL |
| Latency p99 | > 10ms | Check network/sizing |
| Connection errors | > 0.1% | Check auth/connectivity |
| Evictions | Increasing | Increase memory |
