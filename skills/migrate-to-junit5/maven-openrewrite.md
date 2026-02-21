# Maven OpenRewrite Integration

OpenRewrite provides automated migration that handles the bulk of JUnit 4 to JUnit 5 conversion.

## Running the Migration

### One-time execution (no plugin changes)

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-testing-frameworks:RELEASE \
  -Drewrite.activeRecipes=org.openrewrite.java.testing.junit5.JUnit4to5Migration
```

### With plugin configured in pom.xml

Add to your `pom.xml`:

```xml
<plugin>
    <groupId>org.openrewrite.maven</groupId>
    <artifactId>rewrite-maven-plugin</artifactId>
    <version>5.34.0</version>
    <configuration>
        <activeRecipes>
            <recipe>org.openrewrite.java.testing.junit5.JUnit4to5Migration</recipe>
        </activeRecipes>
    </configuration>
    <dependencies>
        <dependency>
            <groupId>org.openrewrite.recipe</groupId>
            <artifactId>rewrite-testing-frameworks</artifactId>
            <version>2.12.0</version>
        </dependency>
    </dependencies>
</plugin>
```

Then run:

```bash
mvn rewrite:run
```

## What OpenRewrite Handles

- Import changes (`org.junit.*` -> `org.junit.jupiter.*`)
- Annotation changes (`@Before` -> `@BeforeEach`, etc.)
- Basic assertion conversions
- Test method visibility adjustments
- `@RunWith(MockitoJUnitRunner.class)` -> `@ExtendWith(MockitoExtension.class)`

## What OpenRewrite Doesn't Handle

See [known-issues.md](known-issues.md) for issues requiring manual intervention:

- Custom `@Rule` implementations
- `RuleChain` ordering
- Apollo `ServiceHelper`
- `GrpcCleanupRule`
- `TestCase` base class removal
- Some assertion parameter reordering

## Required Dependencies

Ensure these are in your `pom.xml`:

```xml
<!-- JUnit 5 -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>

<!-- Vintage engine for JUnit 4 compatibility during migration -->
<dependency>
    <groupId>org.junit.vintage</groupId>
    <artifactId>junit-vintage-engine</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>

<!-- Mockito JUnit 5 extension -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <version>5.5.0</version>
    <scope>test</scope>
</dependency>

<!-- AssertJ for fluent assertions (replaces Hamcrest) -->
<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>3.24.2</version>
    <scope>test</scope>
</dependency>
```

## Post-Migration Cleanup

After 100% migration, remove vintage engine, JUnit 4, and Hamcrest:

```xml
<!-- Remove these after full migration -->
<dependency>
    <groupId>org.junit.vintage</groupId>
    <artifactId>junit-vintage-engine</artifactId>
</dependency>
<dependency>
    <groupId>junit</groupId>
    <artifactId>junit</artifactId>
</dependency>
<!-- Remove Hamcrest if converted to AssertJ -->
<dependency>
    <groupId>org.hamcrest</groupId>
    <artifactId>hamcrest</artifactId>
</dependency>
```

## Troubleshooting

### OpenRewrite Fails to Run

**Error**: `Could not resolve dependencies`

**Fix**: Ensure you have network access to Maven Central:

```bash
mvn dependency:resolve
```

### Recipe Not Found

**Error**: `Recipe not found: org.openrewrite.java.testing.junit5.JUnit4to5Migration`

**Fix**: Check artifact coordinates are correct and use RELEASE or specific version:

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-testing-frameworks:2.12.0 \
  -Drewrite.activeRecipes=org.openrewrite.java.testing.junit5.JUnit4to5Migration
```

### Preview Without Applying Changes

To see what changes would be made without applying them:

```bash
mvn rewrite:dryRun
```

This generates a diff file in `target/rewrite/` directory.
