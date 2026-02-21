# Apollo Integration

Patterns for integrating Decibel with Apollo services.

## Module Setup

**Use when**: Adding Decibel to an Apollo service

```java
import com.spotify.decibel.apollo.DecibelModule;

public class MyServiceModule extends AbstractModule {
    @Override
    protected void configure() {
        install(DecibelModule.create(MyDatabase.Connection.class));
    }
}
```

**Key concepts:**
- `DecibelModule` handles connection lifecycle
- Generated `Connection` class provides typed access
- One module per Decibel database

## Repository Pattern

**Use when**: Encapsulating database operations

```java
package com.spotify.myteam.repository;

import com.spotify.decibel.Connection;
import com.spotify.decibel.Table;
import com.spotify.decibel.Key;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

public class UserDataRepository {
    private final Table<UserDataRow> table;

    public UserDataRepository(Connection connection) {
        this.table = connection.table(UserDataRow.class);
    }

    public CompletableFuture<Optional<UserDataRow>> get(String userId) {
        return table.get(Key.of(userId));
    }

    public CompletableFuture<Void> put(UserDataRow row) {
        return table.put(row);
    }

    public CompletableFuture<Void> delete(String userId) {
        return table.delete(Key.of(userId));
    }
}
```

**Benefits:**
- Type-safe operations
- Async-first API
- Encapsulated data access logic

## Async Operations

### Sequential Reads

**Use when**: Dependent operations

```java
public CompletableFuture<UserProfile> getFullProfile(String userId) {
    return userDataTable.get(Key.of(userId))
        .thenCompose(userData -> {
            if (userData.isEmpty()) {
                return CompletableFuture.completedFuture(null);
            }
            return preferencesTable.get(Key.of(userId))
                .thenApply(prefs -> buildProfile(userData.get(), prefs));
        });
}
```

### Parallel Reads

**Use when**: Independent operations

```java
public CompletableFuture<Dashboard> getDashboard(String userId) {
    CompletableFuture<Optional<UserData>> userFuture =
        userTable.get(Key.of(userId));
    CompletableFuture<Optional<Settings>> settingsFuture =
        settingsTable.get(Key.of(userId));

    return userFuture.thenCombine(settingsFuture,
        (user, settings) -> buildDashboard(user, settings));
}
```

### Batch Reads

**Use when**: Reading multiple keys

```java
public CompletableFuture<List<UserDataRow>> getMultiple(List<String> userIds) {
    List<Key> keys = userIds.stream()
        .map(Key::of)
        .collect(Collectors.toList());

    return table.getAll(keys);
}
```

## Scan Operations

### Range Scan

**Use when**: Querying within a partition

```java
public CompletableFuture<List<EventRow>> getRecentEvents(
    String userId,
    Instant since,
    int limit) {

    return table.scan()
        .partitionKey(userId)
        .sortKeyRange(Range.from(since))
        .limit(limit)
        .execute();
}
```

### Full Partition Scan

**Use when**: Reading all rows in a partition

```java
public CompletableFuture<List<SettingsRow>> getAllSettings(String userId) {
    return table.scan()
        .partitionKey(userId)
        .execute();
}
```

## Error Handling

### Retry Pattern

**Use when**: Transient errors need retry

```java
public CompletableFuture<Optional<UserData>> getWithRetry(String userId) {
    return RetryPolicy.builder()
        .maxAttempts(3)
        .backoff(Duration.ofMillis(100))
        .retryOn(DecibelRetryableException.class)
        .build()
        .executeAsync(() -> table.get(Key.of(userId)));
}
```

### Graceful Degradation

**Use when**: Fallback on failure

```java
public CompletableFuture<UserData> getWithFallback(String userId) {
    return table.get(Key.of(userId))
        .thenApply(opt -> opt.orElse(DEFAULT_USER_DATA))
        .exceptionally(ex -> {
            log.warn("Decibel read failed, using default", ex);
            return DEFAULT_USER_DATA;
        });
}
```

## Configuration

### application.conf

```hocon
decibel {
  my-database {
    bigtable {
      project-id = "my-gcp-project"
      instance-id = "my-bigtable-instance"
    }
    # Connection pool settings
    max-connections = 10
    connection-timeout = 5s
    read-timeout = 10s
  }
}
```

## Anti-Patterns

### Avoid: Blocking on Futures

Before (avoid):
```java
// Blocks the thread!
UserData data = table.get(Key.of(userId)).join();
```

After:
```java
// Return the future, let Apollo handle async
return table.get(Key.of(userId))
    .thenApply(opt -> opt.orElse(null));
```

### Avoid: N+1 Queries

Before (avoid):
```java
for (String userId : userIds) {
    results.add(table.get(Key.of(userId)).join());  // N queries!
}
```

After:
```java
List<Key> keys = userIds.stream().map(Key::of).toList();
return table.getAll(keys);  // Single batch query
```
