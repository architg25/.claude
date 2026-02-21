# Spotify-Specific JUnit 4 Rules

This document covers Spotify-internal JUnit 4 rules that require custom migration patterns.

## Table of Contents

1. [ServiceHelper (Apollo)](#servicehelper-apollo)
2. [BigtableEmulatorRule](#bigtableemulator-rule)
3. [ApolloGrpcTestServerRule](#apollogrpctestserver-rule)
4. [GrpcPingServerRule / HealthCheckerRule](#grpcpingserver-rule)
5. [Combined Apollo + Bigtable Rules](#combined-apollo-bigtable)

---

## ServiceHelper (Apollo)

**Location**: Widespread across Apollo-based services

**Symptoms**: `ServiceHelper not started` error, NullPointerException when accessing ServiceHelper.

**Cause**: Apollo's `ServiceHelper` is a JUnit 4 Rule.

### Per-Class Lifecycle (@ClassRule -> @BeforeAll/@AfterAll)

```java
// Before (JUnit 4)
@ClassRule
public static final ServiceHelper serviceHelper = ServiceHelper.create(Main::configure, SERVICE_NAME);

// After (JUnit 5)
private static final ServiceHelper SERVICE_HELPER = ServiceHelper.create(Main::configure, SERVICE_NAME);

@BeforeAll
static void setUp() throws Exception {
    SERVICE_HELPER.start();
}

@AfterAll
static void tearDown() throws Exception {
    SERVICE_HELPER.close();
}
```

### Per-Test Lifecycle with Extension (@Rule -> @RegisterExtension)

```java
// After (JUnit 5) - using ServiceHelperExtension
@RegisterExtension
static final ServiceHelperExtension serviceHelperExtension =
    ServiceHelperExtension.create(Main::configure, SERVICE_NAME)
        .startTimeoutSeconds(30);

@Test
void testRequest() {
    ServiceHelper serviceHelper = serviceHelperExtension.getServiceHelper();
    // ...
}
```

---

## BigtableEmulatorRule

**Location**: Multiple repos (catapult/monofonix, colander/longclaw, cuepoints/*, ads/unipod-mapper)

**Pattern**: Extends `ExternalResource`, manages Bigtable emulator lifecycle with data/admin clients.

### Before (JUnit 4)

```java
@Rule
public BigtableEmulatorRule bigtable = BigtableEmulatorRule.create();

@Test
public void testBigtable() {
    BigtableDataClient client = bigtable.dataClient();
    BigtableTableAdminClient admin = bigtable.tableAdminClient();
    // ...
}
```

### After (JUnit 5) - Per-Test Lifecycle

```java
private Emulator emulator;
private BigtableDataClient dataClient;
private BigtableTableAdminClient tableAdminClient;

private static final String PROJECT_ID = "test-project";
private static final String INSTANCE_ID = "test-instance";

@BeforeEach
void setUp() throws Exception {
    emulator = Emulator.createBundled();
    emulator.start();

    BigtableDataSettings dataSettings = BigtableDataSettings
        .newBuilderForEmulator(emulator.getPort())
        .setProjectId(PROJECT_ID)
        .setInstanceId(INSTANCE_ID)
        .build();
    dataClient = BigtableDataClient.create(dataSettings);

    BigtableTableAdminSettings adminSettings = BigtableTableAdminSettings
        .newBuilderForEmulator(emulator.getPort())
        .setProjectId(PROJECT_ID)
        .setInstanceId(INSTANCE_ID)
        .build();
    tableAdminClient = BigtableTableAdminClient.create(adminSettings);
}

@AfterEach
void tearDown() {
    if (dataClient != null) dataClient.close();
    if (tableAdminClient != null) tableAdminClient.close();
    if (emulator != null) emulator.stop();
}
```

### After (JUnit 5) - Per-Class Lifecycle (Shared Emulator)

```java
private static Emulator emulator;
private static BigtableDataClient dataClient;

@BeforeAll
static void setUpClass() throws Exception {
    emulator = Emulator.createBundled();
    emulator.start();
    // Create clients...
}

@AfterAll
static void tearDownClass() {
    if (dataClient != null) dataClient.close();
    if (emulator != null) emulator.stop();
}
```

---

## ApolloGrpcTestServerRule

**Location**: auditorium/auditorium-monorepo-bazel-test, protean/monorepo-techdocs-demo

**Pattern**: Extends `ExternalResource`, manages gRPC server with Apollo integration.

### Before (JUnit 4)

```java
@Rule
public ApolloGrpcTestServerRule grpcServer = new ApolloGrpcTestServerRule()
    .withConfig("some.key", "value");

@Test
public void testGrpc() {
    Channel channel = grpcServer.channel();
    // ...
}
```

### After (JUnit 5)

```java
private ApolloGrpcTestServerRule grpcServer;

@BeforeEach
void setUp() throws IOException {
    grpcServer = new ApolloGrpcTestServerRule()
        .withConfig("some.key", "value");
    grpcServer.init();  // Explicit initialization
}

@AfterEach
void tearDown() {
    if (grpcServer != null && grpcServer.grpcServer() != null) {
        try {
            grpcServer.grpcServer().close();
        } catch (IOException e) {
            // Log error
        }
    }
}

@Test
void testGrpc() {
    Channel channel = grpcServer.channel();
    // ...
}
```

---

## GrpcPingServerRule

**Location**: auditorium/auditorium-monorepo-bazel-test (apollo/modules/grpc)

**Pattern**: Testing gRPC health checks and ping endpoints.

### Before (JUnit 4)

```java
@Rule
public GrpcPingServerRule pingServer = new GrpcPingServerRule();
```

### After (JUnit 5)

Same pattern as ApolloGrpcTestServerRule - use lifecycle methods.

---

## Combined Apollo + Bigtable

**Location**: bases/database-autoscaler

**Pattern**: Combines Apollo ServiceHelper with Bigtable emulator.

### Before (JUnit 4)

```java
@ClassRule
public static final RuleChain chain = RuleChain
    .outerRule(bigtable)
    .around(serviceHelper);
```

### After (JUnit 5)

Use `@BeforeAll` to start both, ensuring proper ordering:

```java
private static final BigtableEmulatorRule bigtable = BigtableEmulatorRule.create();
private static final ServiceHelper serviceHelper = ServiceHelper.create(Main::configure, SERVICE_NAME);

@BeforeAll
static void setUp() throws Exception {
    // Start Bigtable first (outerRule equivalent)
    bigtable.before();

    // Then start Apollo with Bigtable connection
    serviceHelper.start();
}

@AfterAll
static void tearDown() {
    // Stop in reverse order
    serviceHelper.close();
    bigtable.after();
}
```

**Key Point**: The ordering in `@BeforeAll`/`@AfterAll` replaces `RuleChain` ordering. Start dependencies first (outerRule), then dependents (around).

---

## Finding Other Spotify Rules

If you encounter an unfamiliar Spotify-specific rule, search for it:

```bash
# Find rule usage across Spotify codebase
# Use code search MCP: "@Rule public.*YourRuleName"

# Check if rule extends ExternalResource or TestRule
grep -r "extends ExternalResource" src/
grep -r "implements TestRule" src/
```

The conversion pattern is generally:
1. Move field initialization to `@BeforeEach` or `@BeforeAll`
2. Call rule's `before()` method (or equivalent initialization)
3. Add cleanup in `@AfterEach` or `@AfterAll`
4. Call rule's `after()` method (or equivalent cleanup)
