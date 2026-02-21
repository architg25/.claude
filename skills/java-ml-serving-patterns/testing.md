# Testing

Patterns for testing ML clients in Java.

## Mocking Salem Client

### Using Mockito

```java
import static org.mockito.Mockito.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class MLInferenceServiceTest {

    @Mock
    private Salem.Client salemClient;

    @Mock
    private BatchFeatureReader featureReader;

    @Test
    void testClassify() {
        // Arrange
        ClassifyResponse mockResponse = ClassifyResponse.newBuilder()
            .setPrediction(Prediction.newBuilder()
                .setClassIndex(1)
                .setProbability(0.85f))
            .build();

        when(salemClient.classify(any(), any()))
            .thenReturn(CompletableFuture.completedFuture(mockResponse));

        MLInferenceService service = new MLInferenceService(
            featureReader, salemClient, "production", "my-problem");

        // Act
        MLResult result = service.classify(context, "user123")
            .toCompletableFuture()
            .join();

        // Assert
        assertEquals(1, result.getClassIndex());
        assertEquals(0.85f, result.getProbability(), 0.01);
    }
}
```

## Mocking Fonzie Reader

```java
@Test
void testFeatureFetch() {
    // Arrange
    FeatureSet mockFeatureSet = FeatureSet.newBuilder()
        .putContinuous("streams30d", 1500.0f)
        .putCategorical("subscriptionType", "premium")
        .build();

    RequestedBatchFeatures mockBatchFeatures = mock(RequestedBatchFeatures.class);
    when(mockBatchFeatures.itemFeatures())
        .thenReturn(CompletableFuture.completedFuture(List.of(mockFeatureSet)));

    when(featureReader.readBatch(any(), anyList()))
        .thenReturn(mockBatchFeatures);

    // Act
    FeatureSet result = service.getFeatureSet(context, "user123")
        .toCompletableFuture()
        .join();

    // Assert
    assertEquals(1500.0f, result.getContinuousMap().get("streams30d"), 0.01);
}
```

## Testing Combined Flow

```java
@Test
void testEndToEndClassification() {
    // Mock Fonzie
    FeatureSet mockFeatures = FeatureSet.newBuilder()
        .putContinuous("streams30d", 1500.0f)
        .build();

    RequestedBatchFeatures mockBatch = mock(RequestedBatchFeatures.class);
    when(mockBatch.itemFeatures())
        .thenReturn(CompletableFuture.completedFuture(List.of(mockFeatures)));
    when(featureReader.readBatch(any(), anyList()))
        .thenReturn(mockBatch);

    // Mock Salem
    ClassifyResponse mockResponse = ClassifyResponse.newBuilder()
        .setPrediction(Prediction.newBuilder()
            .setClassIndex(1)
            .setProbability(0.9f))
        .build();
    when(salemClient.classify(any(), any()))
        .thenReturn(CompletableFuture.completedFuture(mockResponse));

    // Act
    MLResult result = service.classify(context, "user123")
        .toCompletableFuture()
        .join();

    // Assert
    assertEquals(1, result.getClassIndex());

    // Verify interactions
    verify(featureReader).readBatch(eq(context), any());
    verify(salemClient).classify(eq(context), argThat(req ->
        req.getProblem().getId().equals("my-problem")));
}
```

## Testing Error Handling

```java
@Test
void testSalemError_returnsFallback() {
    // Arrange
    when(featureReader.readBatch(any(), anyList()))
        .thenReturn(mockSuccessfulBatch());

    when(salemClient.classify(any(), any()))
        .thenReturn(CompletableFuture.failedFuture(
            new RuntimeException("Salem unavailable")));

    // Act
    MLResult result = serviceWithFallback.classify(context, "user123")
        .toCompletableFuture()
        .join();

    // Assert
    assertEquals(MLResult.UNKNOWN, result);
}

@Test
void testFonzieError_returnsFallback() {
    // Arrange
    RequestedBatchFeatures failedBatch = mock(RequestedBatchFeatures.class);
    when(failedBatch.itemFeatures())
        .thenReturn(CompletableFuture.failedFuture(
            new RuntimeException("Fonzie unavailable")));
    when(featureReader.readBatch(any(), anyList()))
        .thenReturn(failedBatch);

    // Act
    MLResult result = serviceWithFallback.classify(context, "user123")
        .toCompletableFuture()
        .join();

    // Assert
    assertEquals(MLResult.UNKNOWN, result);
}
```

## Testing Timeout

```java
@Test
void testTimeout_returnsFallback() {
    // Arrange
    CompletableFuture<ClassifyResponse> slowFuture = new CompletableFuture<>();
    // Never complete the future

    when(featureReader.readBatch(any(), anyList()))
        .thenReturn(mockSuccessfulBatch());
    when(salemClient.classify(any(), any()))
        .thenReturn(slowFuture);

    // Act
    MLResult result = serviceWithTimeout.classify(context, "user123")
        .toCompletableFuture()
        .join();

    // Assert
    assertEquals(MLResult.UNKNOWN, result);
}
```

## Integration Test Pattern

```java
@IntegrationTest
class MLServiceIntegrationTest {

    private static ServiceComponent component;

    @BeforeAll
    static void setup() {
        // Use test configuration
        Config testConfig = ConfigFactory.parseMap(Map.of(
            "salem.problem-id", "test-problem",
            "salem.slot", "staging"
        ));

        component = DaggerServiceComponent.builder()
            .config(testConfig)
            .build();
    }

    @Test
    void testRealClassification() {
        MLInferenceService service = component.mlInferenceService();

        // Use a test user
        MLResult result = service.classify(context, TEST_USER_ID)
            .toCompletableFuture()
            .join();

        assertNotNull(result);
        assertTrue(result.getProbability() >= 0 && result.getProbability() <= 1);
    }
}
```

## Test Fixtures

```java
public class MLTestFixtures {

    public static FeatureSet createUserFeatureSet() {
        return FeatureSet.newBuilder()
            .putContinuous("streams30d", 1500.0f)
            .putContinuous("sessions7d", 25.0f)
            .putCategorical("subscriptionType", "premium")
            .putCategorical("country", "SE")
            .build();
    }

    public static ClassifyResponse createClassifyResponse(int classIndex, float probability) {
        return ClassifyResponse.newBuilder()
            .setPrediction(Prediction.newBuilder()
                .setClassIndex(classIndex)
                .setProbability(probability)
                .addClassProbabilities(1 - probability)
                .addClassProbabilities(probability))
            .build();
    }

    public static RequestedBatchFeatures mockSuccessfulBatch(FeatureSet featureSet) {
        RequestedBatchFeatures mock = mock(RequestedBatchFeatures.class);
        when(mock.itemFeatures())
            .thenReturn(CompletableFuture.completedFuture(List.of(featureSet)));
        return mock;
    }
}
```

## Verification Patterns

```java
@Test
void testCorrectRequestFormat() {
    // Arrange
    ArgumentCaptor<ClassifyRequest> requestCaptor =
        ArgumentCaptor.forClass(ClassifyRequest.class);

    when(salemClient.classify(any(), requestCaptor.capture()))
        .thenReturn(CompletableFuture.completedFuture(mockResponse));

    // Act
    service.classify(context, "user123").toCompletableFuture().join();

    // Assert request format
    ClassifyRequest captured = requestCaptor.getValue();
    assertEquals("my-problem", captured.getProblem().getId());
    assertEquals("production", captured.getProblem().getSlotName());
    assertEquals("user123", captured.getContext().getSpotifyUid());
    assertEquals("my-service", captured.getClient().getId());
}
```

## Related Patterns

- [Salem Client](salem-client.md) - Client implementation
- [Fonzie Features](fonzie-features.md) - Feature reader implementation
- [Combined Inference](combined-inference.md) - End-to-end flow
