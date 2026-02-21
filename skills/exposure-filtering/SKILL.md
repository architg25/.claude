---
name: exposure-filtering
description: This skill should be used when the user asks to "filter experiment exposure", "use ExposerLib", "prevent SRM", "create custom exposure", "narrow exposed population", or needs guidance on Custom Source, Custom Dataset Exposure, Metrics Hub attributes, and exposure debugging.
allowed-tools:
  - Read
last_validated: 2026-01-20
source_of_truth: https://backstage.spotify.net/docs/default/component/experimentation-design-best-practice/part-3-experiment-setup/7-custom-exposure-filters/
---

# Exposure Filtering Patterns

Patterns for narrowing experiment exposure to improve metric accuracy.

## Pattern Categories

- **[Custom Source](custom-source.md)**: Pre-defined data endpoint with exposed users
- **[Custom Dataset](custom-dataset.md)**: SQL queries defined in EP UI
- **[Metrics Hub Attributes](metrics-hub-attributes.md)**: Boolean attributes for exposure
- **[ExposerLib Patterns](exposerlib-patterns.md)**: Backend custom exposure logging
- **[SRM Prevention](srm-prevention.md)**: Avoiding Sample Ratio Mismatch
- **[Debugging Exposure](debugging-exposure.md)**: Troubleshooting exposure issues

## Quick Reference

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

| Type | Configuration | Best For |
|------|--------------|----------|
| Custom Source | exp-planner repo | Existing data endpoints |
| Custom Dataset | EP UI (SQL) | One-off SQL queries |
| Metrics Hub Attribute | Metrics Hub | Reusable logic |
| ExposerLib | Code | Backend request-level |

### Common Use Cases

| Scenario | Filter Type | Example |
|----------|-------------|---------|
| Widget visibility | Custom Dataset | iOS widget users |
| Page scroll depth | Custom Dataset | Users who scrolled to feature |
| Query length filter | Metrics Hub | Queries > 3 chars |
| Request-level exposure | ExposerLib | Specific API calls |

## Critical Constraints

- **Always** ensure filter is treatment-agnostic (no bias)
- **Always** verify triggered-complement looks like A/A test
- **Never** filter more aggressively in one treatment
- **Never** mix client/backend properties without accounting for timing

## Related Skills

- [rcs-patterns](../rcs-patterns/SKILL.md) - Property definitions
- [experimentation-patterns](../experimentation-patterns/SKILL.md) - Experiment setup

## Support Channels

- #experiment-support - Exposure filter questions
- #metrics-hub - Custom attributes
