# Sample Size

Power analysis and experiment sizing.

## Key Inputs

| Input | Description | Typical Value |
|-------|-------------|---------------|
| Baseline Rate | Current metric value | From historical data |
| MDE | Minimum Detectable Effect | Business requirement |
| Power | Probability of detecting effect | 80% |
| Significance | False positive rate | 5% |

## Quick Sizing Guide

### By Effect Size

| Expected Effect | Sample per Variant | Total Duration |
|-----------------|-------------------|----------------|
| Large (>10%) | 5K-10K | Days |
| Medium (3-10%) | 20K-100K | 1-2 weeks |
| Small (1-3%) | 100K-500K | 2-4 weeks |
| Very Small (<1%) | 500K+ | 4+ weeks |

### By Metric Type

| Metric Type | Typical Sensitivity |
|-------------|-------------------|
| Conversion (rare) | Needs large N |
| Engagement (common) | Medium N |
| Revenue (high variance) | Needs large N |

## EP Power Calculator

Use the built-in calculator in EP UI:
1. Enter baseline metric value
2. Enter minimum detectable effect
3. Get required sample size

## Running Underpowered

**Risks:**
- False negatives (miss real effects)
- Inconclusive results
- Wasted engineering effort

**When Acceptable:**
- Exploratory experiments
- Large expected effects
- Time-sensitive decisions

## Duration Estimation

```
Duration = Required Sample / Daily Users in Target
```

Example:
- Need 100K users
- 10K users/day in target
- Duration = 10 days

Add buffer for:
- Weekend/weekday variation
- Holiday effects
- Ramp-up time
