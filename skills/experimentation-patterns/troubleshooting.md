# Troubleshooting

Common experimentation issues and solutions.

## Sample Ratio Mismatch (SRM)

### Symptoms
- Variant sizes differ from expected ratio
- EP shows SRM warning

### Common Causes

| Cause | Fix |
|-------|-----|
| Biased exposure filter | Review filter logic (see exposure-filtering skill) |
| Bot traffic difference | Add bot filtering |
| Late property propagation | Wait for mobile sync |
| Redirect-based assignment | Fix redirect logic |

### Investigation Steps
1. Check variant counts in EP
2. Calculate chi-squared test
3. Segment by platform/country
4. Review exposure filter implementation

## Metrics Not Showing

### Symptoms
- Metrics empty in EP
- Delayed metric calculation

### Common Causes

| Cause | Fix |
|-------|-----|
| Exposure not logged | Verify exposure logging |
| Metric join issue | Check user ID alignment |
| Pipeline delay | Wait 24-48 hours |
| Wrong metric selected | Verify Metrics Hub metric |

## Inconclusive Results

### Symptoms
- Confidence interval includes zero
- Can't make decision

### Solutions

| Approach | When to Use |
|----------|-------------|
| Run longer | If close to significance |
| Increase allocation | If safe and underpowered |
| Accept null result | If well-powered, no effect |
| Segment analysis | Look for subgroup effects |

## Unexpected Metric Movement

### Symptoms
- Guardrail metric degraded
- Unexpected direction of change

### Investigation
1. Check for logging changes
2. Verify property resolution
3. Look for external factors
4. Segment by user attributes

## Support

- #experiment-support - Primary support channel
- https://backstage.spotify.net/docs/default/component/experimentation-golden-path/
