---
name: verify
description: Use when you need to cross-check claims made in conversation against the actual codebase. Triggers on "verify what you said", "is that actually true", "double check", "are you sure", or /verify. Also use proactively after making multiple architectural or code-level assertions.
---

# Verify

Cross-check claims from conversation against actual code using adversarial multi-agent verification.

## Usage

```
/verify              # Extract and verify recent claims from conversation
/verify <claim>      # Verify a specific claim
```

## How It Works

Claude subagents try to **confirm** claims. Codex tries to **disprove** them. Agreement = high confidence. Disagreement = investigate.

**The dual-agent structure is mandatory.** You MUST dispatch separate agents — one to confirm, one to disprove. Do NOT do all research yourself in a single pass. Single-pass verification produces confirmation bias even when you try to be objective. The adversarial framing only works when different agents have different jobs.

**You MUST use Codex for disprove agents.** Different model families have different search strategies — Claude and Codex will look in different places. This catches false negatives (e.g., one agent missing code in `app-supply-controls-unknown/` because it only searched `podcast-ads-delivery/`). If both models agree, confidence is high; if they disagree, you know where to dig deeper. Only fall back to Claude-only when Codex is genuinely unavailable (command not found), not because it's "easier" to skip.

## Instructions

### Step 0: Extract claims

**If no argument provided:** Scan the last ~10 messages. Extract every factual, code-verifiable claim you made. Skip opinions, suggestions, and questions.

**If conversation history appears compressed or truncated:** Ask the user which claims to verify rather than guessing from incomplete context.

**If argument provided:** Use that as the single claim to verify.

Categorize each claim:

| Category                | Example                               |
| ----------------------- | ------------------------------------- |
| **Code structure**      | "X class depends on Y"                |
| **Data flow**           | "Data goes from A to B via C"         |
| **Config/infra**        | "Service uses MySQL"                  |
| **Service interaction** | "A calls B via gRPC"                  |
| **Behavior**            | "Endpoint returns 404 when not found" |

**Triage:** Not all claims need the full adversarial treatment. If a claim can be verified with a single Grep or Read (e.g., "X class imports Y"), just verify it inline and skip to the verdict. Reserve the dual-agent dispatch for claims that require searching across multiple files or repos.

### Step 1: Assess complexity and select models

Assess claims using the criteria in `shared:complexity-assessment`. Simple claims (single-hop lookups) get lighter models. Complex claims (data flows, multi-service interactions) get stronger models. When unsure, default to complex.

### Step 2: Build verification prompts

For each claim (or group of related claims), create TWO prompts with opposite framing:

**Confirmation prompt (Claude subagent):**

```
CLAIM TO VERIFY: <claim>
REPO: <path>

You are a codebase verifier. Your job is to find EVIDENCE that this claim is TRUE.

Instructions:
- Search for code that supports the claim
- Read actual implementations, not just file names
- Include file paths and line numbers
- If you cannot find supporting evidence, say so explicitly
- Do NOT assume the claim is true — only report what you find

Report:
1. **Evidence found** — specific code references supporting the claim
2. **Evidence strength** — STRONG (multiple sources), MODERATE (single source), WEAK (indirect)
3. **Caveats** — anything that qualifies or limits the evidence
```

**Devil's advocate prompt (Codex):**

```
CLAIM TO DISPROVE: <claim>

You are an adversarial code reviewer. Your job is to find evidence that CONTRADICTS this claim.

Instructions:
- Actively look for counter-examples
- Check for edge cases, exceptions, or alternative paths
- Look for naming that misleads (e.g., "read-only" class that also writes)
- If you cannot find contradictions, say so explicitly
- Only report contradictions backed by specific code references with file paths and line numbers. Do not speculate or infer contradictions — show the code.

Report:
1. **Contradictions found** — specific code that conflicts with the claim
2. **Contradiction strength** — STRONG (direct refutation), MODERATE (partial), WEAK (edge case only)
3. **If no contradictions** — what you searched and why you're confident there are none
```

### Step 3: Dispatch all verifiers in a SINGLE message

**This step is NOT optional. You MUST dispatch separate agents, not do all research yourself.**

Launch all agents concurrently. All tool calls MUST be in the same message.

**For each claim group, launch TWO agents — one to CONFIRM, one to DISPROVE:**

| Agent           | Role     | Tool                                                     |
| --------------- | -------- | -------------------------------------------------------- |
| Claude subagent | Confirm  | Agent tool, `run_in_background: true`                    |
| Codex instance  | Disprove | Bash `codex exec --full-auto`, `run_in_background: true` |

If Codex is unavailable, use a second Claude subagent for the disprove role instead.

**Claude subagent (confirm):**

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: <confirmation prompt>
  run_in_background: true
  name: "claude-confirm-<n>"
  model: <from Step 1>
```

**Codex (disprove):**

```bash
VERIFY_DIR="/tmp/verify-$(date +%s)" && mkdir -p "$VERIFY_DIR" && codex exec --full-auto -m <model> -C <repo-path> -o "$VERIFY_DIR/codex-disprove-<n>.md" "<devil's advocate prompt>"
```

**Codex fallback and output validation:** See `shared:codex-dispatch` for the full Codex dispatch pattern including fallback to Claude subagents and output file validation.

If Codex unavailable, use Claude subagent with the devil's advocate prompt:

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: <devil's advocate prompt>
  run_in_background: true
  name: "claude-disprove-<n>"
  model: <from Step 1>
```

Use `run_in_background: true` on all tool calls.

**Batching:** Group related claims (max 3 per group). Aim for 2-4 agent pairs total.

**Red flags — you're skipping the adversarial structure if you think:**

- "I can just check this myself quickly" — No. Dispatch agents.
- "Single-pass is more efficient" — Efficiency isn't the goal. Catching mistakes is.
- "I'll be objective" — You won't. That's the whole point of separate agents.

### Step 4: Synthesize verdicts

Once all agents complete, read Codex outputs and compare with Claude results.

**For each claim, determine verdict:**

| Verdict            | Condition                                                                                    |
| ------------------ | -------------------------------------------------------------------------------------------- |
| **CONFIRMED**      | Confirmer found strong evidence AND disprover found no contradictions                        |
| **REFUTED**        | Disprover found strong contradictions, regardless of confirmer                               |
| **PARTIALLY TRUE** | Claim is correct in spirit but wrong in specifics (e.g., right protocol, wrong service name) |
| **UNCERTAIN**      | Weak or conflicting evidence from both sides                                                 |

**On disagreement:** If confirmer and disprover disagree, investigate yourself before ruling. Read the disputed code directly.

### Step 5: Present results

Present a structured summary:

```
## Verification Results

| # | Claim | Verdict | Confidence |
|---|-------|---------|------------|
| 1 | ... | CONFIRMED | High |
| 2 | ... | REFUTED | High |
| 3 | ... | PARTIALLY TRUE | Medium |

### Corrections

[For any REFUTED or PARTIALLY TRUE claims, explain what's actually true with code references]

### What's Solid

[Brief confirmation of what checked out]
```

**Lead with corrections.** The whole point is catching mistakes — confirmed claims are less interesting.

### Step 6: Save output

Save the full report to `$VERIFY_DIR/report.md` (using the timestamped directory created in Step 3). If `$VERIFY_DIR` was not set (e.g., all claims were triaged inline), save to `/tmp/verify-$(date +%s)/report.md`.

## Important Rules

- **Adversarial framing is not optional.** The disprove agent MUST be prompted to disprove. "Verify this claim" produces confirmation bias.
- **Count carefully.** Claims about numbers (dependencies, endpoints, parameters) are the most error-prone. When verifying counts, list each item explicitly — don't just say "5" or "6", name them.
- **Don't conflate tables with databases.** Different tables in the same DB != separate databases.
- **Check the README last.** READMEs go stale. Code is truth. If README says one thing and code says another, code wins.
- **PARTIALLY TRUE is a valid verdict.** Don't force binary CONFIRMED/REFUTED when a claim is right in spirit but wrong in detail.

## Common Mistakes

| Mistake                                                   | Fix                                                                  |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| Doing all research yourself instead of dispatching agents | Follow Step 3. Dispatch confirm + disprove agents.                   |
| Waffling on counts ("it's 5... or maybe 7")               | List every item by name, then count the list                         |
| Treating README as ground truth                           | README is a hint. Code is the answer.                                |
| Binary verdicts only                                      | Use PARTIALLY TRUE when claim is directionally correct               |
| Confirming by default                                     | Disprove agent should be actively hostile to the claim               |
| Skipping Codex for disprove role                          | Different tools search differently; Codex catches Claude blind spots |
| Disprove agent searching too narrowly                     | Search the FULL repo, not just the expected directory                |
| Spawning dual agents for trivially-verifiable claims      | If one Grep answers it, just do it inline (Step 0 triage)            |
| Not handling compressed conversation history              | Ask the user which claims to verify if history is truncated          |
