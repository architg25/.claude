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

Claude subagents try to **confirm** claims. Codex tries to **disprove** them. Agreement = high confidence. Disagreement = investigate. See `shared:dual-agent-dispatch` for the full dispatch and synthesis pattern.

## Instructions

### Step 0: Extract claims

**No argument:** Scan the last ~10 messages. Extract every factual, code-verifiable claim you made. Skip opinions, suggestions, questions. If conversation history is compressed/truncated, ask the user which claims to verify.

**Argument provided:** Use that as the single claim.

Categorize each claim:

| Category            | Example                               |
| ------------------- | ------------------------------------- |
| Code structure      | "X class depends on Y"                |
| Data flow           | "Data goes from A to B via C"         |
| Config/infra        | "Service uses MySQL"                  |
| Service interaction | "A calls B via gRPC"                  |
| Behavior            | "Endpoint returns 404 when not found" |

**Triage:** If a claim can be verified with a single Grep or Read (e.g., "X imports Y"), verify it inline and skip dual dispatch. Reserve dual-agent for claims that need multi-file or multi-repo investigation.

### Step 1: Build verification prompts

For each non-trivial claim, create TWO prompts with opposite framing:

**Confirmation prompt (Claude subagent):**

```
CLAIM TO VERIFY: <claim>
REPO: <path>

You are a codebase verifier. Find EVIDENCE that this claim is TRUE.

- Search for code that supports the claim
- Read actual implementations, not just file names
- Include file paths and line numbers
- If you cannot find supporting evidence, say so explicitly

Report:
1. **Evidence found** — specific code references
2. **Evidence strength** — STRONG / MODERATE / WEAK
3. **Caveats** — anything that qualifies the evidence
```

**Devil's advocate prompt (Codex):**

```
CLAIM TO DISPROVE: <claim>

You are an adversarial code reviewer. Find evidence that CONTRADICTS this claim.

- Look for counter-examples, edge cases, alternative paths
- Check for misleading naming (e.g., "read-only" class that writes)
- Only report contradictions backed by code with file paths and line numbers
- If no contradictions found, say what you searched and why you're confident

Report:
1. **Contradictions found** — specific conflicting code
2. **Contradiction strength** — STRONG / MODERATE / WEAK
3. **If none** — search scope and confidence level
```

### Step 2: Dispatch all verifiers

Dispatch per `shared:dual-agent-dispatch`: Claude subagent to confirm, Codex to disprove, all in a single message with `run_in_background: true`.

**Batching:** Group related claims (max 3 per group). Aim for 2-4 agent pairs total.

### Step 3: Synthesize verdicts

For each claim:

| Verdict            | Condition                                      |
| ------------------ | ---------------------------------------------- |
| **CONFIRMED**      | Strong evidence AND no contradictions          |
| **REFUTED**        | Strong contradictions, regardless of confirmer |
| **PARTIALLY TRUE** | Correct in spirit, wrong in specifics          |
| **UNCERTAIN**      | Weak or conflicting evidence from both sides   |

On disagreement: investigate yourself before ruling. Read the disputed code directly.

### Step 4: Present results

```
## Verification Results

| # | Claim | Verdict | Confidence |
|---|-------|---------|------------|
| 1 | ... | CONFIRMED | High |
| 2 | ... | REFUTED | High |

### Corrections
[For REFUTED or PARTIALLY TRUE claims: what's actually true, with code references]

### What's Solid
[Brief confirmation of what checked out]
```

**Lead with corrections.** Confirmed claims are less interesting.

Save report to `/tmp/verify-<timestamp>/report.md`.

## Important Rules

- **Adversarial framing is not optional.** "Verify this claim" produces confirmation bias. The disprove agent MUST be prompted to disprove.
- **Count carefully.** Claims about numbers are most error-prone. List each item explicitly.
- **Code is truth.** READMEs go stale. If README says one thing and code says another, code wins.
- **PARTIALLY TRUE is valid.** Don't force binary when a claim is directionally correct but wrong in detail.

## Common Mistakes

| Mistake                            | Fix                                                    |
| ---------------------------------- | ------------------------------------------------------ |
| Doing all research yourself        | Dispatch dual agents per shared:dual-agent-dispatch    |
| Waffling on counts                 | List every item by name, then count                    |
| Confirming by default              | Disprove agent should be actively hostile to the claim |
| Spawning agents for trivial claims | One Grep answers it? Do it inline (Step 0 triage)      |
| Compressed conversation history    | Ask user which claims to verify                        |
