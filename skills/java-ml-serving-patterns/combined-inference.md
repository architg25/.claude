# Combined Inference

Patterns for end-to-end Fonzie feature fetching + Salem inference.

## Basic Combined Flow

```java
public class MLInferenceService {
    private final BatchFeatureReader featureReader;
    private final Salem.Client salemClient;
    private final Problem problem;
    private final Client clientId;

    public CompletionStage<MLResult> classify(Context context, String userId) {
        // Step 1: Fetch features from Fonzie
        return getFeatureSet(context, userId)
            // Step 2: Build and send Salem request
            .thenCompose(featureSet -> callSalem(context, userId, featureSet))
            // Step 3: Parse response
            .thenApply(this::parseResponse);
    }

    private CompletionStage<FeatureSet> getFeatureSet(Context context, String userId) {
        EntityIdSet entity = EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_GID, userId);
        return featureReader
            .readBatch(context, List.of(entity))
            .itemFeatures()
            .thenApply(sets -> sets.get(0));
    }

    private CompletionStage<ClassifyResponse> callSalem(
            Context context, String userId, FeatureSet features) {
        ClassifyRequest request = ClassifyRequest.newBuilder()
            .setProblem(problem)
            .setClient(clientId)
            .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
            .setFeatures(features)
            .build();

        return salemClient.classify(context, request);
    }

    private MLResult parseResponse(ClassifyResponse response) {
        return new MLResult(
            response.getPrediction().getClassIndex(),
            response.getPrediction().getProbability()
        );
    }
}
```

## Ranking with Item Features

```java
public class RankingService {
    private final BatchFeatureReader userFeatureReader;
    private final BatchFeatureReader itemFeatureReader;
    private final Salem.Client salemClient;

    public CompletionStage<List<ScoredItem>> rank(
            Context context, String userId, List<String> itemIds) {

        // Fetch user and item features in parallel
        CompletionStage<FeatureSet> userFeatures = getUserFeatures(context, userId);
        CompletionStage<Map<String, FeatureSet>> itemFeatures = getItemFeatures(context, itemIds);

        // Combine and call Salem
        return userFeatures.thenCombine(itemFeatures, (userFs, itemFsMap) ->
            buildRankRequest(userId, userFs, itemFsMap)
        ).thenCompose(request -> salemClient.rank(context, request))
         .thenApply(this::parseRankResponse);
    }

    private RankRequest buildRankRequest(
            String userId, FeatureSet userFeatures, Map<String, FeatureSet> itemFeatures) {

        List<Item> items = itemFeatures.entrySet().stream()
            .map(entry -> Item.newBuilder()
                .setId(entry.getKey())
                .setFeatures(entry.getValue())
                .build())
            .collect(Collectors.toList());

        return RankRequest.newBuilder()
            .setProblem(problem)
            .setClient(clientId)
            .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
            .setSharedFeatures(userFeatures)  // User features shared across items
            .addAllItems(items)
            .build();
    }
}
```

## Batch Inference

```java
public class BatchInferenceService {

    public CompletionStage<Map<String, MLResult>> batchClassify(
            Context context, List<String> userIds) {

        // Fetch all features in batch
        return getFeatureSets(context, userIds)
            .thenCompose(featureSetsMap -> {
                // Build batch request
                List<ClassifyRequest> requests = userIds.stream()
                    .filter(featureSetsMap::containsKey)
                    .map(userId -> buildRequest(userId, featureSetsMap.get(userId)))
                    .collect(Collectors.toList());

                BatchClassifyRequest batchRequest = BatchClassifyRequest.newBuilder()
                    .addAllRequests(requests)
                    .build();

                return salemClient.batchClassify(context, batchRequest);
            })
            .thenApply(this::parseBatchResponse);
    }

    private CompletionStage<Map<String, FeatureSet>> getFeatureSets(
            Context context, List<String> userIds) {

        List<EntityIdSet> entities = userIds.stream()
            .map(id -> EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_GID, id))
            .collect(Collectors.toList());

        return featureReader.readBatch(context, entities)
            .itemFeatures()
            .thenApply(featureSets -> {
                Map<String, FeatureSet> result = new HashMap<>();
                for (int i = 0; i < userIds.size(); i++) {
                    result.put(userIds.get(i), featureSets.get(i));
                }
                return result;
            });
    }
}
```

## With Error Handling

```java
public class ResilientInferenceService {
    private final MLInferenceService mlService;
    private final Fallback fallback;

    public CompletionStage<MLResult> classifyWithFallback(Context context, String userId) {
        return mlService.classify(context, userId)
            .handle((result, error) -> {
                if (error != null) {
                    logError(error, userId);
                    return fallback.getDefaultResult(userId);
                }
                return result;
            });
    }

    public CompletionStage<MLResult> classifyWithTimeout(Context context, String userId) {
        return mlService.classify(context, userId)
            .toCompletableFuture()
            .orTimeout(100, TimeUnit.MILLISECONDS)
            .exceptionally(ex -> {
                if (ex instanceof TimeoutException) {
                    metrics.incrementTimeout();
                    return fallback.getDefaultResult(userId);
                }
                throw new RuntimeException(ex);
            });
    }
}
```

## With Caching

```java
public class CachedInferenceService {
    private final Cache<String, MLResult> cache;
    private final MLInferenceService mlService;

    public CompletionStage<MLResult> classify(Context context, String userId) {
        // Check cache first
        MLResult cached = cache.getIfPresent(userId);
        if (cached != null) {
            return CompletableFuture.completedFuture(cached);
        }

        // Call service and cache result
        return mlService.classify(context, userId)
            .thenApply(result -> {
                cache.put(userId, result);
                return result;
            });
    }
}
```

## Complete Service Example

```java
@Singleton
public class UserClassificationService {
    private static final String PROBLEM_ID = "user-classification";
    private static final String SERVICE_NAME = "my-service";

    private final BatchFeatureReader featureReader;
    private final Salem.Client salemClient;
    private final Problem problem;
    private final Client clientId;
    private final String slotName;

    @Inject
    public UserClassificationService(
            BatchFeatureReader featureReader,
            Salem.Client salemClient,
            @Named("salemSlot") String slotName) {
        this.featureReader = featureReader;
        this.salemClient = salemClient;
        this.slotName = slotName;

        this.problem = Problem.newBuilder()
            .setId(PROBLEM_ID)
            .setSlotName(slotName)
            .build();

        this.clientId = Client.newBuilder()
            .setId(SERVICE_NAME)
            .build();
    }

    public CompletionStage<UserClassification> classifyUser(Context context, String userId) {
        return fetchUserFeatures(context, userId)
            .thenCompose(features -> sendClassifyRequest(context, userId, features))
            .thenApply(this::parseClassification)
            .exceptionally(error -> {
                log.error("Classification failed for user {}", userId, error);
                return UserClassification.unknown();
            });
    }

    private CompletionStage<FeatureSet> fetchUserFeatures(Context context, String userId) {
        EntityIdSet entity = EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_GID, userId);

        return featureReader.readBatch(context, List.of(entity))
            .itemFeatures()
            .thenApply(featureSets -> {
                if (featureSets.isEmpty()) {
                    throw new RuntimeException("No features found for user: " + userId);
                }
                return featureSets.get(0);
            });
    }

    private CompletionStage<ClassifyResponse> sendClassifyRequest(
            Context context, String userId, FeatureSet features) {

        ClassifyRequest request = ClassifyRequest.newBuilder()
            .setProblem(problem)
            .setClient(clientId)
            .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
            .setFeatures(features)
            .build();

        return salemClient.classify(context, request);
    }

    private UserClassification parseClassification(ClassifyResponse response) {
        Prediction prediction = response.getPrediction();
        return new UserClassification(
            ClassificationType.fromIndex(prediction.getClassIndex()),
            prediction.getProbability()
        );
    }
}
```

## Related Patterns

- [Salem Client](salem-client.md) - Salem client setup
- [Fonzie Features](fonzie-features.md) - Feature fetching
- [Testing](testing.md) - Testing combined flows
