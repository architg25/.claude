---
name: vogons-epic-context
description: >-
  Gather full context for a Vogons squad epic from Jira, Groove, and Google Docs,
  and optionally generate a Jira-ready summary for the epic description.
  Use when the user provides a Jira key (e.g. CONACCESS-5), epic title, or asks
  "what does vogons need to do for [epic]", "get context on [epic]", "summarize
  epic [key]", "write epic summary", "generate jira description", or wants to
  understand what work an epic entails including its parent DoD and Initiative.
  Pulls from atlassian-mcp, groove-mcp, and google-drive-mcp to build a full
  picture.
---

# Vogons Epic Context

Gather and synthesize context for a Vogons epic across Jira, Groove (Work Graph), and linked Google Docs.

## Cached Schemas & Subagent Prompts

**IMPORTANT**: Do NOT call `get-type-definition`, `get-available-queries`, or `get-graphql-schema` on groove-mcp. All schemas, query templates, and subagent prompts are cached in `references/`:

- `groove-queries.md` — Groove GraphQL schema, query templates, pitfalls
- `jira-patterns.md` — JQL patterns, response field reference
- `google-drive-patterns.md` — doc reading workflow, ID extraction
- `subagent-*.md` — prompt templates for each phase's subagent
- `jira-summary-template.md` — Jira description format

Subagents should read the relevant reference files themselves.

## Input

User provides one of:

- Jira key (e.g. `CONACCESS-5`)
- Epic title or keyword (e.g. "Availability Catalog Trait")
- Groove epic ID (e.g. `EPIC-62187`)

## Workflow

### Phase 0: Preflight MCP Check

Launch one `general-purpose` Task subagent with the prompt from `references/subagent-preflight.md`.

- If any server reports **LINKING_REQUIRED**, show linking URLs (only the failing ones):
  - Groove: `https://backstage.spotify.net/mcp-explorer/link/groove-mcp`
  - Jira: `https://backstage.spotify.net/mcp-explorer/link/atlassian-mcp`
  - Google Drive: `https://backstage.spotify.net/mcp-explorer/link/google-drive-mcp`
    Wait for user confirmation, then re-check only the previously failing servers.
- If **ERROR**, note it and proceed without that source (Groove alone can produce useful output).
- If all **OK**, proceed to Phase 1.

### Phase 1: Parallel Data Gathering

Launch **two** `general-purpose` Task subagents in a **single message** (parallel):

1. **Jira Context** — prompt from `references/subagent-jira.md` (substitute `{JIRA_KEY}` / `{keyword}`)
2. **Groove Context** — prompt from `references/subagent-groove.md` (substitute `{JIRA_KEY}`)

### Phase 2: Google Docs

After Subagent 2 returns with doc IDs, launch one `general-purpose` Task subagent with the prompt from `references/subagent-gdocs.md` (substitute doc IDs and epic/DoD titles).

If doc IDs are already known from conversation history, launch this in parallel with Phase 1.

### Phase 3: Synthesis

Combine all subagent results into this structure:

```
## Initiative: {title} ({id})
## DoD: {title} ({id})
## Epic: {title} ({id})
## What Vogons Needs to Do
## Key References
```

Include owners, statuses, dates, descriptions, sibling epics, and concrete deliverables.

### Phase 4: Jira Epic Summary

1. Read `references/jira-summary-template.md` and format the Phase 3 data into it.
2. Present the formatted summary to the user in a code block for review.
3. Ask: "Want me to write this to the Jira epic `{JIRA_KEY}`?"
4. If yes, launch a subagent with the prompt from `references/subagent-jira-write.md`.
   - If **WRITTEN**: confirm success.
   - If **EXISTING_CONTENT**: ask "Replace it or append below it?" Then launch a subagent with `references/subagent-jira-overwrite.md`.
   - If **ERROR**: report to user.

## Quick Reference

- Vogons org UUID: `6d0f330f-73ce-4128-866e-107a88d16b47`
- Vogons Jira project: `CONACCESS`
- Always filter `deleted: [false]` in Groove queries
- Doc IDs: segment between `/d/` and next `/` in Google Doc URLs
