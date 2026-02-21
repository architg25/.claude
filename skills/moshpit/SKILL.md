---
name: moshpit
description: Moshpit load testing patterns for performance testing services. Covers HTTP/gRPC configuration, data sources, and result analysis. Use when setting up load tests for services. Note: Moshpit is community-maintained as of 2025.
allowed-tools:
  - Read
---

# Moshpit Load Testing Patterns

Patterns for Spotify's configuration-driven load testing framework.

## Pattern Categories

- **[Configuration Patterns](configuration-patterns.md)**: YAML configuration structure
- **[HTTP Testing](http-testing.md)**: HTTP API load testing
- **[gRPC Testing](grpc-testing.md)**: gRPC service testing
- **[Data Sources](data-sources.md)**: BigQuery/GCS data loading
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Quick Reference

### Basic Configuration
```yaml
namespace: 'my-service-load-test'
targets:
  - name: 'API Load Test'
    target_id: 'api_load_test'
    requests_per_second: 100
    duration_seconds: 300
    base_service_uri: 'http://my-service'
    source:
      http:
        - path: '/api/endpoint'
          method: 'GET'
```

### Load Test Sizing
| Test Type | RPS | Duration | Ramp Up |
|-----------|-----|----------|---------|
| Smoke test | 10 | 60s | 10s |
| Load test | 100 | 300s | 60s |
| Stress test | 500+ | 600s | 120s |

## Critical Constraints

- **Never** run load tests against production without approval
- **Always** use ramp-up to avoid cold-start failures
- **Always** set realistic response time estimates

## Related Skills

- [mma-templates](../mma-templates/SKILL.md) - Monitor service during load tests

## Documentation Links

- [Main Docs](https://backstage.spotify.net/docs/default/system/moshpit-load-testing/)
- [Getting Started](https://backstage.spotify.net/docs/default/system/moshpit-load-testing/getting-started/)

## Support Channels

- #moshpit-users - Community support (inner-sourced)
