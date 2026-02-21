# Fonzie Features

Patterns for fetching features from Jukebox using Fonzie in Java.

## Feature Reader Setup

### Basic Setup

```java
import com.spotify.fonzie.BatchFeatureReader;
import com.spotify.fonzie.BatchFeatureReaderBuilder;
import com.spotify.fonzie.InitializingFeature;

List<InitializingFeature> features = List.of(
    InitializingFeature.of("/user/engagement/streams_30d", "recentStreams"),
    InitializingFeature.of("/user/subscription/days_since_registration", "daysRegistered"),
    InitializingFeature.of("/user/demographics/country", "country")
);

BatchFeatureReader reader = BatchFeatureReaderBuilder.newBuilder()
    .executor(executorService)
    .environment(sourceEnvironment)
    .initializingFeatures(features)
    .build();
```

### With Partition Strategy

```java
import com.spotify.ml.jukebox.online.store.PartitionSelectionStrategy;

BatchFeatureReader reader = BatchFeatureReaderBuilder.newBuilder()
    .executor(executorService)
    .environment(sourceEnvironment)
    .initializingFeatures(features)
    .partitionSelectionStrategy(
        PartitionSelectionStrategy.PARTITION_SELECTION_STRATEGY_ALWAYS_LATEST)
    .build();
```

## Entity ID Patterns

### Single Entity

```java
import com.spotify.ml.jukebox.online.store.entity.EntityIdSet;
import static com.spotify.ml.feature.v3.PrimitiveEntity.PRIMITIVE_ENTITY_USER;
import static com.spotify.ml.feature.v3.Identifier.IDENTIFIER_GID;

EntityIdSet entityIdSet = EntityIdSet.of(
    PRIMITIVE_ENTITY_USER,
    IDENTIFIER_GID,
    userId
);
```

### Multiple Entity Types

```java
// User entity
EntityIdSet userEntity = EntityIdSet.of(
    PRIMITIVE_ENTITY_USER,
    IDENTIFIER_GID,
    userId
);

// Artist entity
EntityIdSet artistEntity = EntityIdSet.of(
    PRIMITIVE_ENTITY_ARTIST,
    IDENTIFIER_GID,
    artistId
);

// Track entity
EntityIdSet trackEntity = EntityIdSet.of(
    PRIMITIVE_ENTITY_TRACK,
    IDENTIFIER_GID,
    trackId
);
```

### Using SpotifyEntityId

```java
import com.spotify.ml.jukebox.online.store.entity.SpotifyEntityId;
import com.spotify.ml.feature.v3.Identifier;
import com.spotify.ml.feature.v3.PrimitiveEntity;

SpotifyEntityId entityId = SpotifyEntityId.of(
    PrimitiveEntity.PRIMITIVE_ENTITY_AD_FLIGHT_LINK,
    Identifier.IDENTIFIER_UUID,
    adFlightLinkId
);

EntityIdSet entityIdSet = EntityIdSet.of(entityId);
```

## Fetching Features

### Single Entity Fetch

```java
public CompletionStage<FeatureSet> getFeatureSet(Context context, String userId) {
    EntityIdSet entityIdSet = EntityIdSet.of(
        PRIMITIVE_ENTITY_USER,
        IDENTIFIER_GID,
        userId
    );

    return batchFeatureReader
        .readBatch(context, List.of(entityIdSet))
        .itemFeatures()
        .thenApply(featureSets -> featureSets.get(0));
}
```

### Batch Entity Fetch

```java
public CompletionStage<List<FeatureSet>> getFeatureSets(Context context, List<String> userIds) {
    List<EntityIdSet> entityIdSets = userIds.stream()
        .map(id -> EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_GID, id))
        .collect(Collectors.toList());

    return batchFeatureReader
        .readBatch(context, entityIdSets)
        .itemFeatures();
}
```

### Shared Features (Context Features)

```java
public CompletionStage<FeatureSet> getSharedFeatures(Context context) {
    // Shared features don't require entity IDs
    return batchFeatureReader
        .readBatch(context, List.of())
        .sharedFeatures();
}
```

## Accessing Feature Values

### Continuous Features

```java
public void processFeatures(FeatureSet featureSet) {
    Map<String, Float> continuous = featureSet.getContinuousMap();

    Float streams = continuous.get("recentStreams");
    Float daysRegistered = continuous.get("daysRegistered");
}
```

### Categorical Features

```java
public void processCategorical(FeatureSet featureSet) {
    Map<String, String> categorical = featureSet.getCategoricalMap();

    String country = categorical.get("country");
    String subscriptionType = categorical.get("subscriptionType");
}
```

### Binary Features

```java
public void processBinary(FeatureSet featureSet) {
    Map<String, ByteString> binary = featureSet.getBinaryMap();

    ByteString embedding = binary.get("userEmbedding");
    float[] embeddingVector = parseEmbedding(embedding);
}
```

## Error Handling

### With Fallback

```java
public CompletionStage<FeatureSet> getFeatureSetWithFallback(Context context, String userId) {
    return getFeatureSet(context, userId)
        .handle((featureSet, error) -> {
            if (error != null) {
                log.warn("Fonzie fetch failed for user {}", userId, error);
                return getDefaultFeatureSet();
            }
            return featureSet;
        });
}
```

### With Partial Results

```java
public CompletionStage<Map<String, FeatureSet>> getFeatureSetsPartial(
        Context context, List<String> userIds) {

    List<CompletableFuture<Pair<String, FeatureSet>>> futures = userIds.stream()
        .map(userId -> getFeatureSet(context, userId)
            .toCompletableFuture()
            .handle((fs, err) -> {
                if (err != null) {
                    return null;  // Skip failed fetches
                }
                return Pair.of(userId, fs);
            }))
        .collect(Collectors.toList());

    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
        .thenApply(v -> futures.stream()
            .map(CompletableFuture::join)
            .filter(Objects::nonNull)
            .collect(Collectors.toMap(Pair::getKey, Pair::getValue)));
}
```

## Feature Specification

### Defining Features

```java
public List<InitializingFeature> getUserFeatures() {
    return List.of(
        // Continuous features
        InitializingFeature.of("/user/engagement/streams_30d", "streams30d"),
        InitializingFeature.of("/user/engagement/sessions_7d", "sessions7d"),

        // Categorical features
        InitializingFeature.of("/user/subscription/type", "subscriptionType"),
        InitializingFeature.of("/user/demographics/country", "country"),

        // Binary features (embeddings)
        InitializingFeature.of("/user/embedding/v1", "userEmbedding")
    );
}

public List<InitializingFeature> getItemFeatures() {
    return List.of(
        InitializingFeature.of("/track/audio/danceability", "danceability"),
        InitializingFeature.of("/track/popularity/score", "popularity")
    );
}
```

## Dagger Integration

```java
@Module
public class FonzieModule {

    @Provides
    @Singleton
    BatchFeatureReader provideBatchFeatureReader(
            ExecutorService executor,
            SourceEnvironment environment) {

        return BatchFeatureReaderBuilder.newBuilder()
            .executor(executor)
            .environment(environment)
            .initializingFeatures(getFeatures())
            .partitionSelectionStrategy(
                PartitionSelectionStrategy.PARTITION_SELECTION_STRATEGY_ALWAYS_LATEST)
            .build();
    }

    private List<InitializingFeature> getFeatures() {
        return List.of(
            InitializingFeature.of("/user/engagement/streams_30d", "streams30d"),
            InitializingFeature.of("/user/subscription/type", "subscriptionType")
        );
    }
}
```

## Related Patterns

- [Salem Client](salem-client.md) - Calling Salem with features
- [Combined Inference](combined-inference.md) - Full Fonzie + Salem flow
- [Dependency Injection](dependency-injection.md) - Dagger modules
