# Kustomize Patterns

Patterns for Kustomize-based Kubernetes configurations.

> **Note**: Kustomize is the current standard, but **Gantry is the future**.
> New services should use Gantry. See [Gantry Patterns](gantry-patterns.md).

## Directory Structure

### Standard Layout
```
kubernetes/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
└── environments/
    ├── production/
    │   └── kustomization.yaml
    └── staging/
        └── kustomization.yaml
```

### With Runtime
```
kubernetes/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── gcp-resources/
│   └── runtime.yaml
└── environments/
    ├── production/
    │   └── kustomization.yaml
    └── staging/
        └── kustomization.yaml
```

## Base kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
  - hpa.yaml
  - pdb.yaml

commonLabels:
  app: my-service
```

## Environment Overlay

### Production
```yaml
# kubernetes/environments/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namespace: my-gcp-project

patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
    target:
      kind: Deployment
      name: my-service
```

### Staging
```yaml
# kubernetes/environments/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namespace: my-gcp-project-staging

patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 2
    target:
      kind: Deployment
      name: my-service
```

## Common Patches

### Replica Count
```yaml
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 10
    target:
      kind: Deployment
```

### Resource Requests
```yaml
patches:
  - patch: |-
      - op: replace
        path: /spec/template/spec/containers/0/resources/requests/cpu
        value: "8"
    target:
      kind: Deployment
```

### Environment Variable
```yaml
patches:
  - patch: |-
      - op: add
        path: /spec/template/spec/containers/0/env/-
        value:
          name: ENVIRONMENT
          value: production
    target:
      kind: Deployment
```

## Build and Apply

```bash
# Preview rendered manifests
kubectl kustomize kubernetes/environments/production

# Apply to cluster
kubectl apply -k kubernetes/environments/production

# Dry run
kubectl apply -k kubernetes/environments/production --dry-run=client
```

## Migration to Gantry

Services using Kustomize are blocked from Gantry migration until converted.
See [Gantry Patterns](gantry-patterns.md) for migration instructions.
