---
name: code-simplification
description: Code simplification patterns for Java, Scala, and Python with before/after examples. Use when reviewing code quality, identifying refactoring opportunities, or simplifying code. Covers common cross-language patterns (naming, structure, DRY, SOLID, comment quality, test anti-patterns), Java patterns (streams, Optional, lambdas, modern Java 21/25 features, testing, Guava/Lombok), Scala patterns (pattern matching, Option/Either/Try, for-comprehensions, Scala 2.13 features, Algebird, Magnolify), and Python patterns (comprehensions, generators, modern 3.10+ features, async/await for LLM/AI work, pytest, import conventions).
allowed-tools:
  - Read
---

# Code Simplification Patterns

Unified code simplification skill covering cross-language patterns and language-specific idioms.

## Common Patterns (All Languages)

Loaded by default for any code review or simplification task.

- @common/naming-conventions.md - Methods, classes, variables, constants
- @common/structural-patterns.md - DRY, SOLID, method length, cyclomatic complexity
- @common/comment-quality.md - WHY not WHAT, self-documenting code
- @common/test-anti-patterns.md - Low-value tests to avoid (enum tests, static config tests, mapping tests)

## Language-Specific Patterns

Load based on detected language in the code under review.

### Java

- @java/functional-style.md - Streams, Optional, lambdas, method references
- @java/modern-java.md - Java 21 and 25 language features
- @java/testing-patterns.md - Test simplifications and best practices
- @java/library-patterns.md - Common library idioms (Guava, Lombok)

### Scala

- @scala/functional-style.md - Pattern matching, Option/Either/Try, for-comprehensions
- @scala/scala-2.13-features.md - Option.when, LazyList, tap/pipe, collection improvements
- @scala/library-patterns.md - JavaConverters, Algebird, Magnolify

### Python

- @python/functional-style.md - List comprehensions, generators, functional patterns
- @python/modern-python.md - Python 3.10+ features (match, walrus, type unions)
- @python/async-patterns.md - async/await best practices for LLM/AI work
- @python/testing-patterns.md - pytest fixtures, parametrization, async testing
- @python/import-patterns.md - Top-level imports, avoiding inline imports

## Usage

1. **Always load common patterns** - they apply to all languages
2. **Detect language** from the code being reviewed
3. **Load the relevant language section** for language-specific patterns
4. **Apply patterns** as before/after transformation suggestions

## Conventions

### Java/Scala

- **Static imports**: Common utilities like `checkNotNull()`, `checkArgument()` assume static imports
- **Modern Java**: Examples use Java 16+ features like `.toList()` where applicable
- **Streams over loops**: Prefer functional stream operations over explicit iteration

### Scala

- **Scala 2.13**: Examples assume Scala 2.13 and `scala.jdk.CollectionConverters._`
- **Scio**: For Scio pipeline patterns, see the `scio-patterns` skill

### Python

- **snake_case**: Variables and functions use snake_case (not camelCase)
- **Modern Python**: Examples assume Python 3.10+ for type unions and pattern matching
- **Comprehensions over loops**: Prefer list/dict comprehensions over explicit iteration
- **Package Manager**: UV
- **Linter/Formatter**: Ruff
