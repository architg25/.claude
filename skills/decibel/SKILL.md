---
name: decibel
description: Decibel key-value SDK patterns for Cloud Bigtable. Covers schema design, Apollo/Scio integration, in-memory testing, Padlock encryption, and CLI operations. Use when working with NoSQL storage at Spotify.
allowed-tools:
  - Read
---

# Decibel Patterns

Patterns for Spotify's key-value SDK for Cloud Bigtable.

## Pattern Categories

- **[Schema Patterns](schema-patterns.md)**: Table design, key structure, column families
- **[Apollo Integration](apollo-integration.md)**: DecibelModule, repository pattern, async operations
- **[Scio Integration](scio-integration.md)**: DecibelIO for batch pipelines
- **[Testing Patterns](testing-patterns.md)**: In-memory connections, test fixtures
- **[Padlock Encryption](padlock-encryption.md)**: PII protection with Padlock
- **[CLI Operations](cli-operations.md)**: decibel-cli and decibel-admin-cli usage

## Quick Reference

### Schema Definition
```decibel
version 1;

table {
  partition key {
    String userId = 1;
  }
  sort key {
    @Descending
    Instant timestamp = 2;
  }
  String content = 3;
  Optional<Long> rating = 4;
}
```

### Apollo Module Setup
```java
DecibelModule.create(YourDatabase.Connection.class)
```

### Common CLI Commands
| Task | Command |
|------|---------|
| Read row | `decibel-cli read --key "userId=abc"` |
| Scan table | `decibel-cli scan --limit 10` |
| Create table | `decibel-admin-cli create --schema schema.decibel` |
| Describe table | `decibel-admin-cli describe` |

## Critical Constraints

- **Never** use raw Bigtable client - use Decibel SDK for type safety
- **Always** define partition key first, then optional sort key
- **Always** use `@Descending` annotation for reverse-chronological queries
- **Always** use Padlock for PII fields

## Related Skills

- [locus-caching](../locus-caching/SKILL.md) - Caching layer in front of Decibel
- [apollo-configuration](../apollo-configuration/SKILL.md) - HOCON patterns for database connection configuration

## Documentation Links

- [Main Docs](https://backstage.spotify.net/docs/default/component/decibel/)
- [Apollo Getting Started](https://backstage.spotify.net/docs/default/component/decibel/getting-started/apollo/)
- [Scio Getting Started](https://backstage.spotify.net/docs/default/component/decibel/getting-started-scio/first-steps/)

## Support Channels

- #decibel-support - Main support channel
