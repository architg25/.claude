# Padlock Encryption

Patterns for encrypting PII fields in Decibel using Padlock.

## Basic Encryption

**Use when**: Storing PII in Decibel fields

```decibel
version 1;

table {
  partition key {
    String userId = 1;
  }

  // Encrypted PII fields
  @Padlock(keyId = "my-team/user-pii-key")
  String email = 2;

  @Padlock(keyId = "my-team/user-pii-key")
  String phoneNumber = 3;

  // Non-PII fields (no encryption)
  String preferredLanguage = 4;
  Instant lastLoginTime = 5;
}
```

**Key concepts:**
- `@Padlock(keyId = "...")` - Encrypts the field value
- Key ID format: `<team>/<key-name>`
- Same key ID can be used for multiple fields

## Key Management

### Creating a Padlock Key

**Use when**: Setting up encryption for a new table

1. Request key in Padlock UI: https://padlock.spotify.net
2. Specify:
   - Key name (e.g., `user-pii-key`)
   - Team/namespace (e.g., `my-team`)
   - Authorized services (your service accounts)

3. Reference in schema:
```decibel
@Padlock(keyId = "my-team/user-pii-key")
```

### Key Rotation

**Use when**: Security requirements mandate key rotation

```decibel
// New key version is handled automatically by Padlock
// Data encrypted with old key can still be decrypted
@Padlock(keyId = "my-team/user-pii-key")
String sensitiveData = 2;
```

**Key rotation is transparent:**
- Old data decrypts with old key version
- New data encrypts with new key version
- No schema changes required

## Field Selection

### What to Encrypt

| Data Type | Encrypt? | Example |
|-----------|----------|---------|
| Email addresses | Yes | `user@example.com` |
| Phone numbers | Yes | `+1-555-123-4567` |
| Physical addresses | Yes | `123 Main St` |
| Names | Usually | `John Doe` |
| IP addresses | Usually | `192.168.1.1` |
| User preferences | No | `dark_mode=true` |
| Timestamps | No | `2024-01-15T10:30:00Z` |
| Internal IDs | No | `track-abc123` |

### What NOT to Encrypt

- **Partition keys** - Cannot be encrypted (needed for routing)
- **Sort keys** - Cannot be encrypted (needed for ordering)
- **Frequently filtered fields** - Encrypted data can't be filtered

## Apollo Integration

### Reading Encrypted Fields

**Use when**: Decryption in service code

```java
// Decryption is automatic when using generated client
UserDataRow row = repository.get("user-123").join().orElseThrow();

// Field is already decrypted
String email = row.getEmail();  // Plaintext value
```

### Writing Encrypted Fields

**Use when**: Encryption in service code

```java
// Encryption is automatic when using generated client
UserDataRow row = UserDataRow.builder()
    .userId("user-123")
    .email("user@example.com")  // Will be encrypted
    .build();

repository.put(row).join();
```

## Scio Integration

### Reading Encrypted Data

```scala
// Decryption happens automatically in DecibelIO
val users = sc.read(DecibelIO.read[UserRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "users"
))

// Fields are decrypted
users.map(u => u.email)  // Plaintext values
```

### Writing Encrypted Data

```scala
// Encryption happens automatically
users.write(DecibelIO.write[UserRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "users"
))
```

## Testing with Encryption

**Use when**: Testing encrypted field handling

```java
@Test
void shouldHandleEncryptedFields() {
    // InMemoryConnection handles encryption transparently
    InMemoryConnection connection = InMemoryConnection.create();
    Table<UserRow> table = connection.table(UserRow.class);

    UserRow row = UserRow.builder()
        .userId("test-user")
        .email("test@example.com")  // Encrypted in real Bigtable
        .build();

    table.put(row).join();

    UserRow retrieved = table.get(Key.of("test-user")).join().orElseThrow();
    assertThat(retrieved.getEmail()).isEqualTo("test@example.com");
}
```

## Troubleshooting

### Permission Denied

**Symptom**: `PadlockPermissionDeniedException` at runtime

**Solution**: Add your service account to the Padlock key's authorized list

### Key Not Found

**Symptom**: `PadlockKeyNotFoundException` during schema compilation

**Solution**:
1. Verify key exists in Padlock UI
2. Check key ID spelling in schema
3. Ensure team namespace is correct

### Decryption Failures

**Symptom**: `PadlockDecryptionException` when reading data

**Solution**:
1. Check service has read permissions on key
2. Verify key hasn't been deleted
3. Check for data corruption

## Best Practices

1. **One key per data category**: Group related PII under one key
2. **Document key purposes**: Keep track of which key protects what
3. **Test encryption in staging**: Verify before production deployment
4. **Monitor key usage**: Check Padlock audit logs regularly
5. **Plan for key rotation**: Ensure services can handle rotation
