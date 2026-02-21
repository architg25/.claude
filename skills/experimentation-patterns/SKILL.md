---
name: experimentation-patterns
description: This skill should be used when the user asks to "create an experiment", "set up a rollout", "calculate sample size", "select metrics", "configure targeting", "troubleshoot SRM", or needs guidance on Experimentation Platform setup, A/B testing, and experiment analysis.
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

| Aspect | Experiment | Rollout |
|--------|------------|---------|
| Purpose | Measure impact | Ship feature |
| Variants | Control + Treatment(s) | Single variant |
| Metrics | Required | Optional |
| Duration | Fixed analysis window | Until 100% |

### Experiment Lifecycle

1. **Property Definition** → Define in code, publish to RCS
2. **EP Configuration** → Create experiment, select metrics
3. **QA** → Test with overrides
4. **Launch** → Start at low % (5-10%)
5. **Monitor** → Check SRM daily
6. **Analysis** → Review metrics, decide

### Key Metrics Types

| Type | Purpose | Example |
|------|---------|---------|
| Primary | Core success measure | Conversion rate |
| Secondary | Supporting evidence | Engagement time |
| Guardrail | Safety check | Error rate, latency |

## Critical Constraints

- **Always** start experiments at low percentage (5-10%)
- **Always** monitor for SRM in first 24-48 hours
- **Never** change experiment configuration mid-flight
- **Never** use overlapping properties without exclusivity groups

## Related Skills

- [rcs-patterns](../rcs-patterns/SKILL.md) - Property definitions for experiments
- [exposure-filtering](../exposure-filtering/SKILL.md) - Custom exposure filters

## Support Channels

- #experiment-support - Primary EP support
- https://backstage.spotify.net/experimentation - EP UI
