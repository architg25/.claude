# Schema Patterns

Patterns for designing Decibel table schemas.

## Basic Schema Structure

**Use when**: Creating a new Decibel table

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

  // Data columns
  String content = 3;
  Optional<Long> rating = 4;
}
```

**Key concepts:**
- `partition key` - Required. Determines data distribution across nodes
- `sort key` - Optional. Orders rows within a partition
- Field numbers (`= 1`, `= 2`) - Schema versioning, never reuse deleted numbers

## Key Design Patterns

### Time-Series Data

**Use when**: Storing events, logs, or historical data

```decibel
version 1;

table {
  partition key {
    String entityId = 1;
  }
  sort key {
    @Descending
    Instant eventTime = 2;
  }

  String eventType = 3;
  Bytes payload = 4;
}
```

**Benefits:**
- `@Descending` returns most recent events first
- Efficient range scans within a partition

### Composite Keys

**Use when**: Multiple dimensions identify a row

```decibel
version 1;

table {
  partition key {
    String tenantId = 1;
    String userId = 2;
  }
  sort key {
    String resourceId = 3;
  }

  Bytes data = 4;
}
```

**Benefits:**
- Multi-tenant data isolation
- Efficient queries within tenant+user scope

### Lookup Tables

**Use when**: Simple key-value lookups without ordering

```decibel
version 1;

table {
  partition key {
    String entityId = 1;
  }

  // No sort key needed for simple lookups
  String metadata = 2;
  Instant lastUpdated = 3;
}
```

## Data Types

| Type | Description | Use For |
|------|-------------|---------|
| `String` | UTF-8 text | IDs, names, content |
| `Long` | 64-bit integer | Counts, timestamps |
| `Double` | 64-bit float | Scores, metrics |
| `Boolean` | true/false | Flags |
| `Instant` | Timestamp | Event times |
| `Bytes` | Binary data | Serialized objects |
| `Optional<T>` | Nullable wrapper | Optional fields |
| `List<T>` | Ordered collection | Arrays |
| `Map<K,V>` | Key-value pairs | Metadata |

## Annotations

| Annotation | Location | Purpose |
|------------|----------|---------|
| `@Descending` | Sort key field | Reverse ordering |
| `@Padlock(keyId = "...")` | Any field | PII encryption |

## Anti-Patterns

### Avoid: Large Partitions

Before (avoid):
```decibel
partition key {
  String countryCode = 1;  // Low cardinality = hot partitions
}
```

After:
```decibel
partition key {
  String countryCode = 1;
  String userId = 2;  // Higher cardinality
}
```

### Avoid: Unbounded Lists

Before (avoid):
```decibel
List<String> allEvents = 3;  // Can grow indefinitely
```

After:
```decibel
// Store events in separate rows with sort key
sort key {
  Instant eventTime = 2;
}
String eventType = 3;
```

## Schema Evolution

- **Adding fields**: Add new fields with new field numbers - safe
- **Removing fields**: Mark as deprecated, keep field number reserved
- **Changing types**: Create new field, migrate data, remove old field
- **Never reuse field numbers**: Can cause data corruption
