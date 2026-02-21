# Troubleshooting

Common issues and solutions for Locus caching.

## Connection Issues

### Authentication Failures

**Symptom**: `LocusAuthenticationException` or 401 errors

**Diagnosis**:
```bash
# Check service account
kubectl get serviceaccount my-service -n my-namespace -o yaml

# Verify Locus allowedAccounts
kubectl get locus my-service-locus -n my-namespace -o yaml | grep -A5 allowedAccounts
```

**Solutions**:
1. Add service account to `allowedAccounts`:
   ```yaml
   spec:
     allowedAccounts:
       - my-service@gke-accounts.iam.gserviceaccount.com
   ```

2. Verify service account annotation in pod spec

### Connection Timeouts

**Symptom**: `LocusTimeoutException` on connect

**Diagnosis**:
```bash
# Check Locus pods are running
kubectl get pods -l app.kubernetes.io/name=my-service-locus -n my-namespace

# Check network policies
kubectl get networkpolicies -n my-namespace
```

**Solutions**:
1. Increase connect timeout:
   ```hocon
   memcached.locus.connect-timeout: 5s
   ```

2. Check DNS resolution from service pod

3. Verify network policies allow traffic

### DNS Resolution Failures

**Symptom**: `UnknownHostException` for Locus endpoint

**Solutions**:
1. Check Locus resource status:
   ```bash
   kubectl describe locus my-service-locus -n my-namespace
   ```

2. Verify DNS is working:
   ```bash
   kubectl exec -it my-pod -- nslookup my-service-locus.my-namespace.svc.cluster.local
   ```

## Performance Issues

### High Latency

**Symptom**: p99 latency > 10ms

**Diagnosis**:
```promql
# Check latency distribution
histogram_quantile(0.99, rate(locus_request_duration_seconds_bucket[5m]))
```

**Solutions**:
1. Add local Caffeine cache for hot data
2. Reduce value sizes (compress if needed)
3. Check network between service and Locus regions
4. Increase Locus shards for parallelism

### Low Hit Rate

**Symptom**: Hit rate < 95%

**Diagnosis**:
```promql
# Calculate hit rate
rate(locus_cache_hits_total[5m]) /
(rate(locus_cache_hits_total[5m]) + rate(locus_cache_misses_total[5m]))
```

**Solutions**:
1. Review TTL strategy - may be too short
2. Check for cache key mismatches (typos, case sensitivity)
3. Verify warmup is enabled if needed
4. Analyze access patterns for hot keys

### High Eviction Rate

**Symptom**: Evictions increasing, memory pressure

**Diagnosis**:
```bash
# Check memory usage
kubectl top pods -l app.kubernetes.io/name=my-service-locus -n my-namespace
```

**Solutions**:
1. Increase `memorySizeGb` in Locus spec
2. Reduce TTL to limit stored data
3. Add more shards to distribute data
4. Review what's being cached (remove unnecessary items)

## Data Issues

### Stale Data

**Symptom**: Cache returns outdated values

**Solutions**:
1. Verify invalidation is working:
   ```java
   // After updates, invalidate
   locusClient.delete("user:" + userId).join();
   ```

2. Reduce TTL for volatile data

3. Implement cache-aside pattern correctly

### Serialization Errors

**Symptom**: `SerializationException` on get/set

**Diagnosis**:
```java
// Check object is serializable
try {
    objectMapper.writeValueAsString(myObject);
} catch (Exception e) {
    log.error("Serialization failed", e);
}
```

**Solutions**:
1. Ensure all cached objects are JSON-serializable
2. Check for circular references
3. Add `@JsonIgnore` to non-serializable fields
4. Use custom serializer if needed

### Key Collisions

**Symptom**: Wrong data returned for keys

**Solutions**:
1. Use namespaced keys:
   ```java
   private String key(String id) {
       return "myservice:user:" + id;
   }
   ```

2. Add cache version prefix:
   ```java
   private static final int VERSION = 2;
   private String key(String id) {
       return "v" + VERSION + ":user:" + id;
   }
   ```

## Operational Issues

### Locus Pods Not Starting

**Diagnosis**:
```bash
kubectl describe locus my-service-locus -n my-namespace
kubectl get events -n my-namespace --sort-by='.lastTimestamp'
```

**Common causes**:
- Resource quota exceeded
- Invalid configuration
- Image pull failures

### Cluster Scaling Issues

**Symptom**: Can't add/remove shards

**Solutions**:
1. Check Locus controller logs
2. Verify resource quotas
3. Wait for in-progress operations to complete

### Warmup Failures

**Symptom**: New shards start cold despite `warmupEnabled: true`

**Diagnosis**:
```bash
kubectl logs -l app.kubernetes.io/name=my-service-locus -n my-namespace | grep warmup
```

**Solutions**:
1. Check source shard is healthy
2. Verify network connectivity between shards
3. Check for timeout during warmup (large datasets)

## Debugging Tools

### CLI Access

```bash
# Port-forward to Locus pod
kubectl port-forward pod/my-service-locus-0 11211:11211 -n my-namespace

# Use memcached CLI
echo "stats" | nc localhost 11211
```

### Metrics Endpoints

```bash
# Get Locus metrics
curl http://my-service-locus:9090/metrics
```

### Log Levels

```hocon
# Increase logging for debugging
logging {
  loggers {
    "com.spotify.locus" = DEBUG
  }
}
```

## Getting Help

1. **Check docs**: https://backstage.spotify.net/docs/default/component/locus/
2. **Slack**: #cache-users
3. **On-call**: Page via PagerDuty if production impact
