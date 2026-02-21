# PDB Patterns

Patterns for Pod Disruption Budgets to ensure high availability.

## Basic PDB

**Use when**: Standard HA requirements

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-service
  namespace: my-namespace
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: my-service
```

## minAvailable vs maxUnavailable

### minAvailable (Recommended)
Guarantees minimum pods running:
```yaml
spec:
  minAvailable: 2  # At least 2 pods always running
```

### maxUnavailable
Limits how many can be down:
```yaml
spec:
  maxUnavailable: 1  # At most 1 pod down at a time
```

## Percentage-Based PDB

**Use when**: Variable replica counts

```yaml
spec:
  minAvailable: 50%  # At least half always running
```

## Recommendations by Replica Count

| Replicas | minAvailable | Rationale |
|----------|--------------|-----------|
| 3 | 2 | One pod can be disrupted |
| 5 | 3 | Two pods can be disrupted |
| 10 | 7 | 30% can be disrupted |
| 20+ | 70% | Use percentage |

## Critical Service PDB

**Use when**: Zero tolerance for outages

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: critical-service
  namespace: my-namespace
spec:
  maxUnavailable: 0  # No disruptions allowed
  selector:
    matchLabels:
      app: critical-service
```

**Warning**: This blocks node drains and upgrades. Use sparingly.

## Best Practices

1. **Always create a PDB** for production services
2. **Use minAvailable** rather than maxUnavailable
3. **Don't set too restrictive** - blocks cluster maintenance
4. **Match selector** to Deployment labels exactly
