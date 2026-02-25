---
description: Save documents to local archive at ~/Git/documents-archive/. Use when the user shares an Excalidraw link (excalidraw.com/#json=...), a Google Doc URL (docs.google.com/document/...), provides an .excalidraw file, or asks to save/archive/store a document.
allowed-tools: [Bash, Read]
---

# Document Archive

Save documents to `~/Git/documents-archive/` organized by type, with `.meta.json` sidecars.

Script: `~/.claude/commands/shared/document-archive/archive.py`

## Excalidraw Workflow

### Step 1: Analyze

```bash
python3 ~/.claude/commands/shared/document-archive/archive.py excalidraw --analyze "<url-or-file>"
```

### Step 2: Generate title and description from the analysis

1. **Title**: Short kebab-case filename (2-5 words). Use largest text elements as signals.
2. **Description**: 1-2 sentence summary.
3. **Initiative**: If identifiable from the content, include the initiative/project name.

### Step 3: Save

```bash
python3 ~/.claude/commands/shared/document-archive/archive.py excalidraw "<url-or-file>" "<name>" --description "<desc>" --tags "<tags>" --initiative "<initiative>"
```

## Google Doc Workflow

Google Docs are saved as **bookmarks only** (metadata, no content snapshot) since they're living documents.

### Reading docs

Use the google-docs skill script (NOT MCP) to read documents — this runs via Bash and works in subagents:

```bash
python3 ~/.claude/skills/google-docs/scripts/gdocs.py read <doc-id>
```

Extract the doc ID from the URL: `https://docs.google.com/document/d/<doc-id>/edit`

### Single doc save

1. Read the doc with `gdocs.py read <doc-id>`
2. From the content, generate:
   - **Title**: Short kebab-case filename derived from the doc title
   - **Description**: 1-2 sentence summary
   - **Initiative**: Look for Groove initiative references (INIT-xxx), project names, or bet references
3. Save:

```bash
python3 ~/.claude/commands/shared/document-archive/archive.py google-doc "<name>" \
  --source "https://docs.google.com/document/d/<doc-id>/edit" \
  --title "<doc title>" \
  --description "<desc>" \
  --tags "<tags>" \
  --initiative "<initiative>"
```

This creates only a `.meta.json`. The source link points to the live doc.

### Batch saving multiple docs

When saving many Google Docs at once, **use parallel subagents** (via the Task tool with `run_in_background: true`):

1. Split docs into batches of 5
2. Launch one subagent per batch — each agent reads docs via `gdocs.py read`, generates metadata, and runs `archive.py google-doc` for each
3. After all agents complete, run `archive.py index` to regenerate the README
4. Commit and push

Each subagent prompt should include the doc IDs, titles, and meta paths, and instruct it to:

- Read each doc with: `python3 ~/.claude/skills/google-docs/scripts/gdocs.py read <doc-id>`
- Generate a 1-sentence description and identify initiatives
- Save with: `python3 ~/.claude/commands/shared/document-archive/archive.py google-doc ...`

### Skip analysis when user provides a name

If the user explicitly provides a name, skip the read step and save directly.

## After saving

Tell the user:

- File path and generated title
- Description and initiative (if identified)
- For Excalidraw: the `.excalidraw` file opens directly at excalidraw.com via File > Open
- The original link is preserved in `.meta.json` for re-sharing

## Meta.json schema

```json
{
  "title": "Human Readable Title",
  "description": "1-2 sentence summary",
  "source": "original URL or file path",
  "type": "excalidraw | google-doc",
  "saved": "YYYY-MM-DD",
  "tags": ["tag1", "tag2"],
  "initiative": "Initiative Name or ID"
}
```

## Dependencies

Requires `cryptography` Python package for Excalidraw decryption (`pip3 install cryptography`).
