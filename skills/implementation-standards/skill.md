# Implementation Standards

## Implementation Flow

Use the repo's CLAUDE.md to figure out the structure of the repo first, including how to build and test.

1. **Understand** - Study existing patterns in codebase
2. **Test** - Write test first if interface is clear; after exploratory spike if not
3. **Implement** - Minimal code to pass tests
4. **Refactor** - Clean up with tests still passing
5. **Commit** - With clear message explaining "why"

**Note**: TDD is ideal but not dogma. Spike first if you need to explore the problem space.

## Architecture Principles

- **Composition over inheritance** - Use dependency injection
- **Interfaces over singletons** - Enable testing and flexibility
- **Explicit over implicit** - Clear data flow and dependencies
- **Test-driven when possible** - Never disable tests, fix them

## Code Quality

**Every commit must**:
- Compile successfully
- Pass all existing tests
- Include tests for new functionality
- Follow project formatting/linting

**Before committing**:
- Run formatters/linters
- Self-review changes
- Ensure commit message explains "why"

## Error Handling

- Fail fast with descriptive messages
- Include context for debugging
- Handle errors at appropriate level
- Never silently swallow exceptions

## Project Integration

### Learning the Codebase

- Find 3 similar features/components
- Identify common patterns and conventions
- Use same libraries/utilities when possible
- Follow existing test patterns

### Tooling

- Use project's existing build system
- Use project's test framework
- Use project's formatter/linter settings
- Don't introduce new tools without strong justification

## Quality Gates

### Definition of Done

- [ ] Tests written and passing
- [ ] Code follows project conventions
- [ ] No linter/formatter warnings
- [ ] Commit messages are clear
- [ ] Implementation matches plan
- [ ] No TODOs without issue numbers

### Test Guidelines

- Test behavior, not implementation
- One assertion per test when possible
- Clear test names describing scenario
- Use existing test utilities/helpers
- Tests should be deterministic
