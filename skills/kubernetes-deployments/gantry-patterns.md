# Gantry Patterns

Gantry is Spotify's next-generation deployment platform replacing Tugboat/Kustomize. It follows a "convention over configuration" philosophy with a single `gantry.yaml` file.

> **Important**: New services should use Gantry. Migration deadline: Spring 2026.

## Basic gantry.yaml

**Use when**: Creating a new service

```yaml
apiVersion: gantry.spotify.com/v1alpha1
kind: Service
metadata:
  name: my-service
  namespace: my-gcp-project
spec:
  softwareCatalogEntity: component:default/my-service
  image: gcr.io/my-gcp-project/my-service
  runtimeRef:
    name: my-service
```

**That's it!** Gantry handles:
- Deployment configuration
- Service creation
- HPA setup (min: 2, max: 300)
- Rolling updates
- Health checks

## Full Configuration

```yaml
apiVersion: gantry.spotify.com/v1alpha1
kind: Service
metadata:
  name: my-service
  namespace: my-gcp-project
spec:
  # Required fields
  softwareCatalogEntity: component:default/my-service
  image: gcr.io/my-gcp-project/my-service
  runtimeRef:
    name: my-service

  # Regions (defaults: us-central1, europe-west1, asia-east1)
  regions:
    - us-central1
    - europe-west1
    - asia-east1
    - us-east1
    - europe-west4

  # Environment variables
  env:
    - name: LOG_LEVEL
      value: INFO
    - name: JVM_ARGS
      value: -XX:MaxRAMPercentage=80.0 -Djava.net.preferIPv6Addresses=true

  # Networking
  networking:
    http:
      enabled: true
      healthCheckPath: /health
    grpc:
      enabled: true
    hm:
      enabled: true
      snoopPort: 5701
    probeType: http

  # Resource sizing (T-shirt sizes)
  scaling:
    resourceSizing:
      memorySize: M
      cpuSize: M

  # Secrets from Google Secret Manager
  secretRefs:
    - gcpProjectId: my-gcp-project
      secrets:
        - gsmKey: database-password
          envVar: DB_PASSWORD
        - gsmKey: service-account
          envVar: SERVICE_ACCOUNT_JSON
          path: /var/secrets/google/service-account.json
```

## Key Differences from Kustomize

| Kustomize | Gantry |
|-----------|--------|
| Multiple YAML files | Single gantry.yaml |
| deployment.yaml, service.yaml, hpa.yaml | All-in-one |
| Raw CPU/memory specs | T-shirt sizes (S/M/L/XL) |
| Custom ports | Fixed ports (5990/8080/5700) |
| Manual HPA config | Automatic autoscaling |
| Environment overlays | Single file for all |

## T-Shirt Sizing

Instead of raw Kubernetes resources:

```yaml
scaling:
  resourceSizing:
    memorySize: M   # Options: XS, S, M, L, XL, XXL
    cpuSize: M
```

| Size | Approximate Resources |
|------|----------------------|
| XS | 0.5 CPU, 1Gi memory |
| S | 1 CPU, 2Gi memory |
| M | 2 CPU, 4Gi memory |
| L | 4 CPU, 8Gi memory |
| XL | 8 CPU, 16Gi memory |
| XXL | 16 CPU, 32Gi memory |

## Secret Management

### Environment Variable Secret
```yaml
secretRefs:
  - gcpProjectId: my-gcp-project
    secrets:
      - gsmKey: my-secret-key
        envVar: MY_SECRET
```

### File-Based Secret
```yaml
secretRefs:
  - gcpProjectId: my-gcp-project
    secrets:
      - gsmKey: service-account-json
        envVar: SA_JSON
        path: /var/secrets/google/sa.json
```

## Networking Configuration

### Fixed Ports (Cannot Change)
| Protocol | Port |
|----------|------|
| gRPC | 5990 |
| HTTP | 8080 |
| Hermes (hm) | 5700 |

### Enable/Disable Protocols
```yaml
networking:
  http:
    enabled: true
    healthCheckPath: /healthz
  grpc:
    enabled: false  # Disable if not using gRPC
  hm:
    enabled: true
```

## Migration from Kustomize

### Step 1: Create gantry.yaml
Place in `kubernetes/` directory alongside existing files.

### Step 2: Map Configuration

**From deployment.yaml:**
| deployment.yaml | gantry.yaml |
|-----------------|-------------|
| `env:` | `spec.env` |
| `resources:` | `spec.scaling.resourceSizing` |
| `ports:` | `spec.networking` |

**From service.yaml:**
- Automatically configured based on `spec.networking`

**From hpa.yaml:**
- Automatic. Override with gantryctl if needed.

### Step 3: Update BUILD.bazel
```python
# Replace deployment() with image_push()
image_push(
    name = "push-image",
    image = ":image",
    registry = "gcr.io",
    repository = "my-gcp-project/my-service",
)

# Add gantry.yaml to resources
resources(
    name = "k8s",
    srcs = ["gantry.yaml", "runtime.yaml"],
)
```

### Step 4: Remove Old Files
Delete:
- deployment.yaml
- service.yaml
- hpa.yaml
- deployment-info.yaml
- Kustomize overlays

### Step 5: Validate
```bash
# Check service status
bazel run //gantry/gantryctl -- get service my-gcp-project my-service

# Verify deployment
kubectl site my-service
kubectl get gservice -n my-namespace
```

## gantryctl Commands

```bash
# Service management
bazel run //gantry/gantryctl -- get service <project> <service>
bazel run //gantry/gantryctl -- describe service <project> <service>
bazel run //gantry/gantryctl -- status <project> <service>

# Scaling configuration
bazel run //gantry/gantryctl -- set scalingpolicy <project> <service> \
  --min=2 --max=300 --cpu=80

# Pinning (prevent updates)
bazel run //gantry/gantryctl -- pin <project> <service> <pin-name>
bazel run //gantry/gantryctl -- unpin <project> <service>

# Debugging
bazel run //gantry/gantryctl -- get image <image-uri> -v
```

## Common Issues

### Service Stuck in ContainerCreating
- Check for lingering Tugboat pods
- Verify Runtime exists and is healthy
- Check secret configuration

### Secret Names with Dashes
```yaml
# Problem: "my-secret-key" interpreted as subtraction
# Solution: Use index function in complex secrets
{{ mustToJson (index . "my-secret-key") }}
```

### Health Checks Failing
- Ensure `healthCheckPath` matches your endpoint
- Verify ports use fixed values (8080 for HTTP)

### Service Not in Backstage
- Verify `softwareCatalogEntity` matches exactly
- Check GCP project annotation alignment

## Deprecated Features

For temporary migration support only:
```yaml
spec:
  deprecatedFeatures:
    - complexSecrets  # For ExternalSecret templates
    - ffwd           # For FFWD metrics
```

## Documentation Links

- [Gantry Docs](https://backstage.spotify.net/docs/default/component/gantry-docs/)
- [Migration Guide](https://backstage.spotify.net/docs/default/component/gantry-docs/migration/)
- Support: #deployments-support
