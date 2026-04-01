# Dual-Agent Dispatch

Dispatch work to two model families (Claude + Codex) in parallel for adversarial cross-checking. Use this whenever a skill needs independent verification from different AI systems.

## Why Two Model Families

Different models search differently and have different blind spots. This isn't redundancy — it's adversarial cross-checking. If both agree, confidence is high. If they disagree, you know exactly where to dig deeper.

**You MUST use Codex for the second agent.** Only fall back to a second Claude subagent when Codex is genuinely unavailable (`command not found`), not because it's "easier" to skip. When falling back, log it — results are less independent when both agents are the same model.

## Dispatch Recipe

### 1. Assess complexity

Use `shared:complexity-assessment` to determine the tier (Simple/Complex) and model IDs for both Claude and Codex.

### 2. Build prompts

Write one prompt per agent. The framing depends on the skill:

- **Review skills:** both get the same review criteria, independence comes from different models
- **Verify:** one confirms, one disproves (adversarial framing)
- **Research:** each gets a different angle of the question

### 3. Launch all agents in a SINGLE message

All tool calls MUST be in the same message, all with `run_in_background: true`.

**Claude subagent:**

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: <prompt>
  run_in_background: true
  name: "claude-<role>"
  model: <from complexity-assessment>
```

**Codex instance:**

```bash
WORK_DIR="/tmp/<skill>-$(date +%s)" && mkdir -p "$WORK_DIR" && codex exec --full-auto -m <model> -o "$WORK_DIR/codex-<role>.md" "<prompt>"
```

See `shared:codex-dispatch` for Codex CLI flags and conventions.

### 4. Collect and validate results

- Claude subagent results return directly
- Codex outputs: check file exists AND is non-empty before reading
- If Codex output missing/empty: note the failure, synthesize from Claude only

### 5. Fallback: Codex unavailable

If `codex` command not found:

1. Dispatch a second Claude subagent with the same prompt
2. Use `run_in_background: true`, same output expectations
3. Log the fallback in your synthesis ("Note: Codex unavailable, used Claude for both agents")

## Synthesis Pattern

| Signal                   | Action                                             |
| ------------------------ | -------------------------------------------------- |
| Both agree               | Report as consensus (high confidence)              |
| Only one found something | Include, note single-source                        |
| They disagree            | Investigate yourself before ruling — read the code |
| One failed/empty         | Synthesize from remaining, note the gap            |

**Lead with conflicts and corrections.** Agreement is boring — disagreements are where the value is.

## Naming Convention

Prefix every agent name with its model family: `claude-<role>`, `codex-<role>`. Makes synthesis output clear about which model produced which finding.

## Red Flags — You're Skipping Dual Dispatch

| Thought                         | Reality                                         |
| ------------------------------- | ----------------------------------------------- |
| "I can just check this myself"  | You wrote it. You can't objectively review it.  |
| "Single-pass is more efficient" | Catching mistakes is the goal, not speed.       |
| "I'll be objective"             | You won't. That's the whole point.              |
| "Codex is overkill for this"    | 15 seconds of compute vs. undoing a bad review. |
