---
name: code-research
description: "Use when the user wants to research how something works in the codebase, trace data flows, find implementations, or answer technical questions about services and systems. Triggers on questions like 'how does X work', 'where is Y defined', 'trace the flow of Z'."
---

# Research

Dispatch multiple parallel researchers (Claude subagents + Codex instances) to investigate a question from different angles, then synthesize findings.

## Usage

```
/research <question>
```

## Instructions

### Step 0: Assess complexity and select models

Before decomposing, assess the question complexity to choose appropriate models.

**Simple** — single-hop lookups, "where is X defined", "what config does Y use", "find usages of Z":

- Claude subagents: `model: "sonnet"`
- Codex: `-m gpt-5.4-mini`

**Complex** — multi-service data flows, "how does X get from A to B", architectural questions, tracing through multiple repos:

- Claude subagents: `model: "opus"`
- Codex: `-m gpt-5.4`

**Signals for complex:** multiple services/repos involved, requires tracing data flows, needs to understand architectural decisions, cross-team boundaries, or the user explicitly says "deep dive" / "thorough".

**When unsure, default to complex.** Better to overshoot on model quality than miss findings.

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

**Researcher assignment strategy:**

| Researcher      | Tool                                          | Best for                                   |
| --------------- | --------------------------------------------- | ------------------------------------------ |
| Claude subagent | Agent tool (`run_in_background: true`)        | Local code (Glob, Grep, Read)              |
| Claude subagent | Agent tool (`run_in_background: true`)        | Codesearch MCP (`search_code`), cross-repo |
| Codex instance  | Bash `codex exec` (`run_in_background: true`) | Independent codebase exploration           |
| Codex instance  | Bash `codex exec` (`run_in_background: true`) | Second exploration angle                   |

Assign angles to researchers based on what tools they need. Claude subagents get MCP and local tools. Codex gets independent exploration.

**Claude subagent launch:**

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: <focused research prompt for this angle>
  run_in_background: true
  name: "researcher-1"  (use descriptive names like "researcher-local-code")
  model: "haiku" or "opus"  (from Step 0)
```

**Codex launch:**

```bash
mkdir -p /tmp/research && codex exec --full-auto -m <model> -o /tmp/research/codex-1.md "<focused research prompt>"
```

Use `-m gpt-5.4-mini` or `-m gpt-5.4` based on Step 0.

If in a git repo, add `-C /path/to/repo`. If NOT in a repo, add `--skip-git-repo-check`.

Use `run_in_background: true` on the Bash tool call. Use distinct output files: `codex-1.md`, `codex-2.md`.

### Step 4: Collect and synthesize

Once all researchers complete:

1. Read Codex outputs from `/tmp/research/codex-*.md`
2. Claude subagent results come back directly

Combine all findings into a single answer:

1. **Consensus** — Facts multiple researchers agree on (highest confidence)
2. **Unique findings** — Insights only one researcher found
3. **Conflicts** — Where they disagree (investigate these yourself before presenting)
4. **Gaps** — Questions no one could answer

Present the synthesis directly to the user. Lead with the answer, then supporting evidence.

### Step 5: Save output

Save the synthesized report to `/tmp/research/synthesis.md` for reference.

## Tips

- 3-4 total researchers is the sweet spot. More adds synthesis overhead without proportional value.
- If one researcher fails, synthesize from the others — partial results are still valuable.
- For cross-repo questions, make sure at least one Claude subagent's prompt explicitly says to use codesearch MCP (`search_code` tool).
- For questions about a specific repo, point Codex at it with `-C`.
