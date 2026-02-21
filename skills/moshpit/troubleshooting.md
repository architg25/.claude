# Troubleshooting

Common issues and solutions for Moshpit load testing.

## Configuration Errors

### Invalid YAML Syntax

**Symptom**: `YAML parsing error`

**Solution**:
```bash
# Validate YAML syntax
yamllint moshpit-config.yaml

# Use online YAML validator
```

**Common causes**:
- Incorrect indentation
- Missing quotes around special characters
- Tab characters instead of spaces

### Unknown Field

**Symptom**: `Unknown field 'xyz' in configuration`

**Solution**:
- Check field name spelling
- Verify field is at correct nesting level
- Consult [configuration docs](https://backstage.spotify.net/docs/default/system/moshpit-load-testing/)

### Missing Required Field

**Symptom**: `Required field 'target_id' is missing`

**Solution**:
```yaml
targets:
  - name: 'My Test'
    target_id: 'my_test'  # Add the missing field
    # ... rest of config
```

## Connection Issues

### Service Unavailable

**Symptom**: All requests fail with connection errors

**Diagnosis**:
```bash
# Check service is running
kubectl get pods -l app=my-service -n testing

# Test connectivity
kubectl exec -it load-test-pod -- curl http://my-service:8080/health
```

**Solutions**:
1. Verify `base_service_uri` is correct
2. Check service is deployed in target environment
3. Verify network policies allow load test traffic
4. Check DNS resolution

### Connection Timeout

**Symptom**: Requests timeout during connection

**Solutions**:
1. Increase connection timeout
2. Check firewall rules
3. Verify service port is correct
4. Check for network latency between regions

### TLS/SSL Errors

**Symptom**: Certificate errors for HTTPS endpoints

**Solutions**:
1. Use correct protocol (`https://` vs `http://`)
2. Skip certificate verification for testing (if appropriate)
3. Ensure certificates are valid

## Performance Issues

### Low Throughput

**Symptom**: Actual RPS much lower than configured

**Diagnosis**:
```yaml
# Check if service is the bottleneck
estimated_service_response_time_millis: 100  # Adjust based on actual latency
```

**Solutions**:
1. Increase `estimated_service_response_time_millis`
2. Check target service capacity
3. Verify load test resources are sufficient
4. Check for rate limiting

### High Error Rate

**Symptom**: Many 5xx errors during test

**Diagnosis**:
- Check target service logs
- Verify service can handle the load
- Look for resource exhaustion (CPU, memory, connections)

**Solutions**:
1. Reduce RPS to sustainable level
2. Add ramp-up time
3. Scale target service
4. Check for upstream dependencies failing

### Inconsistent Latency

**Symptom**: Latency varies wildly during test

**Possible causes**:
- Cold start (add ramp-up)
- GC pauses on target service
- Network congestion
- Database connection pool exhaustion

## Data Source Issues

### BigQuery Query Timeout

**Symptom**: Data source query times out

**Solutions**:
```yaml
data_source:
  type: bigquery
  query: |
    -- Add LIMIT
    SELECT * FROM table LIMIT 10000

    -- Use partitioned table
    SELECT * FROM table
    WHERE _PARTITIONDATE = CURRENT_DATE()

    -- Select fewer columns
    SELECT user_id, name FROM table  -- Not SELECT *
```

### GCS Access Denied

**Symptom**: `Permission denied` for GCS file

**Solutions**:
1. Check service account has `storage.objects.get` permission
2. Verify bucket and file path are correct
3. Check file exists

### Variable Not Found

**Symptom**: `Variable 'user_id' not found`

**Diagnosis**:
```yaml
# Check query returns the column
data_source:
  query: 'SELECT user_id FROM users'  # Column must match variable name

# Usage
path: '/api/users/{{user_id}}'  # Must match column name exactly
```

## Test Execution Issues

### Test Won't Start

**Symptom**: Test stays in "pending" state

**Solutions**:
1. Check for resource quotas
2. Verify load test service account permissions
3. Check for validation errors in logs
4. Ensure namespace is unique

### Test Terminates Early

**Symptom**: Test stops before configured duration

**Causes**:
- Error rate exceeded threshold
- Resource limits reached
- Manual cancellation
- Service unavailable

**Check logs**:
```bash
moshpit logs --namespace my-test --target my_target
```

### Results Not Appearing

**Symptom**: Test completes but no results in dashboard

**Solutions**:
1. Wait for metrics propagation (can take 1-5 minutes)
2. Check correct Grafana dashboard
3. Verify time range includes test execution
4. Check for metrics collection errors

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `Connection refused` | Service not listening | Check service and port |
| `DNS lookup failed` | Can't resolve hostname | Check service name and namespace |
| `Request timeout` | Service too slow | Increase timeout or reduce load |
| `Rate limit exceeded` | Hit rate limiter | Reduce RPS or add auth bypass |
| `502 Bad Gateway` | Upstream failure | Check service dependencies |
| `503 Service Unavailable` | Service overloaded | Reduce load, scale service |

## Getting Help

### Before Asking for Help

1. Validate your configuration: `moshpit validate --config config.yaml`
2. Check target service health
3. Review load test logs
4. Check Grafana for metrics

### Information to Include

When asking in #moshpit-users:
- Configuration file (sanitized)
- Error messages
- Target service name
- Environment (testing/staging/production)
- Expected vs actual behavior

### Useful Commands

```bash
# Validate config
moshpit validate --config moshpit-config.yaml

# Dry run (no actual requests)
moshpit run --config moshpit-config.yaml --dry-run

# View logs
moshpit logs --namespace my-test

# Cancel running test
moshpit cancel --namespace my-test
```
