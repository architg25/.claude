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

If you can answer it with one Grep or Glob, don't spawn 4 agents:

- "Where is class Foo defined?" → Grep
- "What files import X?" → Grep
- "Show me the config file" → Glob + Read

## Instructions

### Step 0: Assess complexity

Use `shared:complexity-assessment` for tier and model selection. This determines researcher count:

- **Simple:** 1-2 researchers
- **Complex:** 3-4 researchers

### Step 1: Decompose into research angles

Break the question into focused sub-questions. Each angle should be narrow enough to finish fast.

Example for "how does Padme get video files written to its DB":

- **Angle 1** (local code): Padme's DB write paths, models, storage layer
- **Angle 2** (cross-repo): upstream services/jobs that call Padme's write APIs
- **Angle 3** (data flow): video file from ingestion to DB row — transformations?

Common angle splits:

- **Local code** vs **cross-repo** (codesearch MCP)
- **Producer** vs **consumer** sides of a flow
- **Config/infra** vs **application code**
- **API surface** vs **internal implementation**

### Step 2: Build research prompts

For each angle:

```
RESEARCH ANGLE: <angle description>
CONTEXT: <user's original question>

You are a codebase researcher. Answer the angle above thoroughly.

- Search broadly first, then drill into specifics
- Look at actual code, not just file names
- Include file paths and line numbers for key findings
- Note any assumptions or gaps

Report:
1. **Summary** — Direct answer in 2-3 sentences
2. **Key Findings** — Detailed evidence with file paths
3. **Data Flow** — How data moves (if applicable)
4. **Open Questions** — What you couldn't determine
```

For cross-repo angles, explicitly tell the agent to use codesearch MCP (`search_code` tool).

### Step 3: Dispatch all researchers

Per `shared:dual-agent-dispatch`: launch Claude subagents + Codex instances in parallel, all in a single message.

**Minimum mix:** at least 1 Codex + 1 Claude subagent. For 3-4 researchers, use 2 of each.

Name each researcher: `claude-<angle>`, `codex-<angle>` (e.g., `claude-local-code`, `codex-data-flow`).

If in a git repo, add `-C /path/to/repo` to Codex. If NOT in a repo, add `--skip-git-repo-check`.

### Step 4: Synthesize

Per `shared:dual-agent-dispatch` synthesis pattern. Combine all findings:

1. **Consensus** — multiple researchers agree (highest confidence)
2. **Unique findings** — only one found it (include, note single-source)
3. **Conflicts** — investigate yourself before presenting
4. **Gaps** — what nobody could answer

Consolidate duplicate findings — don't repeat the same evidence from multiple researchers.

Present synthesis directly. Lead with the answer, then evidence. Save to `/tmp/research-<timestamp>/synthesis.md`.

## Tips

- One researcher fails? Synthesize from the others.
- For cross-repo questions, ensure at least one prompt mentions codesearch MCP.
- If a researcher returns empty/garbage, note it and move on. Don't block everything.
