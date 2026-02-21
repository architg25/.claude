# Salem Client

Patterns for calling Salem from Java services.

## Client Setup

### Using Apollo's GrpcChannelFactory

```java
import com.spotify.apollo.grpc.client.GrpcChannelFactory;
import io.grpc.ManagedChannel;
import com.spotify.salem.api.v1.Salem;

@Provides
@Singleton
Salem.Client provideSalemClient(GrpcChannelFactory grpcChannelFactory) {
    ManagedChannel channel = grpcChannelFactory
        .forTarget("nls://salem-api-" + PROBLEM_ID)
        .usePlaintext()  // Required for internal traffic
        .build();

    return Salem.client(channel);
}
```

### Direct Channel Creation

```java
import io.grpc.ManagedChannelBuilder;

ManagedChannel channel = ManagedChannelBuilder
    .forTarget("salem-api.example.com:443")
    .build();

Salem.Client salemClient = Salem.client(channel);
```

## Request Building

### Classification Request

```java
import com.spotify.salem.api.v1.*;

ClassifyRequest request = ClassifyRequest.newBuilder()
    .setClient(Client.newBuilder()
        .setId("my-service"))
    .setProblem(Problem.newBuilder()
        .setId("my-problem-id")
        .setSlotName("production"))
    .setContext(RequestContext.newBuilder()
        .setSpotifyUid(userId))
    .setFeatures(featureSet)
    .build();
```

### Ranking Request

```java
List<Item> items = itemFeatures.entrySet().stream()
    .map(entry -> Item.newBuilder()
        .setId(entry.getKey())
        .setFeatures(entry.getValue())
        .build())
    .collect(Collectors.toList());

RankRequest request = RankRequest.newBuilder()
    .setClient(Client.newBuilder().setId("my-service"))
    .setProblem(Problem.newBuilder()
        .setId(problemId)
        .setSlotName(slotName))
    .setContext(RequestContext.newBuilder()
        .setSpotifyUid(userId))
    .setSharedFeatures(sharedFeatures)  // Features common to all items
    .addAllItems(items)
    .build();
```

### Batch Classification

```java
List<ClassifyRequest> requests = users.stream()
    .map(user -> ClassifyRequest.newBuilder()
        .setProblem(problem)
        .setClient(client)
        .setContext(RequestContext.newBuilder().setSpotifyUid(user.getId()))
        .setFeatures(user.getFeatures())
        .build())
    .collect(Collectors.toList());

BatchClassifyRequest batchRequest = BatchClassifyRequest.newBuilder()
    .addAllRequests(requests)
    .build();
```

## Making Requests

### Async Classification

```java
public CompletionStage<ClassifyResponse> classify(Context context, String userId, FeatureSet features) {
    ClassifyRequest request = ClassifyRequest.newBuilder()
        .setClient(client)
        .setProblem(problem)
        .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
        .setFeatures(features)
        .build();

    return salemClient.classify(context, request);
}
```

### Async Ranking

```java
public CompletionStage<RankResponse> rank(Context context, String userId, List<Item> items) {
    RankRequest request = RankRequest.newBuilder()
        .setClient(client)
        .setProblem(problem)
        .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
        .addAllItems(items)
        .build();

    return salemClient.rank(context, request);
}
```

## Response Handling

### Classification Response

```java
public MyResult parseClassifyResponse(ClassifyResponse response) {
    // Get prediction class
    int predictedClass = response.getPrediction().getClassIndex();

    // Get probability
    float probability = response.getPrediction().getProbability();

    // Get all class probabilities
    List<Float> classProbabilities = response.getPrediction().getClassProbabilitiesList();

    return new MyResult(predictedClass, probability);
}
```

### Ranking Response

```java
public List<ScoredItem> parseRankResponse(RankResponse response) {
    return response.getItemsList().stream()
        .map(item -> new ScoredItem(
            item.getId(),
            item.getScore()
        ))
        .sorted(Comparator.comparing(ScoredItem::getScore).reversed())
        .collect(Collectors.toList());
}
```

## Error Handling

### With Timeout

```java
public CompletionStage<ClassifyResponse> classifyWithTimeout(Context context, ClassifyRequest request) {
    return salemClient.classify(context, request)
        .toCompletableFuture()
        .orTimeout(100, TimeUnit.MILLISECONDS)
        .exceptionally(ex -> {
            if (ex instanceof TimeoutException) {
                log.warn("Salem request timed out");
                return getDefaultResponse();
            }
            throw new RuntimeException(ex);
        });
}
```

### With Fallback

```java
public CompletionStage<MyResult> classifyWithFallback(Context context, String userId) {
    return classify(context, userId)
        .handle((response, error) -> {
            if (error != null) {
                log.error("Salem call failed, using fallback", error);
                return getFallbackResult();
            }
            return parseResponse(response);
        });
}
```

## Building FeatureSet

### From Map

```java
public FeatureSet buildFeatureSet(Map<String, Float> continuousFeatures, Map<String, String> categoricalFeatures) {
    FeatureSet.Builder builder = FeatureSet.newBuilder();

    continuousFeatures.forEach(builder::putContinuous);
    categoricalFeatures.forEach(builder::putCategorical);

    return builder.build();
}
```

### From Fonzie FeatureSet

Fonzie returns a `FeatureSet` compatible with Salem:

```java
public CompletionStage<ClassifyResponse> classifyWithFonzie(Context context, String userId) {
    return fonzieClient.getFeatureSet(context, userId)
        .thenCompose(featureSet -> {
            ClassifyRequest request = ClassifyRequest.newBuilder()
                .setProblem(problem)
                .setClient(client)
                .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
                .setFeatures(featureSet)  // Direct from Fonzie
                .build();
            return salemClient.classify(context, request);
        });
}
```

## Channel Lifecycle

### Registering for Cleanup

```java
@Provides
@Singleton
Salem.Client provideSalemClient(GrpcChannelFactory factory, SourceEnvironment environment) {
    ManagedChannel channel = factory
        .forTarget("nls://salem-api-" + PROBLEM_ID)
        .usePlaintext()
        .build();

    // Register channel for cleanup on shutdown
    environment.closer().register(channel::shutdown);

    return Salem.client(channel);
}
```

## Related Patterns

- [Fonzie Features](fonzie-features.md) - Feature fetching
- [Combined Inference](combined-inference.md) - Full Fonzie + Salem flow
- [Dependency Injection](dependency-injection.md) - Dagger modules
