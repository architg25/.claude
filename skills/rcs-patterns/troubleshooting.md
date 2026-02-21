# Troubleshooting

Common RCS issues and solutions.

## Property Not Resolving

### Symptoms
- Property returns default value unexpectedly
- Targeting not working

### Checks
1. **Property published?** Check RCS UI for property existence
2. **Policy active?** Verify policy is enabled in EP
3. **Targeting match?** Test with Backstage plugin
4. **Resolution context correct?** Log context fields

## Offline Resolution Silent Failures

### Symptoms
- Targeting works for some attributes but not others

### Cause
Offline mode doesn't support all targeting types.

### Solution
```java
// Switch to online resolution for complex targeting
RemoteConfigInitializer.resolverBuilder(SERVICE_NAME, registry)
    .withOnlineResolution()  // Use Pizza
    .publish(properties);
```

## Mobile Property Delay

### Symptoms
- New property values not reaching mobile users

### Cause
Bloom filter propagation takes 1-3 days.

### Solution
- Wait for propagation before analyzing metrics
- Use online resolution for immediate updates
- Account for delay in experiment timeline

## Timeout Errors

### Symptoms
- `TimeoutException` during resolution

### Solution
```java
// Increase timeout
.withResolveTimeout(Duration.ofMillis(2000))

// Or handle gracefully
.orElse(defaultConfig)
```

## Support

- #rcs-support - RCS-specific questions
- https://backstage.spotify.net/docs/default/system/remote-configuration
