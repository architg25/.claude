# Troubleshooting

Common Apollo configuration issues and solutions.

## Configuration Not Loading

### Issue: Changes Not Taking Effect
```bash
# Check which config is being loaded
java -Dconfig.trace=loads -jar myservice.jar
```

**Solutions:**
- Verify file is in `src/main/resources/`
- Check file name matches service name
- Rebuild after config changes

### Issue: Config File Not Found
```
ConfigException: No configuration found
```

**Solutions:**
- Verify file path: `src/main/resources/{service-name}.conf`
- Check classpath includes resources
- Verify Maven/Gradle resource configuration

## Environment Variable Issues

### Issue: Variable Not Substituted
```hocon
# Config shows literal ${?VAR} instead of value
url = ${?MY_URL}
```

**Solutions:**
- Verify env var is set: `echo $MY_URL`
- Check for typos in variable name
- Ensure using `${?VAR}` not `$VAR`

### Issue: Required Variable Missing
```
ConfigException: Could not resolve substitution to a value: ${MY_REQUIRED_VAR}
```

**Solutions:**
- Set the environment variable
- Change to optional: `${?MY_REQUIRED_VAR}`
- Add default value first

## Secret Injection Issues

### Issue: Secret File Not Found
```
ConfigException: include file not found: /etc/spotify/secrets/service.json
```

**Solutions:**
- Verify secret mount in Kubernetes
- Check file permissions
- Verify path in config matches actual path

### Issue: Invalid JSON in Secret
```
ConfigException: Unable to parse file
```

**Solutions:**
- Validate JSON syntax
- Check for trailing commas
- Verify quotes around string values

## Connection Pool Issues

### Issue: Pool Exhausted
```
Cannot acquire connection from pool
```

**Solutions:**
- Increase `max-total` pool size
- Check for connection leaks
- Add connection timeouts

### Issue: Connection Timeouts
```
Connection timed out after 10000ms
```

**Solutions:**
- Increase `max-wait-millis`
- Check database connectivity
- Verify network configuration

## gRPC Issues

### Issue: Deadline Exceeded
```
DEADLINE_EXCEEDED: deadline exceeded after 10s
```

**Solutions:**
```hocon
grpc.server {
  deadlineEnforcer {
    defaultDeadline: 30s  # Increase if needed
  }
}
```

### Issue: Port Already in Use
```
Address already in use: bind
```

**Solutions:**
- Check for duplicate service instances
- Verify port configuration
- Kill existing process on port

## Debugging Commands

```bash
# Print resolved configuration
java -Dconfig.trace=loads -jar myservice.jar

# Verify environment variables
env | grep MY_VAR

# Check file permissions
ls -la /etc/spotify/secrets/

# Validate HOCON syntax
# (Use online HOCON parser or IDE plugin)
```

## Common HOCON Syntax Errors

### Missing Colon/Equals
```hocon
# WRONG
setting value

# CORRECT
setting: value
# or
setting = value
```

### Unquoted Special Characters
```hocon
# WRONG
url: http://localhost:8080

# CORRECT
url: "http://localhost:8080"
```

### Missing Braces
```hocon
# WRONG
jdbc.pool.max-total: 20
jdbc.pool.min-idle: 2

# CORRECT
jdbc {
  pool {
    max-total: 20
    min-idle: 2
  }
}
```
