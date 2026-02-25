---
name: experimentation-patterns
description: This skill should be used when the user asks to "create an experiment", "set up a rollout", "calculate sample size", "select metrics", "configure targeting", "troubleshoot SRM", "filter experiment exposure", "use ExposerLib", "prevent SRM", "create custom exposure", "narrow exposed population", or needs guidance on Experimentation Platform setup, A/B testing, experiment analysis, Custom Source, Custom Dataset Exposure, Metrics Hub attributes, and exposure debugging.
allowed-tools:
  - Read
last_validated: 2026-01-20
source_of_truth: https://backstage.spotify.net/docs/default/component/experimentation-golden-path/
---

# Experimentation Patterns

Patterns for Spotify's Experimentation Platform (EP) built on RCS.

## Pattern Categories

- **[Experiment Setup](experiment-setup.md)**: Creating experiments step-by-step
- **[Rollout Setup](rollout-setup.md)**: Creating rollouts for gradual releases
- **[Metrics Selection](metrics-selection.md)**: Success and guardrail metrics
- **[Targeting Patterns](targeting-patterns.md)**: Country, platform, user segments
- **[Sample Size](sample-size.md)**: Power analysis and sizing
- **[Troubleshooting](troubleshooting.md)**: Common issues (SRM, exposure)

## Quick Reference

### Experiment vs Rollout

| Aspect   | Experiment             | Rollout        |
| -------- | ---------------------- | -------------- |
| Purpose  | Measure impact         | Ship feature   |
| Variants | Control + Treatment(s) | Single variant |
| Metrics  | Required               | Optional       |
| Duration | Fixed analysis window  | Until 100%     |

### Experiment Lifecycle

1. **Property Definition** → Define in code, publish to RCS
2. **EP Configuration** → Create experiment, select metrics
3. **QA** → Test with overrides
4. **Launch** → Start at low % (5-10%)
5. **Monitor** → Check SRM daily
6. **Analysis** → Review metrics, decide

### Key Metrics Types

| Type      | Purpose              | Example             |
| --------- | -------------------- | ------------------- |
| Primary   | Core success measure | Conversion rate     |
| Secondary | Supporting evidence  | Engagement time     |
| Guardrail | Safety check         | Error rate, latency |

## Exposure Filtering

Patterns for narrowing experiment exposure to improve metric accuracy.

- **[Custom Source](exposure/custom-source.md)**: Pre-defined data endpoint with exposed users
- **[Custom Dataset](exposure/custom-dataset.md)**: SQL queries defined in EP UI
- **[Metrics Hub Attributes](exposure/metrics-hub-attributes.md)**: Boolean attributes for exposure
- **[ExposerLib Patterns](exposure/exposerlib-patterns.md)**: Backend custom exposure logging
- **[SRM Prevention](exposure/srm-prevention.md)**: Avoiding Sample Ratio Mismatch
- **[Debugging Exposure](exposure/debugging-exposure.md)**: Troubleshooting exposure issues

### When to Use Custom Exposure

```
Need custom exposure filter?
├── Default exposure sufficient (all users who fetch config)?
│   └── No filter needed
└── Need to narrow exposed population?
    ├── Pre-existing data endpoint with exposed users?
    │   └── Use Custom Source
    ├── Can define exposure with SQL query?
    │   └── Use Custom Dataset Exposure
    └── Need complex logic or reuse across experiments?
        └── Create Metrics Hub boolean attribute
```

### Filter Type Comparison

| Type                  | Configuration    | Best For                |
| --------------------- | ---------------- | ----------------------- |
| Custom Source         | exp-planner repo | Existing data endpoints |
| Custom Dataset        | EP UI (SQL)      | One-off SQL queries     |
| Metrics Hub Attribute | Metrics Hub      | Reusable logic          |
| ExposerLib            | Code             | Backend request-level   |

## Critical Constraints

- **Always** start experiments at low percentage (5-10%)
- **Always** monitor for SRM in first 24-48 hours
- **Always** ensure exposure filters are treatment-agnostic (no bias)
- **Always** verify triggered-complement looks like A/A test
- **Never** change experiment configuration mid-flight
- **Never** use overlapping properties without exclusivity groups
- **Never** filter more aggressively in one treatment
- **Never** mix client/backend properties without accounting for timing

## Related Skills

- [rcs-patterns](../rcs-patterns/SKILL.md) - Property definitions for experiments

## Support Channels

- #experiment-support - Primary EP support
- #metrics-hub - Custom attributes
- https://backstage.spotify.net/experimentation - EP UI
