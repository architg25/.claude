---
name: rcs-patterns
description: This skill should be used when the user asks to "create an RCS property", "define a feature flag", "publish a property", "troubleshoot property resolution", "choose between online and offline resolution", or needs guidance on Java/mobile SDK property patterns, resolution contexts, and testing approaches.
allowed-tools:
  - Read
last_validated: 2026-01-20
source_of_truth: https://backstage.spotify.net/docs/default/system/remote-configuration
---

# RCS Patterns

Patterns for Remote Configuration Service property definition and resolution at Spotify.

## Pattern Categories

- **[Property Types](property-types.md)**: Boolean, Integer, Enum, StringSet definitions
- **[Java SDK Patterns](java-sdk-patterns.md)**: Backend property publishing and resolution
- **[Mobile SDK Patterns](mobile-sdk-patterns.md)**: iOS/Android/Web properties.yaml usage
- **[Resolution Patterns](resolution-patterns.md)**: Online (Pizza) vs Offline (bloom filters)
- **[Testing Patterns](testing-patterns.md)**: Override testing, Backstage plugin usage
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Quick Reference

### Property Type Selection

| Type | Use Case | Example |
|------|----------|---------|
| Boolean | Feature flags | `enable_dark_mode` |
| Integer | Thresholds, limits | `max_retries`, `timeout_ms` |
| Enum | Mode selection | `search_algorithm: [v1, v2, v3]` |
| StringSet | Allow/deny lists | `enabled_markets` |

### Resolution Mode Selection

| Need | Mode | Why |
|------|------|-----|
| Immediate updates | Online (Pizza) | Real-time fetching |
| Low latency | Offline | Cached policies |
| User attributes | Online (Pizza) | Requires attribute fetching |
| Simple targeting | Offline | User/country/catalogue only |

## Critical Constraints

- **Always** include `withDescription()` for property definitions
- **Always** set meaningful defaults (fail-safe values)
- **Never** use offline mode for registration date targeting
- **Never** expect immediate propagation for mobile properties (days delay)

## Related Skills

- [experimentation-patterns](../experimentation-patterns/SKILL.md) - Experiment setup, exposure filtering, and RCS property targeting

## Support Channels

- #rcs-support - RCS-specific questions
- #experiment-support - Experimentation Platform help
