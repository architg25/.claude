# Complexity Assessment & Model Selection

## Two-Tier Classification

Classify every task as **Simple** or **Complex** before spawning subagents or selecting models.

### Simple Signals

- Single-hop lookups: "where is X defined", "what config does Y use"
- Single-file checks or confirmations
- Direct relationship queries: "X uses Y", "what calls Z"
- Factual retrieval with one clear answer

### Complex Signals

- Multiple services or repos involved
- Data flow tracing across boundaries
- Architectural or design questions
- Cross-team or cross-service interactions
- Behavioral assertions ("does X happen when Y")
- User explicitly requests "deep dive", "thorough", or "comprehensive"

### Default

When unsure, **default to Complex**. Overestimating complexity wastes a bit of compute; underestimating it produces shallow answers.

## Model Mapping

| Tier    | Claude subagents  | Codex (via `codex:codex-rescue`) |
| ------- | ----------------- | -------------------------------- |
| Simple  | `model: "sonnet"` | `--model spark`                  |
| Complex | `model: "opus"`   | default (omit `--model`)         |

> Model IDs will change over time. Update this table when new models are available. The key principle is: **use cheaper/faster models for simple tasks, stronger models for complex ones.**

## Effort Mapping

The `--effort` flag controls Codex reasoning depth. Pass it as a flag in the rescue prompt (e.g., `--effort high <prompt>`).

| Tier    | Effort flag                         |
| ------- | ----------------------------------- |
| Simple  | omit (let Codex decide)             |
| Complex | `--effort high` or `--effort xhigh` |

## Researcher Count (research-style skills)

| Tier    | Researchers |
| ------- | ----------- |
| Simple  | 1-2         |
| Complex | 3-4         |
