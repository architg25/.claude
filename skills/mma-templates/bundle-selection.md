# Bundle Selection

Patterns for choosing the right MMA bundle for your service.

## Available Bundles

### Apollo Bundle

**Use when**: Standard Apollo services with HTTP and/or gRPC endpoints

```yaml
panels:
  - template: apollo
    type: bundle
    exclude_grpc: false  # Include gRPC metrics
```

**Provides:**
- HTTP request rate and latency
- HTTP error rates by status code
- gRPC request rate and latency (if enabled)
- gRPC error rates by code
- JVM metrics (heap, GC, threads)

### Kubernetes Bundle

**Use when**: Monitoring infrastructure metrics

```yaml
panels:
  - template: k8s
    type: bundle
```

**Provides:**
- Pod CPU and memory usage
- Container restarts
- Pod scheduling status
- Resource limits vs usage

### gRPC Bundle

**Use when**: gRPC-only services (no HTTP)

```yaml
panels:
  - template: grpc
    type: bundle
```

**Provides:**
- gRPC server request rate
- gRPC server latency (p50, p90, p99)
- gRPC error ratio by code
- gRPC client metrics (if applicable)

### Pub/Sub Bundle

**Use when**: Services consuming from Pub/Sub

```yaml
panels:
  - template: pubsub
    type: bundle
```

**Provides:**
- Message consumption rate
- Processing latency
- Subscription backlog
- Acknowledgment rate

## Bundle Combinations

### Full-Stack Service

**Use when**: Apollo service with Kubernetes deployment

```yaml
panels:
  - template: apollo
    type: bundle
  - template: k8s
    type: bundle
```

### API Gateway

**Use when**: High-traffic HTTP/gRPC entry point

```yaml
panels:
  - template: apollo
    type: bundle
    override:
      http/server/latency-p99:
        threshold_ms: 100  # Stricter latency
        action: pagerduty
```

### Background Worker

**Use when**: Pub/Sub consumer with no HTTP endpoints

```yaml
panels:
  - template: pubsub
    type: bundle
  - template: k8s
    type: bundle
```

## Bundle Options

### Apollo Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `exclude_grpc` | bool | false | Exclude gRPC panels |
| `exclude_http` | bool | false | Exclude HTTP panels |
| `exclude_jvm` | bool | false | Exclude JVM metrics |

```yaml
panels:
  - template: apollo
    type: bundle
    exclude_grpc: true   # HTTP-only service
    exclude_jvm: false   # Keep JVM metrics
```

### Kubernetes Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `namespace_filter` | string | "" | Filter by namespace |
| `container_filter` | string | "" | Filter by container name |

```yaml
panels:
  - template: k8s
    type: bundle
    namespace_filter: "my-namespace"
```

## Decision Tree

```
Is your service deployed on Kubernetes?
├── Yes → Include k8s bundle
│
Does it handle HTTP traffic?
├── Yes → Include apollo bundle (with HTTP)
│
Does it handle gRPC traffic?
├── Yes → Include apollo bundle (with gRPC) OR grpc bundle
│
Does it consume from Pub/Sub?
├── Yes → Include pubsub bundle
│
Does it have custom metrics?
├── Yes → Add custom panels (see custom-metrics.md)
```

## Excluding Panels

### Exclude Specific Panels from Bundle

```yaml
panels:
  - template: apollo
    type: bundle
    exclude:
      - http/server/request-size  # Don't need this
      - jvm/gc-time               # Not relevant
```

### Exclude Entire Categories

```yaml
panels:
  - template: apollo
    type: bundle
    exclude_grpc: true   # No gRPC in this service
```

## Common Mistakes

### Wrong Bundle for Service Type

Before (wrong):
```yaml
# Using grpc bundle for Apollo service
panels:
  - template: grpc  # Misses HTTP metrics!
    type: bundle
```

After (correct):
```yaml
# Use apollo bundle, includes both
panels:
  - template: apollo
    type: bundle
```

### Missing Kubernetes Bundle

Before (incomplete):
```yaml
# Only application metrics
panels:
  - template: apollo
    type: bundle
```

After (complete):
```yaml
# Include infrastructure metrics
panels:
  - template: apollo
    type: bundle
  - template: k8s
    type: bundle
```

## Bundle Versions

Bundles are versioned in the core templates repository:

```yaml
metadata:
  schemaVersion: 5  # Use latest schema version
```

When upgrading schema versions, check the [changelog](https://ghe.spotify.net/monitoring/mma-core-templates-prom/blob/master/CHANGELOG.md) for breaking changes.
