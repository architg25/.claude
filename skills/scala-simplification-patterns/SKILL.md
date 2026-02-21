---
name: scala-simplification-patterns
description: Scala code simplification patterns with before/after examples. Covers functional programming style, Scala 2.13 features, and common library idioms. Use when reviewing Scala code quality.
allowed-tools:
  - Read
---

# Scala Simplification Patterns

Concrete before/after code transformation examples for Scala simplification.

## Pattern Categories

- **[Functional Style](functional-style.md)**: Pattern matching, Option/Either/Try, for-comprehensions
- **[Scala 2.13 Features](scala-2.13-features.md)**: Option.when, LazyList, tap/pipe, collection improvements
- **[Library Patterns](library-patterns.md)**: JavaConverters, Algebird, Magnolify

## Quick Reference

### Pattern Matching vs If-Else

Before:
```scala
def describe(x: Any): String = {
  if (x.isInstanceOf[Int]) {
    "integer: " + x.asInstanceOf[Int]
  } else if (x.isInstanceOf[String]) {
    "string: " + x.asInstanceOf[String]
  } else {
    "unknown"
  }
}
```

After:
```scala
def describe(x: Any): String = x match {
  case i: Int    => s"integer: $i"
  case s: String => s"string: $s"
  case _         => "unknown"
}
```

### Option.when vs If-Some-None

Before:
```scala
if (condition) Some(value) else None
```

After:
```scala
Option.when(condition)(value)
```

### For-Comprehension vs Nested flatMap

Before:
```scala
maybeUser.flatMap { user =>
  maybeAddress.flatMap { address =>
    maybeCity.map { city =>
      (user, address, city)
    }
  }
}
```

After:
```scala
for {
  user    <- maybeUser
  address <- maybeAddress
  city    <- maybeCity
} yield (user, address, city)
```

For complete patterns with detailed examples, see the category files above.

## Conventions Used in Examples

All examples assume Scala 2.13 and the following imports unless otherwise shown:

```scala
import scala.jdk.CollectionConverters._
import scala.util.{Try, Success, Failure}
```

**Scio-Specific**: For Scio pipeline patterns, see the `scio-patterns` skill.
