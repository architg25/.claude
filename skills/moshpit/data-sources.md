# Data Sources

Patterns for loading dynamic test data in Moshpit.

## Data Source Types

| Type | Use Case | Latency |
|------|----------|---------|
| BigQuery | Large datasets, SQL queries | Higher |
| GCS | Pre-generated files | Lower |
| Inline | Small static datasets | Lowest |

## BigQuery Data Source

**Use when**: Dynamic data from production-like datasets

```yaml
data_source:
  type: bigquery
  project: 'my-gcp-project'
  query: |
    SELECT user_id, username
    FROM `my-project.users.active_users`
    WHERE last_active > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    LIMIT 10000

targets:
  - target_id: 'test'
    source:
      http:
        - path: '/api/users/{{user_id}}'
          method: 'GET'
```

### Query Best Practices

```yaml
data_source:
  type: bigquery
  query: |
    -- Use LIMIT to control data size
    -- Use WHERE to filter relevant data
    -- Select only needed columns
    SELECT
      user_id,
      username,
      subscription_type
    FROM `my-project.users.users`
    WHERE
      is_active = TRUE
      AND country = 'SE'
    LIMIT 5000
```

### Caching BigQuery Results

```yaml
data_source:
  type: bigquery
  query: '...'
  cache:
    enabled: true
    ttl_minutes: 60  # Reuse data for 1 hour
```

## GCS Data Source

**Use when**: Pre-generated test data

### JSON File

```yaml
data_source:
  type: gcs
  path: 'gs://my-bucket/test-data/users.json'
  format: json

# users.json content:
# [{"user_id": "123", "name": "Alice"}, {"user_id": "456", "name": "Bob"}]
```

### CSV File

```yaml
data_source:
  type: gcs
  path: 'gs://my-bucket/test-data/users.csv'
  format: csv
  headers: true  # First row is header

# users.csv content:
# user_id,name,email
# 123,Alice,alice@example.com
# 456,Bob,bob@example.com
```

### Newline-Delimited JSON

```yaml
data_source:
  type: gcs
  path: 'gs://my-bucket/test-data/users.ndjson'
  format: ndjson

# users.ndjson content:
# {"user_id": "123", "name": "Alice"}
# {"user_id": "456", "name": "Bob"}
```

## Inline Data Source

**Use when**: Small, static test data

```yaml
data_source:
  type: inline
  records:
    - user_id: '123'
      name: 'Alice'
    - user_id: '456'
      name: 'Bob'
    - user_id: '789'
      name: 'Charlie'
```

## Variable Usage

### In URL Path

```yaml
source:
  http:
    - path: '/api/users/{{user_id}}'
      method: 'GET'
```

### In Query Parameters

```yaml
source:
  http:
    - path: '/api/search'
      query_params:
        user_id: '{{user_id}}'
        name: '{{name}}'
```

### In Request Body

```yaml
source:
  http:
    - path: '/api/users'
      method: 'POST'
      body: |
        {
          "user_id": "{{user_id}}",
          "name": "{{name}}",
          "email": "{{email}}"
        }
```

### In Headers

```yaml
source:
  http:
    - path: '/api/endpoint'
      headers:
        x-user-id: '{{user_id}}'
```

## Data Sampling

### Random Sampling

```yaml
data_source:
  type: bigquery
  query: '...'
  sampling:
    type: random
    # Each request picks a random record
```

### Sequential Sampling

```yaml
data_source:
  type: bigquery
  query: '...'
  sampling:
    type: sequential
    # Cycles through records in order
```

### Weighted Sampling

```yaml
data_source:
  type: bigquery
  query: |
    SELECT user_id, subscription_type, weight
    FROM users
  sampling:
    type: weighted
    weight_column: weight
```

## Multiple Data Sources

### Combined Sources

```yaml
data_sources:
  users:
    type: bigquery
    query: 'SELECT user_id FROM users LIMIT 1000'

  products:
    type: gcs
    path: 'gs://bucket/products.json'

targets:
  - target_id: 'test'
    source:
      http:
        - path: '/api/users/{{users.user_id}}/products/{{products.product_id}}'
```

## Data Generation

### Built-in Generators

| Generator | Output | Example |
|-----------|--------|---------|
| `{{uuid}}` | UUID v4 | `550e8400-e29b-41d4-a716-446655440000` |
| `{{timestamp}}` | ISO timestamp | `2024-01-15T10:30:00Z` |
| `{{random_int}}` | Random integer | `42` |
| `{{random_string}}` | Random alphanumeric | `aB3kX9mQ` |

### Usage

```yaml
source:
  http:
    - path: '/api/items'
      method: 'POST'
      body: |
        {
          "id": "{{uuid}}",
          "created_at": "{{timestamp}}",
          "random_seed": {{random_int}}
        }
```

## Complete Example

```yaml
namespace: 'user-service-load-test'

data_source:
  type: bigquery
  project: 'my-project'
  query: |
    SELECT
      user_id,
      username,
      country
    FROM `my-project.users.active_users`
    WHERE
      last_login > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
      AND country IN ('US', 'GB', 'SE')
    ORDER BY RAND()
    LIMIT 5000
  cache:
    enabled: true
    ttl_minutes: 30

targets:
  - name: 'User Profile Test'
    target_id: 'user_profile'
    requests_per_second: 100
    duration_seconds: 300
    base_service_uri: 'http://user-service.testing'
    source:
      http:
        - path: '/api/v1/users/{{user_id}}/profile'
          method: 'GET'
          headers:
            x-country: '{{country}}'
            x-request-id: '{{uuid}}'
```

## Troubleshooting

### BigQuery Timeout

- Add LIMIT to query
- Use partitioned tables
- Pre-cache results

### GCS Access Denied

- Check bucket permissions
- Verify service account access
- Check file path is correct

### Variable Not Found

- Verify column name in query/file
- Check for typos in `{{variable}}`
- Ensure data source is loaded before targets
