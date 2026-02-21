# Troubleshooting

Common Kubernetes deployment issues and solutions.

## Pod Not Starting

### ImagePullBackOff
```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Common causes:
# - Wrong image path
# - Missing image tag
# - Registry authentication issues
```

**Solution**: Verify image path and that CI has pushed the image.

### CrashLoopBackOff
```bash
# Check pod logs
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous  # Previous crash
```

**Common causes:**
- Application error on startup
- Missing configuration/secrets
- Port already in use

### Pending (Unschedulable)
```bash
# Check events
kubectl describe pod <pod-name> -n <namespace>
```

**Common causes:**
- Insufficient cluster resources
- Resource requests too high (>15 cores)
- Node selector/affinity issues

## Probe Failures

### Readiness Probe Failed
```bash
# Check probe configuration
kubectl describe deployment <deployment> -n <namespace>

# Test endpoint manually
kubectl exec -it <pod> -n <namespace> -- curl localhost:5700/readiness
```

**Solutions:**
- Increase `initialDelaySeconds`
- Fix health endpoint
- Add startup probe for slow-starting apps

### Liveness Probe Failed (Pod Restarts)
```bash
# Check restart count
kubectl get pods -n <namespace>

# Check logs before restart
kubectl logs <pod> -n <namespace> --previous
```

**Solutions:**
- Increase probe timeout
- Fix deadlock causing health check to hang
- Reduce resource contention

## HPA Issues

### HPA Shows Unknown
```bash
# Check HPA status
kubectl describe hpa <hpa-name> -n <namespace>
```

**Common causes:**
- Metrics server not running
- Pod just started (no metrics yet)
- Wrong metric name

### HPA Not Scaling Up
**Check:**
1. Current CPU utilization vs target
2. maxReplicas not reached
3. No PDB blocking scale-up

### HPA Not Scaling Down
**Check:**
1. Scale-down stabilization window (default 5 min)
2. Scale-down policies (Spotify: 10% per 30 min)
3. Traffic still high

## Deployment Issues

### Deployment Stuck in Rollout
```bash
# Check rollout status
kubectl rollout status deployment/<deployment> -n <namespace>

# Check replica sets
kubectl get rs -n <namespace>

# Rollback if needed
kubectl rollout undo deployment/<deployment> -n <namespace>
```

**Common causes:**
- New pods failing probes
- Resource constraints
- PDB blocking rollout

### Tugboat Validation Failed
```bash
# Run validation
tugboat version <component> validate
```

**Common issues:**
- Invalid YAML syntax
- Missing required fields
- Incompatible configuration

## Runtime Issues

### Runtime Not Creating Namespace
```bash
# Check Runtime status
kubectl describe runtime <runtime-name> -n <namespace>
```

**Common causes:**
- Name/namespace mismatch
- Invalid owner format
- Resource quota invalid

## Gantry Issues

### Gantry Service Not Deploying
```bash
# Check Gantry service status
bazel run //gantry/gantryctl -- describe service <project> <service>

# Check for lingering Tugboat resources
kubectl get deployment -n <namespace>
```

### Secrets Not Injecting
```bash
# Verify secret exists in GSM
gcloud secrets list --project=<project>

# Check secretRefs configuration
```

## Quick Debugging Commands

```bash
# Get all resources for a service
kubectl get all -n <namespace> -l app=<service-name>

# Check events
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Exec into pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Port forward for local testing
kubectl port-forward <pod-name> 8080:8080 -n <namespace>

# Check resource usage
kubectl top pods -n <namespace>
```

## Support Channels

- #deployments-support - Primary deployment issues
- #declarative-infra - Runtime resources
- #warpspeed - Gantry issues
