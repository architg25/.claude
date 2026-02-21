# ExposerLib Patterns

Backend custom exposure for request-level filtering.

## Overview

ExposerLib allows backend services to control exactly when exposure is logged.

## When to Use

- Request-level exposure decisions
- Complex business logic for exposure
- Feature used in specific code paths only

## Setup

### Step 1: Disable Default Exposure

```java
RemoteConfigInitializer.resolverBuilder(SERVICE_NAME, registry)
    .withDefaultBackendExposureDisabled()
    .publish(properties);
```

### Step 2: Manual Exposure at Feature Use

```java
// Only expose when feature is actually used
if (shouldUseFeature(request)) {
    exposerLib.expose(userId, experimentId);
    return newFeatureImplementation(request);
} else {
    return defaultImplementation(request);
}
```

## Complete Example

```java
public class SearchService {
    private final RemoteConfigClient rcClient;
    private final ExposerLib exposerLib;

    public SearchResult search(SearchRequest request) {
        Configuration config = rcClient.resolveProperties(
            ResolutionContext.from(request.getUserInfo())
        ).get();

        boolean useNewRanking = config.get(USE_NEW_RANKING);

        // Only expose if query meets criteria
        if (useNewRanking && request.getQuery().length() > 3) {
            exposerLib.expose(
                request.getUserId(),
                "search_ranking_experiment"
            );
            return newRankingSearch(request);
        }

        return defaultSearch(request);
    }
}
```

## Key Considerations

| Consideration | Guidance |
|---------------|----------|
| Exposure timing | Expose at point of actual feature use |
| Treatment agnostic | Same logic for control and treatment |
| Idempotent | Multiple exposes for same user OK |
| Logging reliability | Ensure exposure logging doesn't fail silently |

## Testing

```java
@Test
void shouldExposeOnlyForLongQueries() {
    // Short query - no exposure
    service.search(shortQueryRequest);
    verify(exposerLib, never()).expose(any(), any());

    // Long query - exposure logged
    service.search(longQueryRequest);
    verify(exposerLib).expose(userId, experimentId);
}
```
