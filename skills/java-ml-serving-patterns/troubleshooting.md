# Troubleshooting

Common issues and solutions for Java ML serving patterns.

## Salem Connection Issues

### Connection Refused

**Error**: `UNAVAILABLE: Connection refused`

**Solutions**:

1. **Verify NLS target format**:
   ```java
   // Correct format
   "nls://salem-api-my-problem"

   // Incorrect
   "salem-api-my-problem"  // Missing nls://
   "nls://my-problem"       // Missing salem-api- prefix
   ```

2. **Check problem exists**:
   ```bash
   kubectl get problem my-problem -n salem
   ```

3. **Verify slot is deployed**:
   ```bash
   docker run gcr.io/salem-platform/deployer-cli:latest \
     slot status my-problem production
   ```

### gRPC Deadline Exceeded

**Error**: `DEADLINE_EXCEEDED`

**Solutions**:

1. **Increase timeout**:
   ```java
   .defaultTimeout(Duration.ofMillis(200))  // Increase from 100ms
   ```

2. **Check Salem latency**:
   - View Grafana dashboard for the problem
   - Consider scaling up replicas

3. **Reduce request size** if sending large feature sets

### Missing usePlaintext

**Error**: `SSL handshake failed` or connection issues

**Solution**:
```java
// REQUIRED for internal gRPC
.usePlaintext()
```

## Fonzie Issues

### Feature Not Found

**Error**: `Feature '/user/some/feature' not found`

**Solutions**:

1. **Verify feature path**:
   ```java
   // Check exact path in Jukebox
   InitializingFeature.of("/user/engagement/streams_30d", "streams30d")
   ```

2. **Check feature is loaded online**:
   - Verify LoadOnline workflow ran
   - Check Fonzie scopes match

3. **Verify entity type**:
   ```java
   // Feature path must match entity type
   PRIMITIVE_ENTITY_USER  // for /user/* features
   PRIMITIVE_ENTITY_TRACK // for /track/* features
   ```

### Null Features Returned

**Symptoms**: FeatureSet has null or missing values

**Solutions**:

1. **Check entity ID format**:
   ```java
   // GID vs UUID
   EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_GID, userId)
   EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_UUID, userId)
   ```

2. **Verify partition has data**:
   - Check LoadOnline completed for partition
   - Verify data exists in online store

3. **Handle missing features**:
   ```java
   Float streams = featureSet.getContinuousMap().getOrDefault("streams30d", 0.0f);
   ```

## Async/Future Issues

### Blocking in Request Path

**Symptom**: Slow response times, thread pool exhaustion

**Bad**:
```java
// DON'T block in request handlers
FeatureSet features = featureReader.readBatch(...)
    .itemFeatures()
    .toCompletableFuture()
    .get();  // BLOCKING
```

**Good**:
```java
// Use async composition
return featureReader.readBatch(...)
    .itemFeatures()
    .thenApply(sets -> sets.get(0))
    .thenCompose(features -> callSalem(features));
```

### Unhandled Exceptions

**Symptom**: Silent failures, missing responses

**Solution**:
```java
return classify(context, userId)
    .handle((result, error) -> {
        if (error != null) {
            log.error("Classification failed", error);
            return fallbackResult();
        }
        return result;
    });
```

## Memory Issues

### Feature Reader Memory

**Symptom**: High memory usage

**Solutions**:

1. **Limit feature count**:
   ```java
   // Only initialize needed features
   List<InitializingFeature> features = List.of(
       // Only essential features, not all available
   );
   ```

2. **Use appropriate batch sizes**:
   ```java
   // Don't fetch too many entities at once
   List<EntityIdSet> batch = entityIds.subList(0, Math.min(100, entityIds.size()));
   ```

### Channel Leaks

**Symptom**: Growing number of connections

**Solution**:
```java
// Register channels for cleanup
environment.closer().register(channel::shutdown);
```

## Performance Issues

### High Latency

**Debugging steps**:

1. **Profile each stage**:
   ```java
   long start = System.nanoTime();
   FeatureSet features = getFeatures(...).join();
   log.info("Fonzie: {}ms", (System.nanoTime() - start) / 1_000_000);

   start = System.nanoTime();
   ClassifyResponse response = callSalem(...).join();
   log.info("Salem: {}ms", (System.nanoTime() - start) / 1_000_000);
   ```

2. **Parallelize independent calls**:
   ```java
   CompletionStage<FeatureSet> userFeatures = getUser(...);
   CompletionStage<List<FeatureSet>> itemFeatures = getItems(...);

   // Fetch in parallel
   return userFeatures.thenCombine(itemFeatures, this::combine);
   ```

### Low Throughput

**Solutions**:

1. **Use batch APIs**:
   ```java
   // Batch instead of individual calls
   BatchClassifyRequest batch = ...;
   salemClient.batchClassify(context, batch);
   ```

2. **Increase connection pool**:
   - Configure gRPC channel with more connections

## Serialization Issues

### FeatureSet Mismatch

**Error**: Features don't match model expectations

**Solution**:
```java
// Log features for debugging
log.debug("Features: continuous={}, categorical={}",
    featureSet.getContinuousMap().keySet(),
    featureSet.getCategoricalMap().keySet());
```

### Proto Compatibility

**Error**: Unknown fields or version mismatch

**Solutions**:

1. **Update salem-schemas dependency**:
   ```xml
   <dependency>
       <groupId>com.spotify.salem</groupId>
       <artifactId>salem-schemas</artifactId>
       <version>LATEST</version>
   </dependency>
   ```

2. **Check proto version compatibility**

## Debugging Tools

### Logging Request/Response

```java
public CompletionStage<ClassifyResponse> classifyWithLogging(
        Context context, ClassifyRequest request) {

    log.debug("Salem request: problemId={}, slot={}, features={}",
        request.getProblem().getId(),
        request.getProblem().getSlotName(),
        request.getFeatures().getContinuousCount());

    return salemClient.classify(context, request)
        .thenApply(response -> {
            log.debug("Salem response: class={}, probability={}",
                response.getPrediction().getClassIndex(),
                response.getPrediction().getProbability());
            return response;
        });
}
```

### Health Check

```java
public CompletionStage<Boolean> healthCheck(Context context) {
    ClassifyRequest healthRequest = ClassifyRequest.newBuilder()
        .setProblem(problem)
        .setClient(clientId)
        .setFeatures(FeatureSet.getDefaultInstance())
        .build();

    return salemClient.classify(context, healthRequest)
        .handle((response, error) -> error == null);
}
```

## Getting Help

If issues persist:

1. **Check Slack**:
   - #hendrix-serving-salem for Salem issues
   - #hendrix-features-jukebox for Fonzie issues

2. **Post with details**:
   - Problem ID
   - Error message and stack trace
   - Request example (sanitized)
   - Dependency versions

3. **Documentation**:
   - [Salem Docs](https://backstage.spotify.net/docs/default/component/salem/)
   - [Fonzie Tutorial](https://backstage.spotify.net/docs/default/system/hendrix/tutorials/features/fonzie-feature-fetching/)

## Related Patterns

- [Salem Client](salem-client.md) - Client setup
- [Fonzie Features](fonzie-features.md) - Feature fetching
- [Testing](testing.md) - Test patterns
