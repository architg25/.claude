---
name: java-simplification-patterns
description: Java code simplification patterns with before/after examples. Covers functional programming style, modern Java features (21/25), testing patterns, and library-specific simplifications. Use when reviewing Java code quality or identifying refactoring opportunities.
allowed-tools:
  - Read
---

# Java Simplification Patterns

Concrete before/after code transformation examples for Java simplification.

## Pattern Categories

- **[Functional Style](functional-style.md)**: Streams, Optional, lambdas, method references
- **[Modern Java Features](modern-java.md)**: Java 21 and 25 language features
- **[Testing Patterns](testing-patterns.md)**: Test simplifications and best practices
- **[Library Patterns](library-patterns.md)**: Common library idioms (Guava, Lombok, etc.)

## Quick Reference

### Static Import Violations

Before:
```java
import com.example.TestFixtures;

class MyTest {
    void test() {
        User user = TestFixtures.createUser("test");
        Order order = TestFixtures.createOrder(user);
    }
}
```

After:
```java
import static com.example.TestFixtures.*;

class MyTest {
    void test() {
        User user = createUser("test");
        Order order = createOrder(user);
    }
}
```

### Stream vs For-Loop

Before:
```java
List<String> names = new ArrayList<>();
for (User user : users) {
    if (user.isActive()) {
        names.add(user.getName());
    }
}
```

After:
```java
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .toList();
```

### Optional vs Null Check

Before:
```java
String name = user.getName();
if (name != null) {
    return name.toUpperCase();
} else {
    return "UNKNOWN";
}
```

After:
```java
return Optional.ofNullable(user.getName())
    .map(String::toUpperCase)
    .orElse("UNKNOWN");
```

For complete patterns with detailed examples, see the category files above.

## Conventions Used in Examples

All examples assume the following static imports unless otherwise shown:

```java
// Collectors
import static java.util.stream.Collectors.*;

// Guava
import static com.google.common.base.Preconditions.*;
import static com.google.common.collect.ImmutableList.*;
import static com.google.common.collect.ImmutableMap.*;

// Testing
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;
```

**Modern Java**: Examples target Java 21+ and use modern idioms like `.toList()` (Java 16+), pattern matching for switch, and record patterns.
