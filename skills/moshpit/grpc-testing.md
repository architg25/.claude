# gRPC Testing

Patterns for gRPC service load testing with Moshpit.

## Basic gRPC Request

**Use when**: Testing a single gRPC method

```yaml
source:
  grpc:
    - service: 'com.spotify.myservice.UserService'
      method: 'GetUser'
      request:
        user_id: '12345'
```

## gRPC Configuration

### Service Definition

```yaml
base_service_uri: 'grpc://my-service:50051'
source:
  grpc:
    - service: 'com.spotify.myservice.UserService'
      method: 'GetUser'
      request:
        user_id: '12345'
```

### Proto Import

```yaml
proto:
  import_path: 'protos/'
  files:
    - 'user_service.proto'

source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
```

## Request Types

### Unary RPC

```yaml
source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      request:
        user_id: '12345'
```

### Server Streaming RPC

```yaml
source:
  grpc:
    - service: 'FeedService'
      method: 'StreamEvents'
      request:
        user_id: '12345'
        limit: 100
      streaming: server
```

### Client Streaming RPC

```yaml
source:
  grpc:
    - service: 'UploadService'
      method: 'UploadChunks'
      requests:
        - chunk_id: 1
          data: 'base64encodeddata=='
        - chunk_id: 2
          data: 'base64encodeddata=='
      streaming: client
```

## Request Bodies

### Simple Request

```yaml
source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      request:
        user_id: '12345'
```

### Nested Message

```yaml
source:
  grpc:
    - service: 'OrderService'
      method: 'CreateOrder'
      request:
        user_id: '12345'
        items:
          - product_id: 'prod-1'
            quantity: 2
          - product_id: 'prod-2'
            quantity: 1
        shipping:
          address: '123 Main St'
          city: 'Stockholm'
```

### Dynamic Request with Variables

```yaml
data_source:
  type: bigquery
  query: 'SELECT user_id FROM users LIMIT 1000'

source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      request:
        user_id: '{{user_id}}'
```

## Metadata (Headers)

### Static Metadata

```yaml
source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      metadata:
        x-request-id: '{{uuid}}'
        x-spotify-clientid: 'load-test'
      request:
        user_id: '12345'
```

### Authentication Metadata

```yaml
source:
  grpc:
    - service: 'SecureService'
      method: 'GetSecretData'
      metadata:
        authorization: 'Bearer {{token}}'
      request:
        resource_id: 'secret-123'
```

## Multiple Methods

### Weighted Distribution

```yaml
source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      weight: 70
      request:
        user_id: '{{user_id}}'

    - service: 'UserService'
      method: 'ListUsers'
      weight: 25
      request:
        page_size: 10

    - service: 'UserService'
      method: 'CreateUser'
      weight: 5
      request:
        name: 'Test User {{uuid}}'
```

### Multiple Services

```yaml
source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      weight: 50
      request:
        user_id: '{{user_id}}'

    - service: 'PlaylistService'
      method: 'GetPlaylist'
      weight: 50
      request:
        playlist_id: '{{playlist_id}}'
```

## Response Validation

### Status Code Validation

```yaml
source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      request:
        user_id: '12345'
      expected_status: OK
```

### Valid Status Codes

| Status | Use Case |
|--------|----------|
| `OK` | Success |
| `NOT_FOUND` | Expected for some lookups |
| `INVALID_ARGUMENT` | Client error |
| `DEADLINE_EXCEEDED` | Timeout |

```yaml
source:
  grpc:
    - service: 'UserService'
      method: 'GetUser'
      expected_status: [OK, NOT_FOUND]
```

## Complete gRPC Example

```yaml
namespace: 'my-service-grpc-load-test'

proto:
  import_path: 'protos/'
  files:
    - 'user_service.proto'

targets:
  - name: 'User Service gRPC Load Test'
    target_id: 'user_grpc_test'
    requests_per_second: 200
    duration_seconds: 300
    ramp_up_duration_seconds: 60
    estimated_service_response_time_millis: 50
    base_service_uri: 'grpc://user-service.testing:50051'
    source:
      grpc:
        # Read operations (80%)
        - service: 'com.spotify.users.UserService'
          method: 'GetUser'
          weight: 60
          metadata:
            x-request-id: '{{uuid}}'
          request:
            user_id: '{{user_id}}'
          expected_status: [OK, NOT_FOUND]

        - service: 'com.spotify.users.UserService'
          method: 'ListUsers'
          weight: 20
          request:
            page_size: 20
            page_token: ''

        # Write operations (20%)
        - service: 'com.spotify.users.UserService'
          method: 'UpdateUser'
          weight: 20
          request:
            user_id: '{{user_id}}'
            update_mask:
              paths: ['display_name']
            user:
              display_name: 'Updated {{timestamp}}'

data_source:
  type: bigquery
  query: |
    SELECT user_id
    FROM `my-project.users.active_users`
    WHERE last_active > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    LIMIT 10000
```

## Troubleshooting gRPC Tests

### Connection Issues

- Verify gRPC port (usually 50051)
- Check TLS configuration if using secure channel
- Verify service name resolution

### Proto Compilation Errors

- Ensure proto files are in correct path
- Check for missing dependencies
- Verify package names match service definition

### Serialization Errors

- Check request field names match proto
- Verify field types (string vs int)
- Check for required fields
