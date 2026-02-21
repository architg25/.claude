---
name: java-ml-serving-patterns
description: Java patterns for calling Salem (model serving) and Fonzie (feature fetching) from Java backend services at Spotify. Covers gRPC client setup, BatchFeatureReader, combined inference flows, and Dagger integration. Use when building Java services that need ML inference.
allowed-tools:
  - Read
---

# Java ML Serving Patterns

Patterns for Java backend services to call Salem for model inference and Fonzie for feature fetching.

## Pattern Categories

- **[Salem Client](salem-client.md)**: gRPC client setup, request building, response handling
- **[Fonzie Features](fonzie-features.md)**: BatchFeatureReader, InitializingFeature, EntityIdSet
- **[Combined Inference](combined-inference.md)**: End-to-end Fonzie → Salem flow
- **[Dependency Injection](dependency-injection.md)**: Dagger module patterns
- **[Testing](testing.md)**: Unit testing ML clients

## Quick Reference

### Maven Dependencies

```xml
<!-- Salem gRPC stubs -->
<dependency>
    <groupId>com.spotify.salem</groupId>
    <artifactId>salem-schemas</artifactId>
</dependency>

<!-- Fonzie feature reader -->
<dependency>
    <groupId>com.spotify.ml</groupId>
    <artifactId>fonzie</artifactId>
    <version>1.6.797</version>  <!-- Use latest, minimum 1.4.0 -->
</dependency>
```

### Salem Client Quick Start

```java
// Create channel with NLS service discovery
ManagedChannel channel = grpcChannelFactory
    .forTarget("nls://salem-api-my-problem-id")
    .usePlaintext()
    .build();

// Create Salem client
Salem.Client salemClient = Salem.client(channel);

// Build classification request
ClassifyRequest request = ClassifyRequest.newBuilder()
    .setClient(Client.newBuilder().setId("my-service"))
    .setProblem(Problem.newBuilder()
        .setId("my-problem-id")
        .setSlotName("production"))
    .setContext(RequestContext.newBuilder()
        .setSpotifyUid(userId))
    .setFeatures(featureSet)
    .build();

// Make async request
CompletionStage<ClassifyResponse> response = salemClient.classify(context, request);
```

### Fonzie Feature Fetch Quick Start

```java
// Define features to fetch
List<InitializingFeature> features = List.of(
    InitializingFeature.of("/user/engagement/streams_30d", "recentStreams"),
    InitializingFeature.of("/artist/popularity/normalized", "artistPopularity")
);

// Build reader
BatchFeatureReader reader = BatchFeatureReaderBuilder.newBuilder()
    .executor(executorService)
    .environment(sourceEnvironment)
    .initializingFeatures(features)
    .build();

// Fetch features for entity
EntityIdSet entityIdSet = EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_GID, userId);
CompletionStage<FeatureSet> featureSet = reader
    .readBatch(context, List.of(entityIdSet))
    .itemFeatures()
    .thenApply(sets -> sets.get(0));
```

### Combined Fonzie → Salem Flow

```java
public CompletionStage<MLResponse> classify(Context context, String userId) {
    // Step 1: Fetch features
    return fonzieClient.getFeatureSet(context, userId)
        // Step 2: Call Salem with features
        .thenCompose(featureSet -> {
            ClassifyRequest request = ClassifyRequest.newBuilder()
                .setProblem(Problem.newBuilder()
                    .setId(PROBLEM_ID)
                    .setSlotName(slotName))
                .setClient(Client.newBuilder().setId(SERVICE_NAME))
                .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
                .setFeatures(featureSet)
                .build();
            return salemClient.classify(context, request);
        })
        // Step 3: Parse response
        .thenApply(this::parseResponse);
}
```

## Key Classes Reference

### Salem (com.spotify.salem.api.v1)

| Class | Purpose |
|-------|---------|
| `Salem.client(ManagedChannel)` | Factory to create Salem client |
| `ClassifyRequest` / `ClassifyResponse` | Classification tasks |
| `RankRequest` / `RankResponse` | Ranking tasks |
| `BatchClassifyRequest` | Batch classification |
| `FeatureSet` | Feature container for requests |
| `Problem` | Problem ID and slot specification |

### Fonzie (com.spotify.fonzie)

| Class | Purpose |
|-------|---------|
| `BatchFeatureReaderBuilder` | Builder for feature readers |
| `BatchFeatureReader` | Reads features for multiple entities |
| `InitializingFeature` | Specifies which features to fetch |
| `EntityIdSet` | Entity identification |
| `SpotifyEntityId` | Entity with type and identifier |

### Entity Types (com.spotify.ml.feature.v3.PrimitiveEntity)

| Enum Value | Use Case |
|------------|----------|
| `PRIMITIVE_ENTITY_USER` | User features |
| `PRIMITIVE_ENTITY_ARTIST` | Artist features |
| `PRIMITIVE_ENTITY_TRACK` | Track features |
| `PRIMITIVE_ENTITY_AD_FLIGHT_LINK` | Ad features |

## Critical Constraints

- **Always** use NLS service discovery: `nls://salem-api-<problem-id>`
- **Always** use `usePlaintext()` for internal gRPC channels
- **Never** block on CompletionStage in request path - use thenCompose/thenApply
- **Always** handle Fonzie failures gracefully with fallback behavior
- **Always** register channels for cleanup on service shutdown

## Production Examples

| Repository | Pattern |
|------------|---------|
| `ads/adranker` | Salem + Fonzie batch inference |
| `Illuminati-Squad/pns-capper` | Single-user Salem + Fonzie flow |
| `AdSafetyML/ad-categorization-service` | Salem classification |

## Related Skills

- [hendrix-serving-salem](../hendrix-serving-salem/SKILL.md) - Python deployment (deploy models)
- [hendrix-features-jukebox](../hendrix-features-jukebox/SKILL.md) - Python feature specs (training)

## Documentation Links

- [Salem Documentation](https://backstage.spotify.net/docs/default/component/salem/)
- [Fonzie Tutorial](https://backstage.spotify.net/docs/default/system/hendrix/tutorials/features/fonzie-feature-fetching/)
- [How to Call Salem Models](https://backstage.spotify.net/docs/default/component/salem/how-tos/call_model/)

## Support Channels

- #hendrix-serving-salem - Salem support
- #hendrix-features-jukebox - Fonzie/Jukebox support
