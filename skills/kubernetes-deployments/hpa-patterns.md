# HPA Patterns

Patterns for Horizontal Pod Autoscaler configuration at Spotify.

## Basic HPA (Recommended)

**Use when**: Standard autoscaling for Apollo services

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-service
  namespace: my-namespace
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      policies:
        - type: Percent
          value: 10
          periodSeconds: 1800
```

## Spotify Recommended Settings

| Setting | Value | Reason |
|---------|-------|--------|
| minReplicas | 3 | High availability across zones |
| maxReplicas | 20 | Reasonable upper bound |
| CPU target | 80% | Balance efficiency and headroom |
| Scale-down rate | 10% per 30 min | Prevent flapping |

## CPU-Based Scaling

### Standard Configuration
```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

### Aggressive Scaling
```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Scale earlier
```

## Scale-Down Behavior

### Conservative (Recommended)
```yaml
behavior:
  scaleDown:
    policies:
      - type: Percent
        value: 10
        periodSeconds: 1800  # 30 minutes
    stabilizationWindowSeconds: 300
```

### Aggressive (Development)
```yaml
behavior:
  scaleDown:
    policies:
      - type: Percent
        value: 50
        periodSeconds: 300  # 5 minutes
```

## Scale-Up Behavior

### Fast Response
```yaml
behavior:
  scaleUp:
    policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 4
        periodSeconds: 60
    selectPolicy: Max
```

## Why NOT Memory-Based Scaling

**Don't use memory for Java services:**

```yaml
# WRONG for Java services
metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Reasons:**
- Java heap doesn't shrink predictably
- Scaling up kills warm caches
- GC behavior is unpredictable
- Memory is not a good proxy for load

## Custom Metrics

**Use when**: Business metrics better indicate load

```yaml
metrics:
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

## High-Traffic Service

**Use when**: Service handles very high traffic

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: high-traffic-service
  namespace: my-namespace
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: high-traffic-service
  minReplicas: 10
  maxReplicas: 100
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # More headroom
  behavior:
    scaleUp:
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30  # Fast scale-up
    scaleDown:
      policies:
        - type: Percent
          value: 5
          periodSeconds: 1800  # Slow scale-down
```

## Troubleshooting

### HPA Not Scaling
```bash
# Check HPA status
kubectl get hpa my-service -n my-namespace

# Check current metrics
kubectl describe hpa my-service -n my-namespace

# Verify metrics-server is running
kubectl get pods -n kube-system | grep metrics-server
```

### Common Issues
- **Unknown target**: Metrics server not running or no metrics yet
- **Stuck at min**: CPU not reaching target threshold
- **Stuck at max**: Need to increase maxReplicas or optimize service
