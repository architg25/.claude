# Experiment Setup

Step-by-step guide to creating experiments.

## Prerequisites

1. Property defined in code (see rcs-patterns skill)
2. Property published to RCS
3. Metrics identified in Metrics Hub

## Step 1: Create Experiment in EP UI

Navigate to https://backstage.spotify.net/experimentation

1. Click "Create Experiment"
2. Select your RCS property
3. Name experiment clearly (feature + hypothesis)

## Step 2: Configure Variants

| Variant | Property Value | Purpose |
|---------|---------------|---------|
| Control | `false` (default) | Baseline |
| Treatment | `true` | New feature |

### Multiple Treatments
For testing multiple options:
- Treatment A: `algorithm_v2`
- Treatment B: `algorithm_v3`
- Control: `algorithm_v1`

## Step 3: Select Metrics

### Primary Metric
- One metric that defines success
- Must have clear hypothesis direction
- Example: "Increase conversion rate by 2%"

### Secondary Metrics
- Supporting evidence
- Related engagement measures

### Guardrail Metrics
- Safety checks (error rate, latency)
- Should NOT degrade significantly

## Step 4: Configure Targeting

See targeting-patterns.md for details.

Common configurations:
- All users (default)
- Specific countries
- Specific platforms
- User segments

## Step 5: Set Sample Size

See sample-size.md for power analysis.

Quick guidance:
| Effect Size | Typical Sample |
|-------------|---------------|
| Large (>5%) | 10K-50K users |
| Medium (2-5%) | 50K-200K users |
| Small (<2%) | 200K+ users |

## Step 6: Launch

1. Start at 5-10% allocation
2. Verify no SRM in 24-48 hours
3. Ramp to full allocation
4. Run for planned duration

## Checklist

- [ ] Property published and verified
- [ ] Metrics selected and hypothesis documented
- [ ] Targeting configured correctly
- [ ] Sample size calculated
- [ ] QA testing completed
- [ ] Stakeholders informed
