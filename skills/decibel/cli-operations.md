# CLI Operations

Common operations using decibel-cli and decibel-admin-cli.

## Installation

**Mac (Homebrew)**:
```bash
brew install spotify/public/decibel-cli
brew install spotify/public/decibel-admin-cli
```

**Verify installation**:
```bash
decibel-cli --version
decibel-admin-cli --version
```

## Configuration

### Save Default Config

**Use when**: Setting up CLI for a table

```bash
# Data operations CLI
decibel-cli config save \
  --namespace bigtable:<PROJECT>/<INSTANCE> \
  --table <TABLE>

# Admin CLI
decibel-admin-cli config save \
  --namespace bigtable:<PROJECT>/<INSTANCE>
```

### Override Config Per-Command

```bash
decibel-cli read \
  --namespace bigtable:my-project/my-instance \
  --table my-table \
  --key "userId=abc123"
```

## Data Operations (decibel-cli)

### Read Single Row

**Use when**: Fetching a specific row by key

```bash
# Simple partition key
decibel-cli read --key "userId=abc123"

# Composite key
decibel-cli read --key "tenantId=acme,userId=user-1"

# With sort key
decibel-cli read --key "userId=abc123,timestamp=2024-01-15T10:30:00Z"
```

### Scan Rows

**Use when**: Querying multiple rows

```bash
# Scan with limit
decibel-cli scan --limit 10

# Scan partition
decibel-cli scan --partition-key "userId=abc123" --limit 20

# Scan with filter
decibel-cli scan --filter "status='active'" --limit 50
```

### Write Row

**Use when**: Inserting or updating data

```bash
# Interactive write
decibel-cli write --key "userId=abc123"

# Write from JSON
echo '{"content": "hello", "rating": 5}' | decibel-cli write --key "userId=abc123"
```

### Delete Row

**Use when**: Removing data

```bash
# Delete single row
decibel-cli delete --key "userId=abc123"

# Delete with confirmation
decibel-cli delete --key "userId=abc123" --confirm
```

## Admin Operations (decibel-admin-cli)

### Create Table

**Use when**: Provisioning a new table

```bash
# From schema file
decibel-admin-cli create --schema path/to/schema.decibel

# With custom table name
decibel-admin-cli create --schema schema.decibel --table my-table
```

### Describe Table

**Use when**: Inspecting table structure

```bash
decibel-admin-cli describe

# Output shows:
# - Partition key fields
# - Sort key fields
# - Data columns
# - Annotations (Padlock, etc.)
```

### List Tables

**Use when**: Discovering available tables

```bash
decibel-admin-cli list

# Filter by prefix
decibel-admin-cli list --prefix "user-"
```

### Destroy Table

**Use when**: Removing a table (use with caution!)

```bash
# Requires explicit confirmation
decibel-admin-cli destroy --table my-table --confirm
```

## Output Formats

### JSON Output

**Use when**: Processing output programmatically

```bash
decibel-cli read --key "userId=abc123" --format json

# Pipe to jq
decibel-cli scan --limit 10 --format json | jq '.[] | .userId'
```

### Table Output

**Use when**: Human-readable display

```bash
decibel-cli scan --limit 10 --format table
```

## Common Workflows

### Debug Data Issues

```bash
# 1. Check if row exists
decibel-cli read --key "userId=problematic-user"

# 2. Scan related rows
decibel-cli scan --partition-key "userId=problematic-user" --limit 100

# 3. Check specific field
decibel-cli read --key "userId=problematic-user" --format json | jq '.status'
```

### Bulk Operations

```bash
# Export partition to file
decibel-cli scan --partition-key "tenantId=acme" --format json > export.json

# Count rows in partition
decibel-cli scan --partition-key "userId=abc123" --count-only
```

### Schema Validation

```bash
# Validate schema syntax
decibel-admin-cli validate --schema schema.decibel

# Compare to deployed schema
decibel-admin-cli diff --schema schema.decibel --table my-table
```

## Troubleshooting

### Authentication Errors

```bash
# Re-authenticate with GCP
gcloud auth application-default login

# Verify project access
gcloud config list project
```

### Connection Timeouts

```bash
# Increase timeout
decibel-cli read --key "userId=abc" --timeout 30s
```

### Permission Denied

```bash
# Check service account
gcloud auth list

# Verify Bigtable permissions
gcloud bigtable instances describe <INSTANCE>
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `DECIBEL_NAMESPACE` | Default namespace |
| `DECIBEL_TABLE` | Default table |
| `DECIBEL_PROJECT` | Default GCP project |

```bash
export DECIBEL_NAMESPACE="bigtable:my-project/my-instance"
export DECIBEL_TABLE="my-table"

# Now simpler commands work
decibel-cli read --key "userId=abc"
```
