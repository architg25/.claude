# Setup Patterns

Patterns for configuring Locus Kubernetes resources.

## Basic Locus Resource

**Use when**: Creating a new Locus cache cluster

```yaml
apiVersion: caching.spotify.com/v1alpha3
kind: Locus
metadata:
  name: my-service-locus
  namespace: my-namespace
  labels:
    app.kubernetes.io/name: my-service-locus
    app.kubernetes.io/component: cache
spec:
  regions:
    - europe-west1
    - us-central1
  numShards: 3
  podSpec:
    cpu: 2
    memorySizeGb: 16
  warmupEnabled: true
  authEnabled: true
  allowedAccounts:
    - my-service@gke-accounts.iam.gserviceaccount.com
```

**Key fields:**
- `regions` - Deploy to multiple regions for high availability
- `numShards` - Number of cache shards (affects parallelism)
- `podSpec` - Resource allocation per shard
- `authEnabled` - Always enable for production

## Sizing Guidelines

### Memory Sizing

| Use Case | Memory per Shard | Shards | Total |
|----------|------------------|--------|-------|
| Small (metadata) | 4 GB | 2 | 8 GB |
| Medium (session data) | 16 GB | 3 | 48 GB |
| Large (ML features) | 32 GB | 5 | 160 GB |

### CPU Sizing

| QPS Target | CPU per Shard |
|------------|---------------|
| < 10K | 1 |
| 10K - 50K | 2 |
| 50K - 100K | 4 |
| > 100K | 4+ (add shards) |

## Region Selection

### Single Region (Non-critical)

**Use when**: Development or non-production workloads

```yaml
spec:
  regions:
    - europe-west1
```

### Multi-Region (Production)

**Use when**: High availability requirements

```yaml
spec:
  regions:
    - europe-west1    # Primary
    - europe-west4    # Backup EU
    - us-central1     # US presence
```

**Benefits:**
- Automatic failover
- Lower latency for multi-region services
- Increased fault tolerance

## Authentication Setup

### Enable Auth (Required for Production)

```yaml
spec:
  authEnabled: true
  allowedAccounts:
    - my-service@gke-accounts.iam.gserviceaccount.com
    - my-batch-job@gke-accounts.iam.gserviceaccount.com
```

### Service Account Patterns

```yaml
# Single service
allowedAccounts:
  - my-service@gke-accounts.iam.gserviceaccount.com

# Shared by team
allowedAccounts:
  - my-team-services@gke-accounts.iam.gserviceaccount.com

# Multiple services
allowedAccounts:
  - service-a@gke-accounts.iam.gserviceaccount.com
  - service-b@gke-accounts.iam.gserviceaccount.com
```

## Warmup Configuration

### Enable Warmup

**Use when**: Cache needs to be pre-populated on startup

```yaml
spec:
  warmupEnabled: true
```

**Benefits:**
- Reduces cold-start latency
- Prevents thundering herd on deployments
- Copies data from existing shards

### Disable Warmup

**Use when**: Fresh cache is acceptable

```yaml
spec:
  warmupEnabled: false
```

## Resource Labels

### Standard Labels

```yaml
metadata:
  labels:
    app.kubernetes.io/name: my-service-locus
    app.kubernetes.io/component: cache
    app.kubernetes.io/managed-by: team-name
    squad: my-squad
```

## Environment-Specific Config

### Development

```yaml
spec:
  regions: [europe-west1]
  numShards: 1
  podSpec:
    cpu: 1
    memorySizeGb: 4
  authEnabled: false  # OK for dev only
```

### Staging

```yaml
spec:
  regions: [europe-west1]
  numShards: 2
  podSpec:
    cpu: 2
    memorySizeGb: 8
  authEnabled: true
```

### Production

```yaml
spec:
  regions: [europe-west1, europe-west4, us-central1]
  numShards: 3
  podSpec:
    cpu: 2
    memorySizeGb: 16
  warmupEnabled: true
  authEnabled: true
```

## Deployment Workflow

1. **Create resource file**: `locus/my-service-locus.yaml`
2. **Apply to cluster**: `kubectl apply -f locus/my-service-locus.yaml`
3. **Wait for readiness**: `kubectl get locus my-service-locus -w`
4. **Verify endpoints**: Check service discovery

## Validation

### Pre-Deployment Checks

```bash
# Validate YAML syntax
kubectl apply --dry-run=client -f locus/my-service-locus.yaml

# Check namespace exists
kubectl get namespace my-namespace

# Verify service account
kubectl get serviceaccount my-service -n my-namespace
```

### Post-Deployment Checks

```bash
# Check Locus status
kubectl get locus my-service-locus -n my-namespace

# View events
kubectl describe locus my-service-locus -n my-namespace

# Check pod health
kubectl get pods -l app.kubernetes.io/name=my-service-locus -n my-namespace
```
