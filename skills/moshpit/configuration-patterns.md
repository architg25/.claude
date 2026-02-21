# Configuration Patterns

Patterns for Moshpit YAML configuration structure.

## Basic Configuration

**Use when**: Setting up a simple load test

```yaml
namespace: 'my-service-load-test'
targets:
  - name: 'API Load Test'
    target_id: 'api_load_test'
    requests_per_second: 100
    duration_seconds: 300
    ramp_up_duration_seconds: 60
    estimated_service_response_time_millis: 1000
    region: 'europe-west1'
    environment: 'testing'
    base_service_uri: 'http://my-service'
    source:
      http:
        - path: '/api/endpoint'
          method: 'GET'
```

## Configuration Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `namespace` | string | Unique identifier for the test |
| `targets` | list | List of target configurations |
| `target_id` | string | Unique ID for the target |
| `requests_per_second` | int | Target RPS |
| `duration_seconds` | int | Total test duration |
| `base_service_uri` | string | Service endpoint |
| `source` | object | Request definition |

### Optional Fields

| Field | Default | Description |
|-------|---------|-------------|
| `ramp_up_duration_seconds` | 0 | Gradual RPS increase |
| `estimated_service_response_time_millis` | 1000 | Expected latency |
| `region` | auto | GCP region |
| `environment` | testing | Target environment |
| `headers` | {} | Global headers |

## Multiple Targets

**Use when**: Testing multiple endpoints

```yaml
namespace: 'my-service-comprehensive-test'
targets:
  - name: 'Read Endpoint'
    target_id: 'read_test'
    requests_per_second: 500
    duration_seconds: 300
    base_service_uri: 'http://my-service'
    source:
      http:
        - path: '/api/v1/users'
          method: 'GET'

  - name: 'Write Endpoint'
    target_id: 'write_test'
    requests_per_second: 50
    duration_seconds: 300
    base_service_uri: 'http://my-service'
    source:
      http:
        - path: '/api/v1/users'
          method: 'POST'
          body: '{"name": "test"}'
```

## Ramp-Up Patterns

### Linear Ramp-Up

```yaml
targets:
  - target_id: 'gradual_test'
    requests_per_second: 100
    ramp_up_duration_seconds: 60  # 0 to 100 RPS over 60 seconds
    duration_seconds: 300
```

### Step Ramp-Up

```yaml
targets:
  - target_id: 'step_1'
    requests_per_second: 50
    duration_seconds: 120
  - target_id: 'step_2'
    requests_per_second: 100
    duration_seconds: 120
    depends_on: 'step_1'
  - target_id: 'step_3'
    requests_per_second: 200
    duration_seconds: 120
    depends_on: 'step_2'
```

## Environment Configuration

### Testing Environment

```yaml
environment: 'testing'
base_service_uri: 'http://my-service.testing.svc.cluster.local'
```

### Staging Environment

```yaml
environment: 'staging'
base_service_uri: 'http://my-service.staging.svc.cluster.local'
```

### Production (Requires Approval!)

```yaml
environment: 'production'
base_service_uri: 'http://my-service.production.svc.cluster.local'
# WARNING: Requires explicit approval!
```

## Headers Configuration

### Global Headers

```yaml
headers:
  x-spotify-clientid: 'my-load-test'
  x-request-id: '{{uuid}}'
  authorization: 'Bearer {{token}}'

targets:
  - target_id: 'test'
    # Headers applied to all requests
```

### Per-Target Headers

```yaml
targets:
  - target_id: 'test'
    headers:
      x-custom-header: 'target-specific'
    source:
      http:
        - path: '/api/endpoint'
          headers:
            x-endpoint-header: 'request-specific'
```

## Variable Substitution

### Built-in Variables

| Variable | Description |
|----------|-------------|
| `{{uuid}}` | Random UUID |
| `{{timestamp}}` | Current timestamp |
| `{{random_int}}` | Random integer |

### Data Source Variables

```yaml
data_source:
  type: bigquery
  query: 'SELECT user_id FROM my_dataset.users LIMIT 1000'

targets:
  - target_id: 'test'
    source:
      http:
        - path: '/api/users/{{user_id}}'
```

## Scheduling

### One-Time Run

```yaml
schedule:
  type: manual
  # Triggered via Backstage or CLI
```

### Recurring Tests

```yaml
schedule:
  type: cron
  expression: '0 6 * * *'  # Daily at 6 AM
```

## Validation

### Pre-Deployment Validation

```bash
# Validate configuration syntax
moshpit validate --config moshpit-config.yaml

# Dry run (no actual requests)
moshpit run --config moshpit-config.yaml --dry-run
```

### Configuration Linting

- Namespace must be unique
- target_id must be alphanumeric with underscores
- RPS must be positive integer
- Duration must be at least 10 seconds

## Best Practices

1. **Use descriptive namespaces**: Include service and test type
2. **Set realistic response times**: Prevents resource over-allocation
3. **Always use ramp-up**: Avoids cold-start failures
4. **Version your configs**: Keep in version control
5. **Document test purpose**: Add comments explaining goals
