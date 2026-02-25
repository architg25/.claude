---
description: Migrate JUnit 4 tests to JUnit 5 for Maven projects. Handles @Test, @Before/@After, @Rule/@ClassRule annotations, and optionally converts Hamcrest to AssertJ. Use when you see imports from org.junit (not org.junit.jupiter), @Rule annotations, or JUnit 4 assertions.
allowed-tools:
  - Read
  - Bash
---

# Migrate to JUnit 5

Automate JUnit 4 to JUnit 5 migration for Maven projects using OpenRewrite recipes, followed by iterative fixes for issues the automated migration doesn't handle.

## Reference Files

- **@shared/migrate-to-junit5/known-issues.md** — Issues OpenRewrite doesn't handle, with before/after examples
- **@shared/migrate-to-junit5/maven-openrewrite.md** — Automated migration setup for Maven projects
- **@shared/migrate-to-junit5/spotify-rules.md** — Spotify-specific JUnit 4 rules (ServiceHelper, BigtableEmulatorRule, etc.)

## Migration Workflow

### Step 1: Run OpenRewrite Migration

```bash
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-testing-frameworks:RELEASE \
  -Drewrite.activeRecipes=org.openrewrite.java.testing.junit5.JUnit4to5Migration
```

See @shared/migrate-to-junit5/maven-openrewrite.md for full details and troubleshooting.

### Step 2: Build and Identify Issues

```bash
mvn test-compile
```

### Step 3: Fix Issues Iteratively

For each build/test error, check @shared/migrate-to-junit5/known-issues.md and @shared/migrate-to-junit5/spotify-rules.md. Fix, rebuild, repeat.

### Step 4: Run Tests

```bash
mvn test
```

### Step 5: Format Code

```bash
mvn fmt:format
```

### Step 6: Validate Migration Complete

```bash
# Verify no JUnit 4 imports remain
grep -r "import org.junit.Test" src/test/java | wc -l
grep -r "import junit.framework.TestCase" src/test/java | wc -l
grep -r "extends TestCase" src/test/java | wc -l
```

All counts should be 0.

## Quick Reference

### Annotation Mapping

| JUnit 4                              | JUnit 5                               |
| ------------------------------------ | ------------------------------------- |
| `@Before`                            | `@BeforeEach`                         |
| `@After`                             | `@AfterEach`                          |
| `@BeforeClass`                       | `@BeforeAll` (static method)          |
| `@AfterClass`                        | `@AfterAll` (static method)           |
| `@Ignore`                            | `@Disabled`                           |
| `@Test(expected=X.class)`            | `assertThrows(X.class, () -> ...)`    |
| `@Test(timeout=1000)`                | `@Timeout(value=1, unit=SECONDS)`     |
| `@RunWith(MockitoJUnitRunner.class)` | `@ExtendWith(MockitoExtension.class)` |

### Import Mapping

| JUnit 4                    | JUnit 5                                      |
| -------------------------- | -------------------------------------------- |
| `org.junit.Test`           | `org.junit.jupiter.api.Test`                 |
| `org.junit.Before`         | `org.junit.jupiter.api.BeforeEach`           |
| `org.junit.Assert.*`       | `org.junit.jupiter.api.Assertions.*`         |
| `org.junit.runner.RunWith` | `org.junit.jupiter.api.extension.ExtendWith` |

### AssertJ Migration (Default)

By default, convert Hamcrest assertions to AssertJ for better IDE support and fluent API. See @shared/migrate-to-junit5/known-issues.md for conversion patterns.

To preserve Hamcrest instead (if explicitly requested), see the known-issues doc for keeping Hamcrest with `MatcherAssert`.

## Core Principles

1. **Incremental Migration**: JUnit 4 and 5 coexist during migration. Never remove JUnit 4 dependencies until 100% migrated.

2. **Small Batches**: Migrate 5-10 files at a time, validating after each batch.

3. **Complete Conversion**: Convert ALL assertions/imports in a file at once. Never leave mixed syntax.

4. **Immediate Validation**: Run `mvn test-compile` and `mvn test` after each batch.

## Critical Constraints

- **Always** use JUnit 5 assertions parameter order: `assertEquals(expected, actual, message)`
- **Always** add `@Test` to all test methods when removing `extends TestCase`
- **Never** mix JUnit 4 and JUnit 5 annotations in the same file
- **Always** run `mvn fmt:format` after migration to maintain code style
