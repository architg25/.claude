# Metrics Selection

Choosing the right metrics for experiments.

## Metric Categories

### Primary Metrics
Single metric that defines experiment success.

**Characteristics:**
- Directly measures business value
- Has clear expected direction
- Sensitive enough to detect change

**Examples:**
| Domain | Primary Metric |
|--------|---------------|
| Search | Query success rate |
| Playback | Stream starts |
| Conversion | Premium signups |

### Secondary Metrics
Supporting evidence for primary metric.

**Purpose:**
- Understand mechanism of change
- Detect unintended effects
- Provide additional context

### Guardrail Metrics
Safety checks that should NOT degrade.

**Must-haves:**
- Error rate
- Latency (p50, p99)
- Crash rate

## Metrics Hub Integration

Metrics are defined in Metrics Hub:
- Search for existing metrics first
- Create new metrics if needed
- Ensure proper exposure alignment

## Metric Selection Checklist

| Question | Answer |
|----------|--------|
| Is primary metric tied to business goal? | |
| Can we detect expected effect size? | |
| Do we have relevant guardrails? | |
| Are metrics available in Metrics Hub? | |

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too many primary metrics | Unclear success | Pick one |
| No guardrails | Miss regressions | Add error/latency |
| Vanity metrics | No business value | Tie to outcomes |
