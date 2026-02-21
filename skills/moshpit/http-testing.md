# HTTP Testing

Patterns for HTTP API load testing with Moshpit.

## Basic HTTP Request

**Use when**: Simple GET request testing

```yaml
source:
  http:
    - path: '/api/v1/endpoint'
      method: 'GET'
```

## HTTP Methods

### GET Request

```yaml
source:
  http:
    - path: '/api/v1/users/123'
      method: 'GET'
```

### POST Request

```yaml
source:
  http:
    - path: '/api/v1/users'
      method: 'POST'
      content_type: 'application/json'
      body: |
        {
          "name": "Test User",
          "email": "test@example.com"
        }
```

### PUT Request

```yaml
source:
  http:
    - path: '/api/v1/users/123'
      method: 'PUT'
      content_type: 'application/json'
      body: |
        {
          "name": "Updated User"
        }
```

### DELETE Request

```yaml
source:
  http:
    - path: '/api/v1/users/123'
      method: 'DELETE'
```

## Headers

### Common Headers

```yaml
source:
  http:
    - path: '/api/v1/endpoint'
      method: 'GET'
      headers:
        content-type: 'application/json'
        accept: 'application/json'
        x-spotify-clientid: 'my-load-test'
        x-request-id: '{{uuid}}'
```

### Authentication Headers

```yaml
source:
  http:
    - path: '/api/v1/secure-endpoint'
      method: 'GET'
      headers:
        authorization: 'Bearer {{token}}'
```

## Request Bodies

### JSON Body

```yaml
source:
  http:
    - path: '/api/v1/endpoint'
      method: 'POST'
      content_type: 'application/json'
      body: |
        {
          "field1": "value1",
          "field2": 123
        }
```

### Form Data

```yaml
source:
  http:
    - path: '/api/v1/form'
      method: 'POST'
      content_type: 'application/x-www-form-urlencoded'
      body: 'field1=value1&field2=value2'
```

### Dynamic Body with Variables

```yaml
data_source:
  type: gcs
  path: 'gs://my-bucket/test-data.json'

source:
  http:
    - path: '/api/v1/users'
      method: 'POST'
      content_type: 'application/json'
      body: |
        {
          "user_id": "{{user_id}}",
          "name": "{{name}}"
        }
```

## Multiple Endpoints

### Sequential Requests

```yaml
source:
  http:
    - path: '/api/v1/login'
      method: 'POST'
      body: '{"username": "test"}'
    - path: '/api/v1/dashboard'
      method: 'GET'
      depends_on: 'login'
```

### Weighted Distribution

```yaml
source:
  http:
    - path: '/api/v1/users'
      method: 'GET'
      weight: 80  # 80% of requests
    - path: '/api/v1/users'
      method: 'POST'
      weight: 15  # 15% of requests
    - path: '/api/v1/admin'
      method: 'GET'
      weight: 5   # 5% of requests
```

## Response Validation

### Status Code Validation

```yaml
source:
  http:
    - path: '/api/v1/endpoint'
      method: 'GET'
      expected_status: 200
```

### Multiple Valid Status Codes

```yaml
source:
  http:
    - path: '/api/v1/endpoint'
      method: 'GET'
      expected_status: [200, 201, 204]
```

### Response Time Thresholds

```yaml
source:
  http:
    - path: '/api/v1/endpoint'
      method: 'GET'
      response_time_threshold_ms: 500
```

## Query Parameters

### Static Parameters

```yaml
source:
  http:
    - path: '/api/v1/search'
      method: 'GET'
      query_params:
        q: 'test query'
        limit: 10
        offset: 0
```

### Dynamic Parameters

```yaml
source:
  http:
    - path: '/api/v1/search'
      method: 'GET'
      query_params:
        q: '{{search_query}}'
        user_id: '{{user_id}}'
```

## Complete HTTP Example

```yaml
namespace: 'my-service-http-load-test'
headers:
  x-spotify-clientid: 'my-load-test'
  x-correlation-id: '{{uuid}}'

targets:
  - name: 'User API Load Test'
    target_id: 'user_api_test'
    requests_per_second: 100
    duration_seconds: 300
    ramp_up_duration_seconds: 60
    estimated_service_response_time_millis: 200
    base_service_uri: 'http://user-service.testing'
    source:
      http:
        # Read operations (80%)
        - path: '/api/v1/users/{{user_id}}'
          method: 'GET'
          weight: 80
          expected_status: 200
          response_time_threshold_ms: 100

        # Write operations (20%)
        - path: '/api/v1/users'
          method: 'POST'
          weight: 20
          content_type: 'application/json'
          body: |
            {
              "name": "Load Test User {{uuid}}",
              "email": "loadtest-{{uuid}}@example.com"
            }
          expected_status: 201
          response_time_threshold_ms: 500
```

## Troubleshooting HTTP Tests

### Connection Refused

- Check service is running in target environment
- Verify network policies allow load test traffic
- Check base_service_uri is correct

### 4xx Errors

- Verify authentication headers
- Check request body format
- Validate query parameters

### High Latency

- Check estimated_service_response_time_millis
- Reduce RPS if service is overloaded
- Check for network issues between regions
