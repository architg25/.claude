# Custom Metrics

Patterns for adding custom Prometheus panels to MMA dashboards.

## Basic Custom Panel

**Use when**: Visualizing metrics not covered by bundles

```yaml
panels:
  - template: apollo
    type: bundle
  - template: custom
    type: panel
    name: cache-hit-rate
    title: "Cache Hit Rate"
    query: |
      sum(rate(cache_hits_total[5m])) /
      sum(rate(cache_requests_total[5m]))
    unit: percent
```

## Panel Types

### Time Series (Default)

```yaml
- template: custom
  type: panel
  name: request-rate
  title: "Request Rate"
  query: sum(rate(http_requests_total[5m]))
  unit: reqps
  visualization: timeseries
```

### Gauge

```yaml
- template: custom
  type: panel
  name: current-connections
  title: "Active Connections"
  query: sum(active_connections)
  unit: short
  visualization: gauge
  thresholds:
    - value: 0
      color: green
    - value: 80
      color: yellow
    - value: 100
      color: red
```

### Stat

```yaml
- template: custom
  type: panel
  name: total-users
  title: "Active Users (24h)"
  query: count(distinct(user_id))
  visualization: stat
  unit: short
```

### Table

```yaml
- template: custom
  type: panel
  name: top-endpoints
  title: "Top Endpoints by Latency"
  query: |
    topk(10,
      avg by (endpoint) (http_request_duration_seconds{quantile="0.99"})
    )
  visualization: table
  columns:
    - endpoint
    - value
```

## Query Patterns

### Rate Calculation

```yaml
# Requests per second
query: sum(rate(http_requests_total[5m]))

# Errors per second
query: sum(rate(http_requests_total{status=~"5.."}[5m]))
```

### Ratio/Percentage

```yaml
# Error rate percentage
query: |
  100 * sum(rate(http_requests_total{status=~"5.."}[5m])) /
        sum(rate(http_requests_total[5m]))
unit: percent
```

### Histogram Percentiles

```yaml
# P99 latency
query: |
  histogram_quantile(0.99,
    sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
  )
unit: seconds
```

### Aggregation by Label

```yaml
# Rate by endpoint
query: |
  sum by (endpoint) (rate(http_requests_total[5m]))
legend: "{{endpoint}}"
```

## Common Custom Metrics

### Cache Metrics

```yaml
- template: custom
  name: cache-hit-rate
  title: "Cache Hit Rate"
  query: |
    sum(rate(cache_hits_total[5m])) /
    sum(rate(cache_requests_total[5m])) * 100
  unit: percent
  thresholds:
    - value: 95
      color: green
    - value: 80
      color: yellow
    - value: 0
      color: red

- template: custom
  name: cache-latency
  title: "Cache Latency (P99)"
  query: |
    histogram_quantile(0.99,
      sum(rate(cache_operation_duration_seconds_bucket[5m])) by (le)
    )
  unit: seconds
```

### Database Metrics

```yaml
- template: custom
  name: db-connection-pool
  title: "DB Connection Pool"
  query: sum(db_pool_active_connections)
  unit: short

- template: custom
  name: db-query-latency
  title: "DB Query Latency (P99)"
  query: |
    histogram_quantile(0.99,
      sum(rate(db_query_duration_seconds_bucket[5m])) by (le)
    )
  unit: seconds
```

### Queue Metrics

```yaml
- template: custom
  name: queue-depth
  title: "Message Queue Depth"
  query: sum(pubsub_subscription_backlog)
  unit: short
  thresholds:
    - value: 0
      color: green
    - value: 1000
      color: yellow
    - value: 10000
      color: red

- template: custom
  name: queue-age
  title: "Oldest Unacked Message"
  query: max(pubsub_oldest_unacked_message_age_seconds)
  unit: seconds
```

### Business Metrics

```yaml
- template: custom
  name: active-users
  title: "Active Users (5m)"
  query: count(count by (user_id) (http_requests_total[5m]))
  unit: short

- template: custom
  name: revenue-rate
  title: "Transactions/min"
  query: sum(rate(transactions_total{status="success"}[5m])) * 60
  unit: short
```

## Custom Alerts

### Adding Alert to Custom Panel

```yaml
- template: custom
  name: cache-hit-rate
  title: "Cache Hit Rate"
  query: |
    sum(rate(cache_hits_total[5m])) /
    sum(rate(cache_requests_total[5m])) * 100
  alert:
    threshold: 90
    operator: lt  # Less than
    action: slack
    message: "Cache hit rate dropped below 90%"
```

### Multi-Threshold Alerts

```yaml
- template: custom
  name: queue-depth
  alerts:
    - name: queue-warning
      threshold: 1000
      action: slack
    - name: queue-critical
      threshold: 10000
      action: pagerduty
```

## Dashboard Organization

### Row Grouping

```yaml
rows:
  - name: "Application Metrics"
    panels:
      - template: apollo
        type: bundle

  - name: "Cache Metrics"
    collapsed: false
    panels:
      - template: custom
        name: cache-hit-rate
      - template: custom
        name: cache-latency

  - name: "Database Metrics"
    collapsed: true  # Collapsed by default
    panels:
      - template: custom
        name: db-connection-pool
```

## Best Practices

1. **Name panels descriptively** - Use lowercase-hyphenated names
2. **Include units** - Always specify `unit` for clarity
3. **Set appropriate thresholds** - Use colors to indicate health
4. **Use legends** - Add `legend` for multi-series queries
5. **Group related panels** - Use rows to organize
6. **Document queries** - Add comments for complex PromQL
