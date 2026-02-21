# Runtime Patterns

Patterns for configuring Spotify's Runtime CRD. Runtime is the **first resource** you need for any new service - it creates namespaces, resource quotas, and service accounts.

## Basic Runtime

**Use when**: Creating a new service with default settings

```yaml
apiVersion: runtime.spotify.com/v1alpha1
kind: Runtime
metadata:
  name: my-service
  namespace: my-gcp-project
spec:
  owners:
    - my-team@iam.spotify.com
```

**Key fields:**
- `name` - Must match your service name
- `namespace` - Must match your GCP project
- `owners` - IAM group for ownership (use groups, not individuals)

## Runtime with Resource Quotas

**Use when**: Service has specific resource requirements

```yaml
apiVersion: runtime.spotify.com/v1alpha1
kind: Runtime
metadata:
  name: my-service
  namespace: my-gcp-project
spec:
  owners:
    - my-team@iam.spotify.com
  resourceQuota:
    hard:
      limits.cpu: '96'
      limits.memory: 360Gi
      requests.cpu: '48'
      requests.memory: 180Gi
```

### Resource Quota Sizing Guide

| Service Type | CPU Requests | Memory Requests | CPU Limits | Memory Limits |
|-------------|--------------|-----------------|------------|---------------|
| Small | 48 | 180Gi | 96 | 360Gi |
| Medium | 96 | 360Gi | 192 | 720Gi |
| Large | 400 | 500Gi | 800 | 1000Gi |
| ML/Data Heavy | 600+ | 1000Gi+ | 1200+ | 2000Gi+ |

## Salem-Type Runtime

**Use when**: Deploying ML models via Salem

```yaml
apiVersion: runtime.spotify.com/v1alpha1
kind: Runtime
metadata:
  name: my-ml-service
  namespace: my-gcp-project
spec:
  type: salem
  serviceAccount: my-ml-service@gke-accounts.iam.gserviceaccount.com
  owners:
    - my-team@iam.spotify.com
    - salem@iam.spotify.com  # Required for Salem services
```

**Important**: Salem services must include `salem@iam.spotify.com` as an owner.

## Role-Based Runtime

**Use when**: Service needs specific role configurations

```yaml
apiVersion: runtime.spotify.com/v1alpha1
kind: Runtime
metadata:
  name: my-service
  namespace: my-gcp-project
spec:
  roles:
    - my-service-staging
    - my-service-production
  owners:
    - my-team@iam.spotify.com
```

## Multi-Environment Runtime

**Use when**: Separate quotas for staging and production

**File**: `kubernetes/gcp-resources/staging/runtime.yaml`
```yaml
apiVersion: runtime.spotify.com/v1alpha1
kind: Runtime
metadata:
  name: my-service-staging
  namespace: my-gcp-project-staging
spec:
  owners:
    - my-team@iam.spotify.com
  resourceQuota:
    hard:
      requests.cpu: '24'
      requests.memory: 90Gi
```

**File**: `kubernetes/gcp-resources/production/runtime.yaml`
```yaml
apiVersion: runtime.spotify.com/v1alpha1
kind: Runtime
metadata:
  name: my-service
  namespace: my-gcp-project
spec:
  owners:
    - my-team@iam.spotify.com
  resourceQuota:
    hard:
      requests.cpu: '96'
      requests.memory: 360Gi
```

## Common Mistakes

### Mistake 1: Name/Namespace Mismatch
```yaml
# WRONG - name doesn't match namespace
metadata:
  name: my-service
  namespace: different-project  # Should match!
```

### Mistake 2: Setting Quotas Below Defaults
```yaml
# WRONG - creates obsolete config
resourceQuota:
  hard:
    requests.cpu: '2'  # Below default, will be ignored
```

### Mistake 3: Using Individual Users Instead of Groups
```yaml
# WRONG - use groups instead
spec:
  owners:
    - john.doe@spotify.com  # Use IAM groups!

# CORRECT
spec:
  owners:
    - my-team@iam.spotify.com
```

### Mistake 4: Missing Salem Owner
```yaml
# WRONG - Salem services need salem owner
spec:
  type: salem
  owners:
    - my-team@iam.spotify.com
    # Missing: salem@iam.spotify.com
```

## What Runtime Manages

Runtime CRD automatically creates and manages:
- Namespaces on workload clusters
- ResourceQuotas
- ServiceAccounts
- RBACSyncConfig
- SecretStores

## Validation

```bash
# Check Runtime status
kubectl get runtime my-service -n my-gcp-project

# Describe for events
kubectl describe runtime my-service -n my-gcp-project

# Verify namespace was created
kubectl get namespace my-gcp-project
```

## Documentation Links

- [Runtime Operator Docs](https://backstage.spotify.net/docs/default/component/runtime-operator/)
- [Runtime Examples](https://backstage.spotify.net/docs/default/component/runtime-operator/users/examples/)
