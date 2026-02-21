# Testing Patterns

Patterns for testing Decibel database operations.

## In-Memory Connection

**Use when**: Unit testing without external dependencies

```java
import com.spotify.decibel.testing.InMemoryConnection;

class UserRepositoryTest {
    private InMemoryConnection connection;
    private UserRepository repository;

    @BeforeEach
    void setUp() {
        connection = InMemoryConnection.create();
        repository = new UserRepository(connection);
    }

    @Test
    void shouldStoreAndRetrieveUser() {
        UserDataRow row = UserDataRow.builder()
            .userId("user-123")
            .name("Test User")
            .build();

        repository.put(row).join();

        Optional<UserDataRow> result = repository.get("user-123").join();
        assertThat(result).isPresent();
        assertThat(result.get().getName()).isEqualTo("Test User");
    }
}
```

**Benefits:**
- No Bigtable instance needed
- Fast execution
- Deterministic results

## Test Fixtures

**Use when**: Setting up consistent test data

```java
class DecibelTestFixtures {

    public static void seedTestData(Connection connection) {
        Table<UserDataRow> table = connection.table(UserDataRow.class);

        List<UserDataRow> testUsers = List.of(
            UserDataRow.builder()
                .userId("user-1")
                .name("Alice")
                .build(),
            UserDataRow.builder()
                .userId("user-2")
                .name("Bob")
                .build()
        );

        CompletableFuture.allOf(
            testUsers.stream()
                .map(table::put)
                .toArray(CompletableFuture[]::new)
        ).join();
    }
}
```

## JUnit 5 Extension

**Use when**: Consistent setup across test classes

```java
import org.junit.jupiter.api.extension.*;

public class DecibelTestExtension implements BeforeEachCallback, AfterEachCallback {
    private InMemoryConnection connection;

    @Override
    public void beforeEach(ExtensionContext context) {
        connection = InMemoryConnection.create();
        // Inject into test instance
    }

    @Override
    public void afterEach(ExtensionContext context) {
        connection.close();
    }

    public Connection getConnection() {
        return connection;
    }
}

// Usage
@ExtendWith(DecibelTestExtension.class)
class MyRepositoryTest {
    @Inject
    private Connection connection;

    // tests...
}
```

## Testing Async Operations

**Use when**: Testing CompletableFuture-based code

```java
@Test
void shouldHandleParallelReads() {
    // Setup
    seedTestData(connection);

    // Execute parallel reads
    List<CompletableFuture<Optional<UserDataRow>>> futures = List.of(
        repository.get("user-1"),
        repository.get("user-2"),
        repository.get("user-3")
    );

    List<Optional<UserDataRow>> results = futures.stream()
        .map(CompletableFuture::join)
        .toList();

    // Verify
    assertThat(results.get(0)).isPresent();
    assertThat(results.get(1)).isPresent();
    assertThat(results.get(2)).isEmpty();  // Non-existent user
}
```

## Testing Error Scenarios

**Use when**: Verifying error handling

```java
@Test
void shouldHandleMissingData() {
    Optional<UserDataRow> result = repository.get("non-existent").join();

    assertThat(result).isEmpty();
}

@Test
void shouldHandleInvalidKey() {
    assertThatThrownBy(() ->
        repository.get(null).join()
    ).isInstanceOf(IllegalArgumentException.class);
}
```

## Testing Scans

**Use when**: Testing range queries

```java
@Test
void shouldScanWithinRange() {
    // Setup - insert time-series data
    Instant now = Instant.now();
    for (int i = 0; i < 10; i++) {
        EventRow row = EventRow.builder()
            .userId("user-1")
            .timestamp(now.minus(Duration.ofHours(i)))
            .eventType("click")
            .build();
        eventTable.put(row).join();
    }

    // Execute scan for last 5 hours
    List<EventRow> results = eventTable.scan()
        .partitionKey("user-1")
        .sortKeyRange(Range.from(now.minus(Duration.ofHours(5))))
        .execute()
        .join();

    // Verify
    assertThat(results).hasSize(5);
    assertThat(results).allMatch(r ->
        r.getTimestamp().isAfter(now.minus(Duration.ofHours(5)))
    );
}
```

## Mocking Pattern

**Use when**: Testing code that uses Decibel without InMemoryConnection

```java
@Test
void shouldHandleDecibelFailure() {
    // Mock the table
    Table<UserDataRow> mockTable = mock(Table.class);
    when(mockTable.get(any()))
        .thenReturn(CompletableFuture.failedFuture(
            new DecibelException("Connection failed")
        ));

    // Mock the connection
    Connection mockConnection = mock(Connection.class);
    when(mockConnection.table(UserDataRow.class))
        .thenReturn(mockTable);

    // Test error handling
    UserService service = new UserService(mockConnection);

    assertThatThrownBy(() -> service.getUser("user-1").join())
        .hasCauseInstanceOf(DecibelException.class);
}
```

## Integration Testing

**Use when**: Testing against real Bigtable (staging)

```java
@Tag("integration")
class DecibelIntegrationTest {

    private static Connection connection;

    @BeforeAll
    static void setUpConnection() {
        connection = DecibelConnectionFactory.create(
            DecibelConfig.builder()
                .projectId("my-staging-project")
                .instanceId("my-staging-instance")
                .build()
        );
    }

    @Test
    void shouldReadFromRealBigtable() {
        // Test against real data
        // Use test-specific partition keys to avoid conflicts
    }

    @AfterAll
    static void cleanUp() {
        // Clean up test data
        connection.close();
    }
}
```

## Test Data Patterns

### Time-Based Test Keys

**Use when**: Avoiding conflicts with concurrent tests

```java
private String testKey() {
    return "test-" + Instant.now().toEpochMilli() + "-" + UUID.randomUUID();
}
```

### Test User ID Pattern

**Use when**: Consistent test user identification

```java
// Use well-known test prefixes
private static final String TEST_USER_PREFIX = "test-user-";

private String testUserId(String suffix) {
    return TEST_USER_PREFIX + suffix;
}
```
