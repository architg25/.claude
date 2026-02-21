---
name: mma-templates
description: MMA (Manage Monitoring and Alerting) patterns for Grafana dashboards and alerts. Covers bundle selection, panel customization, alert configuration, and service levels. Use when setting up monitoring for services.
allowed-tools:
  - Read
---

# MMA Templates Patterns

Patterns for configuring monitoring dashboards and alerts using MMA.

## Pattern Categories

- **[Bundle Selection](bundle-selection.md)**: Choosing the right bundle (apollo, k8s, grpc, pubsub)
- **[Panel Customization](panel-customization.md)**: Overriding panel defaults, thresholds
- **[Alert Configuration](alert-configuration.md)**: PagerDuty integration, severity levels
- **[Service Levels](service-levels.md)**: SLO/SLI definitions
- **[Custom Metrics](custom-metrics.md)**: Custom Prometheus panels

## Quick Reference

### Basic Configuration
```yaml
metadata:
  schemaVersion: 5
components:
  my-service:
    - service_info: service-info.yaml
      panels:
        - template: apollo
          type: bundle
```

### Bundle Selection
| Service Type | Bundle | What You Get |
|--------------|--------|--------------|
| Apollo HTTP/gRPC | `apollo` | Request rate, latency, errors |
| Kubernetes workloads | `k8s` | CPU, memory, restarts |
| gRPC-only services | `grpc` | gRPC-specific metrics |
| Pub/Sub consumers | `pubsub` | Message rates, lag |

### Alert Override Example
```yaml
override:
  grpc/server/rpc-error-ratio:
    threshold_pct: 1
    action: pagerduty
```

## Critical Constraints

- **Never** set alert thresholds too low (causes alert fatigue)
- **Always** use `service_info: service-info.yaml` reference
- **Always** start with a bundle before adding custom panels

## Related Skills

- [locus-caching](../locus-caching/SKILL.md) - Add cache hit rate monitoring
- [decibel](../decibel/SKILL.md) - Add database latency monitoring
- [kubernetes-deployments](../kubernetes-deployments/SKILL.md) - Kubernetes deployment patterns for services being monitored

## Documentation Links

- [Main Docs](https://backstage.spotify.net/docs/default/component/mma-docs/)
- [Getting Started](https://backstage.spotify.net/docs/default/component/mma-docs/getting-started/)
- [Core Templates Repo](https://ghe.spotify.net/monitoring/mma-core-templates-prom)

## Support Channels

- #mma-support - Main support channel
