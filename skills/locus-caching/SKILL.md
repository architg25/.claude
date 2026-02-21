---
name: locus-caching
description: Locus managed caching patterns for Memcached at Spotify. Covers Kubernetes setup, Java client configuration, multilevel caching (Caffeine + Locus), and migration patterns. Use when implementing caching for high-read workloads.
allowed-tools:
  - Read
---

# Locus Caching Patterns

Patterns for Spotify's managed distributed caching solution built on Memcached.

## Pattern Categories

- **[Setup Patterns](setup-patterns.md)**: Kubernetes Locus resource configuration
- **[Java Client](java-client.md)**: Client configuration, connection pooling
- **[Multilevel Cache](multilevel-cache.md)**: Caffeine local cache + Locus patterns
- **[Migration Patterns](migration-patterns.md)**: Migrating from other cache solutions
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Quick Reference

### Kubernetes Resource
```yaml
apiVersion: caching.spotify.com/v1alpha3
kind: Locus
metadata:
  name: my-service-locus
spec:
  regions: [europe-west1, us-central1]
  numShards: 3
  podSpec:
    cpu: 2
    memorySizeGb: 16
  authEnabled: true
```

### Java Client Config
```hocon
memcached.locus {
  projectId: "my-project"
  name: "my-service-locus"
  max-outstanding-requests: 20000
}
```

### When to Use Locus
| Scenario | Recommendation |
|----------|----------------|
| Read-heavy (>98% hit rate expected) | Use Locus |
| Session/metadata caching | Use Locus |
| Sub-millisecond latency required | Use local Caffeine only |
| Write-heavy workload | Consider Decibel instead |

## Critical Constraints

- **Never** store PII without Padlock encryption
- **Always** enable auth for production clusters
- **Always** use multilevel cache for latency-sensitive paths
- **Always** set appropriate TTLs to prevent stale data

## Related Skills

- [decibel](../decibel/SKILL.md) - Persistent storage behind the cache
- [mma-templates](../mma-templates/SKILL.md) - Monitoring cache hit rates
- [kubernetes-deployments](../kubernetes-deployments/SKILL.md) - Standard Kubernetes deployment patterns
- [apollo-configuration](../apollo-configuration/SKILL.md) - HOCON configuration for Apollo services

## Documentation Links

- [Main Docs](https://backstage.spotify.net/docs/default/component/locus/)
- [Getting Started](https://backstage.spotify.net/docs/default/component/locus/getting-started/)
- [Java Client](https://backstage.spotify.net/docs/default/system/locus/using-locus-from-java/)

## Support Channels

- #cache-users - Main support channel
