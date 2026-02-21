# Rollout Setup

Gradual feature releases without full experimentation.

## When to Use Rollouts

| Scenario | Use Rollout? |
|----------|--------------|
| New feature, need metrics | No → Experiment |
| Proven feature, gradual ship | Yes |
| Risk mitigation only | Yes |
| A/B comparison needed | No → Experiment |

## Step 1: Create Rollout

1. Navigate to EP UI
2. Click "Create Rollout"
3. Select your property
4. Name rollout clearly

## Step 2: Configure Stages

```
Stage 1: 1% → Verify no crashes
Stage 2: 10% → Monitor metrics
Stage 3: 50% → Check at scale
Stage 4: 100% → Full release
```

### Recommended Timeline

| Stage | Percentage | Duration |
|-------|------------|----------|
| 1 | 1-5% | 1-2 days |
| 2 | 10-25% | 3-5 days |
| 3 | 50% | 3-5 days |
| 4 | 100% | - |

## Step 3: Define Rollback Criteria

Document what triggers rollback:
- Error rate > X%
- Latency p99 > Y ms
- Crash rate increase > Z%

## Step 4: Execute Rollout

1. Advance to each stage manually
2. Monitor guardrail metrics
3. Wait minimum time at each stage
4. Document any issues

## Rollout vs Feature Flag

After 100% rollout:
1. Keep property for kill-switch capability
2. Or remove property and hard-code behavior
3. Document decision in ticket
