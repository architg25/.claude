# Panel Customization

Patterns for customizing MMA dashboard panels.

## Override Syntax

### Basic Override

**Use when**: Changing default thresholds

```yaml
panels:
  - template: apollo
    type: bundle
    override:
      http/server/latency-p99:
        threshold_ms: 500
```

### Multiple Overrides

```yaml
override:
  http/server/latency-p99:
    threshold_ms: 200
  grpc/server/rpc-error-ratio:
    threshold_pct: 0.5
  http/server/error-ratio:
    threshold_pct: 1
```

## Common Overrides

### Latency Thresholds

| Service Type | P99 Threshold | P90 Threshold |
|--------------|---------------|---------------|
| User-facing API | 100-200ms | 50-100ms |
| Internal API | 200-500ms | 100-200ms |
| Background job | 1000-5000ms | 500-1000ms |

```yaml
override:
  http/server/latency-p99:
    threshold_ms: 200
  http/server/latency-p90:
    threshold_ms: 100
```

### Error Rate Thresholds

| Service Type | Error Threshold |
|--------------|-----------------|
| Critical path | 0.1% - 0.5% |
| Standard API | 0.5% - 1% |
| Best effort | 1% - 5% |

```yaml
override:
  http/server/error-ratio:
    threshold_pct: 0.5
  grpc/server/rpc-error-ratio:
    threshold_pct: 0.5
```

### Alert Actions

| Action | When to Use |
|--------|-------------|
| `no_action` | Informational, no alerts |
| `slack` | Non-urgent notifications |
| `pagerduty` | Requires immediate response |

```yaml
override:
  http/server/latency-p99:
    threshold_ms: 200
    action: pagerduty
  http/server/request-rate:
    action: no_action  # Informational only
```

## Threshold Strategies

### Absolute Thresholds

**Use when**: Known SLA/SLO requirements

```yaml
override:
  http/server/latency-p99:
    threshold_ms: 200  # SLO: 200ms p99
```

### Relative Thresholds

**Use when**: Alerting on deviation from baseline

```yaml
override:
  http/server/latency-p99:
    threshold_deviation_pct: 50  # Alert if 50% higher than baseline
```

### Multi-Window Thresholds

**Use when**: Reducing noise from transient spikes

```yaml
override:
  http/server/error-ratio:
    threshold_pct: 1
    window: 5m      # Aggregate over 5 minutes
    for: 2m         # Must persist for 2 minutes
```

## Panel Visibility

### Hiding Panels

```yaml
panels:
  - template: apollo
    type: bundle
    exclude:
      - http/server/request-size
      - http/server/response-size
```

### Collapsing Rows

```yaml
panels:
  - template: apollo
    type: bundle
    collapse:
      - jvm-metrics  # Collapsed by default
```

## Custom Labels

### Adding Context

```yaml
panels:
  - template: apollo
    type: bundle
    labels:
      environment: production
      team: my-team
```

### Filter by Label

```yaml
override:
  http/server/latency-p99:
    filter:
      endpoint: "/api/v1/users"  # Only this endpoint
```

## Graph Customization

### Y-Axis Limits

```yaml
override:
  http/server/latency-p99:
    y_max: 1000  # Cap at 1 second
```

### Time Range

```yaml
override:
  http/server/request-rate:
    default_time_range: 6h  # Show last 6 hours
```

## Combining Overrides with Exclusions

### Customize What You Keep

```yaml
panels:
  - template: apollo
    type: bundle
    exclude:
      - jvm/heap-usage      # Don't need
      - jvm/thread-count    # Don't need
    override:
      http/server/latency-p99:
        threshold_ms: 100
        action: pagerduty
```

## Best Practices

### Start Permissive, Tighten Later

```yaml
# Week 1: Observe baseline
override:
  http/server/error-ratio:
    action: no_action

# Week 2: Add slack notification
override:
  http/server/error-ratio:
    threshold_pct: 5
    action: slack

# Week 3: Reduce threshold, add paging
override:
  http/server/error-ratio:
    threshold_pct: 1
    action: pagerduty
```

### Document Override Rationale

```yaml
panels:
  - template: apollo
    type: bundle
    override:
      # Relaxed threshold: service handles batch uploads
      # which can take up to 30 seconds
      http/server/latency-p99:
        threshold_ms: 30000
```

### Align with SLOs

```yaml
# If SLO is 99.9% availability (0.1% error budget)
override:
  http/server/error-ratio:
    threshold_pct: 0.1
    action: pagerduty
```
