# Service Levels

Patterns for defining SLOs and SLIs using MMA.

## SLO/SLI Concepts

| Term | Definition | Example |
|------|------------|---------|
| **SLI** | Service Level Indicator | 99.5% of requests < 200ms |
| **SLO** | Service Level Objective | Target: 99.9% availability |
| **Error Budget** | Allowed failures | 0.1% of requests can fail |

## Basic SLO Configuration

### Availability SLO

**Use when**: Defining uptime targets

```yaml
service_levels:
  availability:
    target: 99.9
    window: 30d
    sli:
      type: availability
      good_events: successful_requests
      total_events: all_requests
```

### Latency SLO

**Use when**: Defining response time targets

```yaml
service_levels:
  latency:
    target: 99.0
    window: 30d
    sli:
      type: latency
      threshold_ms: 200
      percentile: 99
```

## SLI Types

### Request-Based SLIs

```yaml
sli:
  type: request_based
  good_events:
    query: |
      sum(rate(http_server_requests_total{status!~"5.."}[5m]))
  total_events:
    query: |
      sum(rate(http_server_requests_total[5m]))
```

### Latency-Based SLIs

```yaml
sli:
  type: latency
  query: |
    histogram_quantile(0.99,
      sum(rate(http_server_duration_seconds_bucket[5m])) by (le)
    )
  threshold_seconds: 0.2
```

### Throughput-Based SLIs

```yaml
sli:
  type: throughput
  query: |
    sum(rate(http_server_requests_total[5m]))
  minimum_rps: 100
```

## Error Budget Configuration

### Budget Calculation

```yaml
service_levels:
  api_availability:
    target: 99.9      # 99.9% target
    window: 30d       # Monthly window
    # Error budget = 100% - 99.9% = 0.1%
    # For 30 days = 43.2 minutes of downtime allowed
```

### Budget Alerts

```yaml
error_budget_alerts:
  - name: budget-warning
    threshold_pct: 50  # Alert at 50% budget consumed
    action: slack

  - name: budget-critical
    threshold_pct: 80  # Alert at 80% budget consumed
    action: pagerduty
```

### Budget Burn Rate

```yaml
burn_rate_alerts:
  - name: fast-burn
    rate: 14.4  # Consuming 14.4x normal rate
    window: 1h
    action: pagerduty

  - name: slow-burn
    rate: 1.5   # Consuming 1.5x normal rate
    window: 24h
    action: slack
```

## Multi-Tier SLOs

### By Endpoint Criticality

```yaml
service_levels:
  critical_endpoints:
    target: 99.99
    filter:
      endpoint: "/api/v1/checkout"
    sli:
      type: availability

  standard_endpoints:
    target: 99.9
    filter:
      endpoint: "/api/v1/*"
    sli:
      type: availability
```

### By Customer Tier

```yaml
service_levels:
  premium_users:
    target: 99.99
    filter:
      user_tier: premium
    sli:
      type: latency
      threshold_ms: 100

  standard_users:
    target: 99.9
    filter:
      user_tier: standard
    sli:
      type: latency
      threshold_ms: 500
```

## Dashboard Integration

### SLO Dashboard Panel

```yaml
panels:
  - template: slo-dashboard
    type: custom
    config:
      slos:
        - name: availability
          target: 99.9
        - name: latency
          target: 99.0
```

### Error Budget Timeline

```yaml
panels:
  - template: error-budget-timeline
    type: custom
    time_range: 30d
```

## Common SLO Patterns

### Standard Web Service

```yaml
service_levels:
  availability:
    target: 99.9
    window: 30d
    sli:
      type: availability
      good_events: http_status < 500

  latency_p99:
    target: 99.0
    window: 30d
    sli:
      type: latency
      threshold_ms: 500
      percentile: 99
```

### Critical Infrastructure

```yaml
service_levels:
  availability:
    target: 99.99  # Four nines
    window: 30d

  latency_p99:
    target: 99.9
    sli:
      threshold_ms: 100
```

### Background Processing

```yaml
service_levels:
  completion_rate:
    target: 99.5
    window: 7d
    sli:
      type: job_success
      good_events: completed_jobs
      total_events: submitted_jobs

  processing_time:
    target: 95.0
    window: 7d
    sli:
      type: duration
      threshold_minutes: 30
```

## SLO Review Process

### Monthly Review Checklist

1. Calculate actual SLI performance
2. Compare against SLO target
3. Review error budget consumption
4. Identify top causes of budget burn
5. Plan reliability improvements

### Adjusting SLOs

```yaml
# Start conservative, tighten over time
# Month 1
target: 99.0

# Month 3 (after improvements)
target: 99.5

# Month 6 (mature service)
target: 99.9
```

## Best Practices

1. **Start with 99.9 or lower** - 99.99 is very hard to achieve
2. **Use 30-day windows** - Aligns with monthly reporting
3. **Include error budget alerts** - Know when budget is depleting
4. **Focus on user-facing metrics** - SLIs should reflect user experience
5. **Review and adjust** - SLOs should evolve with the service
