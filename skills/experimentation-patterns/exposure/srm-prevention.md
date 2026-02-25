# SRM Prevention

Avoiding Sample Ratio Mismatch with custom exposure.

## What is SRM?

Sample Ratio Mismatch occurs when variant proportions differ from configured allocation.

Example:

- Expected: 50% control, 50% treatment
- Observed: 48% control, 52% treatment
- This indicates bias in experiment

## Common Causes with Custom Exposure

### 1. Biased Filter Logic

**Problem**: Filter triggers differently by treatment.

```java
// BAD: Filter depends on treatment
if (useNewFeature && newFeatureVisible) {
    expose(user);
}

// GOOD: Filter independent of treatment
if (featureAreaVisible) {
    expose(user);
}
```

### 2. Mixed Property Types

**Problem**: Client and backend properties with different timing.

| Property Type | Propagation |
| ------------- | ----------- |
| Backend       | Immediate   |
| Mobile        | 1-3 days    |

**Solution**: Use same property type for all experiment properties.

### 3. Property Conflicts

**Problem**: Overlapping experiments without exclusivity.

**Solution**: Use exclusivity groups in EP.

### 4. Delayed Exposure

**Problem**: Mobile exposure logged days after assignment.

**Solution**:

- Account for delay in analysis window
- Or use online resolution for immediate

## Prevention Checklist

| Check                            | Status |
| -------------------------------- | ------ |
| Filter logic treatment-agnostic? |        |
| Same property types used?        |        |
| Exclusivity group if needed?     |        |
| Propagation delay accounted for? |        |

## Validation: Triggered-Complement Analysis

The users NOT triggered should look like an A/A test:

1. Segment users by triggered vs not-triggered
2. Compare control vs treatment in not-triggered group
3. Should see no significant differences
4. If differences exist, filter is biased

## Monitoring

Check SRM in first 24-48 hours:

1. Go to EP experiment dashboard
2. Check variant proportions
3. Look for SRM warning
4. Investigate immediately if detected
