# Deployment Patterns

Patterns for configuring Kubernetes Deployments for Apollo services.

## Basic Deployment

**Use when**: Creating a standard Apollo service deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
  namespace: my-namespace
  labels:
    app: my-service
    role: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
  template:
    metadata:
      labels:
        app: my-service
      annotations:
        apollo.prometheus.spotify.net/scrape: "true"
        podpreset.admission.spotify.com/exclude: "observability"
    spec:
      containers:
        - name: my-service
          image: $DEPLOYMENT_IMAGE
          ports:
            - name: grpc
              containerPort: 5990
            - name: http
              containerPort: 8080
            - name: hm
              containerPort: 5700
            - name: hm-snoop
              containerPort: 5701
          resources:
            requests:
              cpu: "4"
              memory: "8Gi"
            limits:
              cpu: "6"
              memory: "8Gi"
          readinessProbe:
            httpGet:
              path: /readiness
              port: 5700
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /liveness
              port: 5700
            initialDelaySeconds: 30
            periodSeconds: 10
          lifecycle:
            preStop:
              exec:
                command: ["sleep", "15"]
```

## Resource Sizing

### Starting Values
| Setting | Value | Notes |
|---------|-------|-------|
| CPU Request | 4 cores | Adjust based on actual usage |
| CPU Limit | 6 cores | 1.5x request typical |
| Memory Request | 8Gi | Set equal to limit |
| Memory Limit | 8Gi | Prevents OOM surprises |

### Sizing Guidelines
- **Memory ratio**: 1:4 vCPU:GiB recommended
- **Max pod size**: ≤15 cores (scheduling constraints)
- **Memory request = limit**: Always (prevents OOM kills)

### T-Shirt Sizes (for reference)
| Size | CPU Request | Memory |
|------|-------------|--------|
| Small | 1-2 | 2-4Gi |
| Medium | 4 | 8Gi |
| Large | 8 | 16Gi |
| XLarge | 16 | 32Gi |

## Probe Configuration

### Readiness Probe
Controls when pod receives traffic:
```yaml
readinessProbe:
  httpGet:
    path: /readiness
    port: 5700
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

### Liveness Probe
Controls when pod gets restarted:
```yaml
livenessProbe:
  httpGet:
    path: /liveness
    port: 5700
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
```

### Startup Probe
For slow-starting applications:
```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 5700
  initialDelaySeconds: 0
  periodSeconds: 10
  failureThreshold: 30  # 5 minutes to start
```

### Probe Best Practices
- Use separate `/readiness` and `/liveness` endpoints
- Keep probe checks lightweight
- Set `initialDelaySeconds` based on actual startup time
- Use startup probe for apps that take >30s to initialize

## Rolling Update Strategy

### Standard (Recommended)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 25%
```

### Conservative (Zero Downtime)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

### Fast (Development)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 50%
    maxUnavailable: 50%
```

## Lifecycle Hooks

### PreStop Hook (Zero-Downtime)
```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "15"]
```

**Why 15 seconds?** Allows in-flight requests to complete and load balancers to drain connections.

## Labels and Annotations

### Standard Labels
```yaml
labels:
  app: my-service
  role: api  # or: worker, batch, ml
  environment: production
  squad: my-squad
```

### Common Annotations
```yaml
annotations:
  # Enable Prometheus scraping
  apollo.prometheus.spotify.net/scrape: "true"

  # Exclude from observability podpreset
  podpreset.admission.spotify.com/exclude: "observability"

  # Enable Nameless service discovery
  nameless.spotify.com/srv-expose: "true"
```

## Environment Variables

### From ConfigMap
```yaml
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: my-config
        key: log-level
```

### From Secret
```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: my-secrets
        key: db-password
```

### Direct Value
```yaml
env:
  - name: JVM_ARGS
    value: "-XX:MaxRAMPercentage=80.0"
```

## Anti-Patterns to Avoid

### Don't use "latest" tag
```yaml
# WRONG
image: gcr.io/my-project/my-service:latest

# CORRECT
image: $DEPLOYMENT_IMAGE  # CI substitutes with SHA
```

### Don't skip probes
```yaml
# WRONG - no probes defined
containers:
  - name: my-service
    image: $DEPLOYMENT_IMAGE

# CORRECT - always include probes
```

### Don't set unequal memory request/limit
```yaml
# WRONG - can cause OOM kills
resources:
  requests:
    memory: "4Gi"
  limits:
    memory: "8Gi"

# CORRECT
resources:
  requests:
    memory: "8Gi"
  limits:
    memory: "8Gi"
```
