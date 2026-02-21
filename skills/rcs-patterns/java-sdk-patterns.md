# Java SDK Patterns

Backend patterns for RCS property publishing and resolution.

## Basic Setup

### Property Publishing
```java
RemoteConfigClient client = RemoteConfigInitializer
    .resolverBuilder(SERVICE_NAME, registry)
    .withResolveTimeout(Duration.ofMillis(1000))
    .publish(List.of(ENABLE_FEATURE, MAX_RETRIES));
```

### Property Resolution
```java
Configuration config = client.resolveProperties(
    ResolutionContext.from(userInfo)
).toCompletableFuture().get();

boolean enabled = config.get(ENABLE_FEATURE);
int maxRetries = config.get(MAX_RETRIES);
```

## Resolution Context

The context determines how policies are evaluated.

### Available Context Fields
| Field | Source | Notes |
|-------|--------|-------|
| `user_id` | UserInfo | Primary targeting |
| `country` | UserInfo | Market targeting |
| `platform` | Request | Android/iOS/Web |
| `app_version` | Request | Version targeting |

### Building Context
```java
ResolutionContext context = ResolutionContext.builder()
    .userId(userId)
    .country(country)
    .platform(platform)
    .build();
```

## Disabling Default Exposure

For custom exposure filtering (see exposure-filtering skill):

```java
RemoteConfigInitializer.resolverBuilder(SERVICE_NAME, registry)
    .withDefaultBackendExposureDisabled()
    .publish(properties);
```

## Error Handling

```java
try {
    Configuration config = client.resolveProperties(context)
        .toCompletableFuture()
        .get(timeout, TimeUnit.MILLISECONDS);
} catch (TimeoutException e) {
    // Use defaults - RCS is unavailable
    log.warn("RCS timeout, using defaults");
}
```

## Testing with Overrides

Use Backstage Remote Config Plugin to test resolution for specific users before launch.
