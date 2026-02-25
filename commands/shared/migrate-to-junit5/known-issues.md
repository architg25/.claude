# Known Issues and Fixes

This document covers issues that automated migration (OpenRewrite) doesn't handle. Add new cases as discovered.

## Table of Contents

1. [@Rule not converted](#issue-rule-not-converted)
2. [@ClassRule not converted](#issue-classrule-not-converted)
3. [RuleChain not converted](#issue-rulechain-not-converted)
4. [GrpcCleanupRule not converted](#issue-grpccleanurule-not-converted)
5. [ExpectedException rule](#issue-expectedexception-rule)
6. [TemporaryFolder rule](#issue-temporaryfolder-rule)
7. [Timeout rule](#issue-timeout-rule)
8. [Missing @Testcontainers annotation](#issue-missing-testcontainers)
9. [Assert.assertThat removed](#issue-assertthat-removed)
10. [ExternalResourceSupport doesn't exist](#issue-externalresourcesupport)
11. [TestCase base class](#issue-testcase-base-class)
12. [Mockito UnnecessaryStubbingException](#issue-mockito-strictness)
13. [Parameter order swapped](#issue-parameter-order)
14. [Hamcrest to AssertJ conversion](#issue-hamcrest-assertj)
15. [Transitive JUnit 4 dependencies](#issue-transitive-dependencies)
16. [Public test class/method visibility](#issue-visibility)

---

## Issue: @Rule not converted

**Symptoms**: Build error about `@Rule` annotation not recognized, or test fields still using JUnit 4 `@Rule`.

**Cause**: OpenRewrite may not convert `@Rule` for custom rule implementations.

**Fix**: Convert to JUnit 5 extension pattern:

```java
// Before (JUnit 4)
@Rule
public MyCustomRule rule = new MyCustomRule();

// After (JUnit 5) - Option 1: @RegisterExtension
@RegisterExtension
MyCustomExtension extension = new MyCustomExtension();

// After (JUnit 5) - Option 2: Lifecycle methods
private MyResource resource;

@BeforeEach
void setUp() {
    resource = new MyResource();
    resource.start();
}

@AfterEach
void tearDown() {
    if (resource != null) {
        resource.close();
    }
}
```

---

## Issue: @ClassRule not converted

**Symptoms**: Class-level resources not being shared across tests.

**Fix**: Use static fields with static lifecycle methods:

```java
// Before (JUnit 4)
@ClassRule
public static PostgreSQLContainer POSTGRES = new PostgreSQLContainer();

// After (JUnit 5)
private static final PostgreSQLContainer POSTGRES = new PostgreSQLContainer();

@BeforeAll
static void setUp() {
    POSTGRES.start();
}

@AfterAll
static void tearDown() {
    POSTGRES.stop();
}
```

---

## Issue: RuleChain not converted

**Symptoms**: `IllegalStateException` about containers needing to start first.

**Fix**: Use `.dependsOn()` for container dependencies:

```java
// Before (JUnit 4)
@ClassRule
public static final RuleChain startup = RuleChain
    .outerRule(DATABASE)
    .around(SERVICE);

// After (JUnit 5)
@Container
static final PostgreSQLContainer DATABASE = new PostgreSQLContainer();

@Container
static final ApolloContainer SERVICE = ApolloContainer.imageFromBuild()
    .withDatabase(DATABASE)
    .dependsOn(DATABASE);
```

---

## Issue: GrpcCleanupRule not converted

**Symptoms**: Build error about `GrpcCleanupRule`, or gRPC resources not cleaned up.

**Fix**: Use lifecycle methods:

```java
// Before (JUnit 4)
@Rule
public final GrpcCleanupRule grpcCleanup = new GrpcCleanupRule();

// After (JUnit 5)
private Server server;
private ManagedChannel channel;

@AfterEach
void cleanup() {
    if (channel != null) {
        channel.shutdownNow();
    }
    if (server != null) {
        server.shutdownNow();
    }
}
```

---

## Issue: ExpectedException rule

**Symptoms**: Build error about `ExpectedException`.

**Fix**: Use `assertThrows()`:

```java
// Before (JUnit 4)
@Rule
public ExpectedException thrown = ExpectedException.none();

@Test
public void testException() {
    thrown.expect(IllegalArgumentException.class);
    thrown.expectMessage("Invalid input");
    methodThatThrows();
}

// After (JUnit 5)
@Test
void testException() {
    IllegalArgumentException exception = assertThrows(
        IllegalArgumentException.class,
        () -> methodThatThrows()
    );
    assertTrue(exception.getMessage().contains("Invalid input"));
}
```

**Best practice**: Keep only the throwing call in the lambda:

```java
// Good - minimal lambda
String input = prepareInput();
assertThrows(IllegalArgumentException.class, () -> processor.process(input));
```

---

## Issue: TemporaryFolder rule

**Symptoms**: Build error about `TemporaryFolder`.

**Fix**: Use `@TempDir`:

```java
// Before (JUnit 4)
@Rule
public TemporaryFolder tempFolder = new TemporaryFolder();

@Test
public void testWithTempFile() throws IOException {
    File file = tempFolder.newFile("test.txt");
}

// After (JUnit 5)
@TempDir
Path tempDir;

@Test
void testWithTempFile() throws IOException {
    Path file = tempDir.resolve("test.txt");
    Files.createFile(file);
}
```

---

## Issue: Timeout rule

**Symptoms**: Build error about `Timeout` rule.

**Fix**: Use `@Timeout` annotation:

```java
// Before (JUnit 4)
@Rule
public Timeout globalTimeout = Timeout.seconds(10);

// After (JUnit 5) - class level
@Timeout(10)
class MyTest {
    // All tests have 10-second timeout
}

// After (JUnit 5) - method level
@Test
@Timeout(value = 500, unit = TimeUnit.MILLISECONDS)
void testWithTimeout() {
}
```

---

## Issue: Missing @Testcontainers annotation

**Symptoms**: Containers not starting, `@Container` fields ignored.

**Fix**: Add `@Testcontainers` to test class:

```java
@Testcontainers
class MyIntegrationTest {
    @Container
    static PostgreSQLContainer postgres = new PostgreSQLContainer("postgres:latest");
}
```

---

## Issue: Assert.assertThat removed

**Symptoms**: Compilation error for `org.junit.Assert.assertThat`.

**Cause**: JUnit 5 removed `assertThat`.

**Fix (Default) - Convert to AssertJ**:

```java
// Best option - fluent API, better error messages
import static org.assertj.core.api.Assertions.assertThat;

assertThat(actual).isEqualTo(expected);
```

See [Hamcrest to AssertJ conversion](#issue-hamcrest-assertj) for full mapping table.

**Fix (Alternative) - Keep Hamcrest** (only if explicitly requested):

```java
// Use Hamcrest's MatcherAssert instead of JUnit's
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;

assertThat(actual, is(expected));
```

**Fix (Simple cases) - Convert to JUnit 5 native**:

```java
import static org.junit.jupiter.api.Assertions.assertEquals;

assertEquals(expected, actual);
```

---

## Issue: ExternalResourceSupport doesn't exist

**Symptoms**: Build error `cannot find symbol: class ExternalResourceSupport`.

**Cause**: OpenRewrite adds `@ExtendWith(ExternalResourceSupport.class)` but this class isn't available.

**Fix**: Remove annotation and convert to lifecycle methods:

```java
// OpenRewrite generated (broken)
@ExtendWith(ExternalResourceSupport.class)
class MyTest {
    @Rule
    public final SomeRule rule = new SomeRule();
}

// After (working)
class MyTest {
    private SomeRule rule;

    @BeforeEach
    void setUp() {
        rule = new SomeRule();
        rule.before();
    }

    @AfterEach
    void tearDown() {
        if (rule != null) {
            rule.after();
        }
    }
}
```

---

## Issue: TestCase base class

**Symptoms**: Tests run but aren't recognized by JUnit 5 runner.

**Cause**: `TestCase` classes use `testXxx()` naming convention without `@Test` annotations.

**Fix**:

```java
// Before (JUnit 4)
import junit.framework.TestCase;

public class MyTest extends TestCase {
    public void testSomething() {  // No @Test needed
        assertEquals(expected, actual);
    }
}

// After (JUnit 5)
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MyTest {  // Remove extends TestCase
    @Test  // Required in JUnit 5
    void testSomething() {
        assertEquals(expected, actual);
    }
}
```

**CRITICAL**: When removing `extends TestCase`:

1. Remove `import junit.framework.TestCase`
2. Add `@Test` to ALL `testXxx()` methods
3. Replace `junit.framework.TestCase.*` assertions with JUnit 5

---

## Issue: Mockito UnnecessaryStubbingException

**Symptoms**: `UnnecessaryStubbingException: Unnecessary stubbings detected`.

**Cause**: JUnit 5's Mockito extension uses strict stubbing by default.

**Fix Option 1 - Best**: Remove the unnecessary stubbing.

**Fix Option 2 - Quick**: Add lenient mode:

```java
@MockitoSettings(strictness = Strictness.LENIENT)
class MyTest {
}
```

**Fix Option 3 - Per-stub**:

```java
lenient().when(mock.method()).thenReturn(value);
```

---

## Issue: Parameter order swapped

**Symptoms**: Assertions pass when they should fail, or vice versa.

**Cause**: JUnit 5 swapped parameter order.

**Fix**:

```java
// JUnit 4
assertTrue(message, condition);
assertEquals(message, expected, actual);

// JUnit 5
assertTrue(condition, message);
assertEquals(expected, actual, message);
```

---

## Issue: Hamcrest to AssertJ conversion (default)

Convert Hamcrest assertions to AssertJ by default. AssertJ provides better IDE support, fluent API, and more descriptive failure messages. Common mappings:

| Hamcrest                                 | AssertJ                                       |
| ---------------------------------------- | --------------------------------------------- |
| `assertThat(x, is(y))`                   | `assertThat(x).isEqualTo(y)`                  |
| `assertThat(x, nullValue())`             | `assertThat(x).isNull()`                      |
| `assertThat(x, notNullValue())`          | `assertThat(x).isNotNull()`                   |
| `assertThat(collection, hasSize(n))`     | `assertThat(collection).hasSize(n)`           |
| `assertThat(collection, empty())`        | `assertThat(collection).isEmpty()`            |
| `assertThat(collection, contains(...))`  | `assertThat(collection).containsExactly(...)` |
| `assertThat(string, containsString(s))`  | `assertThat(string).contains(s)`              |
| `assertThat(x, instanceOf(Class.class))` | `assertThat(x).isInstanceOf(Class.class)`     |

---

## Issue: Transitive JUnit 4 dependencies

**Symptoms**: JUnit 4 still on classpath after removing direct dependency.

**Cause**: Other dependencies bring in JUnit 4 transitively.

**Detection**:

```bash
mvn dependency:tree | grep "junit:junit"
```

**Common problematic dependencies at Spotify**:

- `com.spotify:apollo-test` (brings in junit:junit:4.13.2)
- `com.spotify:spotify-apollo-test` (brings in junit-vintage-engine)

**Fix**: Exclude if not using JUnit 4 features from these libraries:

```xml
<dependency>
    <groupId>com.spotify</groupId>
    <artifactId>apollo-test</artifactId>
    <exclusions>
        <exclusion>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

---

## Issue: Public test class/method visibility

**Symptoms**: JUnit 5 allows package-private visibility but tests may still be public.

**Info**: JUnit 5 doesn't require `public` visibility for test classes and methods. You can optionally change to package-private:

```java
// JUnit 4 (required public)
public class MyTest {
    @Test
    public void testSomething() {}
}

// JUnit 5 (package-private allowed)
class MyTest {
    @Test
    void testSomething() {}
}
```

This is optional - public visibility still works.
