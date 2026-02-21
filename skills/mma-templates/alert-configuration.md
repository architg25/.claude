# Alert Configuration

Patterns for configuring MMA alerts and notifications.

## Alert Actions

### Available Actions

| Action | Destination | Urgency |
|--------|-------------|---------|
| `no_action` | None (dashboard only) | Informational |
| `slack` | Slack channel | Low |
| `pagerduty` | PagerDuty service | High |

### PagerDuty Setup

**Use when**: Critical alerts requiring immediate response

```yaml
override:
  http/server/error-ratio:
    threshold_pct: 1
    action: pagerduty
```

**Prerequisites**:
- PagerDuty service configured in Backstage
- On-call schedule defined
- Escalation policy set

### Slack Notification

**Use when**: Non-urgent alerts for awareness

```yaml
override:
  http/server/latency-p99:
    threshold_ms: 500
    action: slack
    slack_channel: "#my-team-alerts"
```

## Severity Levels

### Critical (Page)

```yaml
override:
  http/server/error-ratio:
    threshold_pct: 5
    action: pagerduty
    severity: critical
```

**Use for**:
- Complete service outage
- Data loss risk
- Security incidents

### Warning (Slack)

```yaml
override:
  http/server/latency-p99:
    threshold_ms: 500
    action: slack
    severity: warning
```

**Use for**:
- Degraded performance
- Approaching limits
- Non-blocking issues

### Info (Dashboard)

```yaml
override:
  http/server/request-rate:
    action: no_action
    severity: info
```

**Use for**:
- Trend monitoring
- Capacity planning
- Debugging context

## Alert Timing

### Window Configuration

```yaml
override:
  http/server/error-ratio:
    threshold_pct: 1
    window: 5m       # Evaluate over 5 minutes
    for: 2m          # Must be true for 2 minutes
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `window` | 5m | Aggregation period |
| `for` | 1m | Persistence requirement |

### Reducing False Positives

```yaml
# Transient spikes OK, sustained issues alert
override:
  http/server/latency-p99:
    threshold_ms: 200
    window: 5m    # Average over 5 minutes
    for: 5m       # Must persist for 5 minutes
```

### Fast Detection

```yaml
# Critical issue, alert quickly
override:
  http/server/error-ratio:
    threshold_pct: 50
    window: 1m
    for: 0m  # Immediate
    action: pagerduty
```

## Multi-Condition Alerts

### AND Conditions

**Use when**: Alert only when multiple conditions met

```yaml
# Alert only if both latency AND error rate are high
alerts:
  - name: service-degraded
    conditions:
      - metric: http/server/latency-p99
        threshold_ms: 500
      - metric: http/server/error-ratio
        threshold_pct: 1
    action: pagerduty
```

### OR Conditions (Separate Alerts)

```yaml
# Either condition triggers independently
override:
  http/server/latency-p99:
    threshold_ms: 1000
    action: pagerduty
  http/server/error-ratio:
    threshold_pct: 5
    action: pagerduty
```

## Alert Annotations

### Runbook Links

```yaml
override:
  http/server/error-ratio:
    threshold_pct: 1
    action: pagerduty
    annotations:
      runbook: "https://backstage.spotify.net/docs/component/my-service/runbooks/high-error-rate"
```

### Context Information

```yaml
override:
  http/server/error-ratio:
    threshold_pct: 1
    action: pagerduty
    annotations:
      summary: "Error rate exceeded 1%"
      description: "Check logs for error details. Common causes: DB timeouts, upstream failures."
      dashboard: "https://grafana.spotify.net/d/my-service"
```

## Alert Grouping

### By Service

```yaml
alert_grouping:
  group_by: [service]
  group_wait: 30s
  group_interval: 5m
```

### By Endpoint

```yaml
alert_grouping:
  group_by: [service, endpoint]
  group_wait: 30s
```

## Silencing and Maintenance

### Scheduled Silence

```yaml
# Silence during maintenance window
maintenance:
  schedule:
    - start: "2024-01-15T02:00:00Z"
      end: "2024-01-15T04:00:00Z"
      comment: "Planned deployment"
```

### Deployment Silence

Alerts are automatically silenced during deployments when using standard CI/CD pipelines.

## Alert Hierarchy

### Recommended Structure

```yaml
# Critical: Pages on-call
override:
  http/server/error-ratio:
    threshold_pct: 5
    action: pagerduty
    severity: critical

# Warning: Slack notification
  http/server/error-ratio-warning:
    threshold_pct: 1
    action: slack
    severity: warning

# Info: Dashboard only
  http/server/error-ratio-info:
    threshold_pct: 0.5
    action: no_action
    severity: info
```

## Testing Alerts

### Dry Run

```bash
# Validate alert configuration
mma validate --config monitoring-info.yaml

# Preview generated alerts
mma preview --config monitoring-info.yaml --output alerts.yaml
```

### Alert Testing

```bash
# Trigger test alert
mma test-alert --alert http/server/error-ratio --config monitoring-info.yaml
```

## Best Practices

1. **Start with fewer alerts** - Add more as you understand the system
2. **Include runbooks** - Every PagerDuty alert needs a runbook link
3. **Review regularly** - Remove noisy or unused alerts
4. **Use appropriate severity** - Not everything needs to page
5. **Test during business hours** - Verify alerts work before they're needed at 3 AM
