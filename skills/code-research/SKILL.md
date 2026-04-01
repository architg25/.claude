---
name: code-research
description: "Use when the user wants to research how something works in the codebase, trace data flows, find implementations, or answer technical questions about services and systems. Triggers on questions like 'how does X work', 'where is Y defined', 'trace the flow of Z'."
---

# Research

Dispatch multiple parallel researchers (Claude subagents + Codex instances) to investigate a question from different angles, then synthesize findings.

## Usage

```
/code-research <question>
```

## When NOT to Use

Don't use this for questions answerable with a single tool call:

- "Where is class Foo defined?" → just use Grep
- "What files import X?" → just use Grep
- "Show me the config file" → just use Glob + Read

Rule of thumb: if you can answer it with one Grep or Glob, don't spawn 4 agents.

## Instructions

### Step 0: Assess complexity

Assess the question using the criteria in `shared:complexity-assessment`.

This determines **model selection**. Do not artificially limit researcher count — use as many angles as the question needs.

### Step 1: Decompose the question into research angles

Break the user's question into 3-4 focused sub-questions that attack it from different angles. Each angle should be narrow enough to finish fast.

Example for "how does Padme get video files written to its DB":

- **Angle 1** (local code): Find Padme's DB write paths, models, and storage layer
- **Angle 2** (cross-repo): Find upstream services/jobs that call Padme's write APIs
- **Angle 3** (data flow): Trace the video file from ingestion to DB row — what transformations happen?

Tailor the angles to the question. Common splits:

- **Local code** vs **cross-repo** (codesearch MCP)
- **Producer** vs **consumer** sides of a flow
- **Config/infra** vs **application code**
- **API surface** vs **internal implementation**

### Step 2: Build research prompts

For each angle, construct a focused prompt using this template:

```
RESEARCH ANGLE: <angle description>
CONTEXT: <user's original question>

You are a codebase researcher. Answer the angle above thoroughly.

Instructions:
- Search broadly first, then drill into specifics
- Look at actual code, not just file names
- Include file paths and line numbers for key findings
- Note any assumptions or gaps in your findings

Write your findings as a structured report with:
1. **Summary** - Direct answer in 2-3 sentences
2. **Key Findings** - Detailed evidence with file paths and code references
3. **Data Flow** - How data moves through the system (if applicable)
4. **Open Questions** - Anything you couldn't determine
```

### Step 3: Dispatch all researchers in a SINGLE message

Create the output directory and launch all agents concurrently. All tool calls MUST be in the same message.

**You MUST use both Claude subagents AND Codex instances.** Do not use only Claude subagents. Codex has MCP access (including codesearch) and can explore codebases independently. Using a different model family acts as a cross-check — if Claude and Codex agree, confidence is high; if they disagree, you know where to dig deeper during synthesis.

**Minimum mix:** At least 1 Codex instance and at least 1 Claude subagent. For 3-4 researchers, use 2 of each.

**Naming convention:** Prefix every researcher name with `claude-` or `codex-` so the synthesis output clearly shows which model produced which findings.

| Researcher      | Tool                                          | Name example        |
| --------------- | --------------------------------------------- | ------------------- |
| Claude subagent | Agent tool (`run_in_background: true`)        | `claude-local-code` |
| Claude subagent | Agent tool (`run_in_background: true`)        | `claude-cross-repo` |
| Codex instance  | Bash `codex exec` (`run_in_background: true`) | `codex-data-flow`   |
| Codex instance  | Bash `codex exec` (`run_in_background: true`) | `codex-api-surface` |

**Claude subagent launch:**

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: <focused research prompt for this angle>
  run_in_background: true
  name: "claude-<angle>"  (e.g. "claude-local-code", "claude-cross-repo")
  model: "haiku" or "opus"  (from Step 0)
```

**Codex launch:**

```bash
RESEARCH_DIR="/tmp/research-$(date +%s)" && mkdir -p "$RESEARCH_DIR" && codex exec --full-auto -m <model> -o "$RESEARCH_DIR/codex-<angle>.md" "<focused research prompt>"
```

Use the Codex model from `shared:complexity-assessment` based on Step 0.

If in a git repo, add `-C /path/to/repo`. If NOT in a repo, add `--skip-git-repo-check`.

Use `run_in_background: true` on the Bash tool call. Use distinct output files per angle: `codex-data-flow.md`, `codex-api-surface.md`, etc.

**Codex fallback:** If Codex is unavailable (command not found), use a Claude subagent instead with the same prompt. See `shared:codex-dispatch` for the full pattern.

**Output validation:** After Codex completes, verify the output file exists and is non-empty before reading. If missing or empty, note the failure and synthesize from remaining agents.

### Step 4: Collect and synthesize

Once all researchers complete:

1. Read Codex outputs from `$RESEARCH_DIR/codex-*.md` (named by angle)
2. Claude subagent results come back directly

Combine all findings into a single answer:

1. **Consensus** — Facts multiple researchers agree on (highest confidence)
2. **Unique findings** — Insights only one researcher found
3. **Conflicts** — Where they disagree (investigate these yourself before presenting)
4. **Gaps** — Questions no one could answer

When multiple researchers find the same thing, consolidate — don't repeat the same evidence three times. Credit the finding once and note that multiple researchers confirmed it.

Present the synthesis directly to the user. Lead with the answer, then supporting evidence.

### Step 5: Save output

Save the synthesized report to `$RESEARCH_DIR/synthesis.md` for reference.

## Tips

- If one researcher fails, synthesize from the others — partial results are still valuable.
- For cross-repo questions, make sure at least one Claude subagent's prompt explicitly says to use codesearch MCP (`search_code` tool).
- For questions about a specific repo, point Codex at it with `-C`.
- If a researcher hangs or returns empty/garbage, note it in synthesis and move on. Don't block the whole research on one failing agent.
- If Codex is unavailable, fall back to Claude subagents. See `shared:codex-dispatch`.
