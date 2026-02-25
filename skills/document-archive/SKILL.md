---
name: document-archive
description: Save documents to local archive at ~/Git/documents-archive/. Use when the user shares an Excalidraw link (excalidraw.com/#json=...), a Google Doc URL (docs.google.com/document/...), provides an .excalidraw file, or asks to save/archive/store a document.
allowed-tools: [Bash, Read]
---

# Document Archive

Saves documents to `~/Git/documents-archive/` organized by type, with `.meta.json` sidecars.

Script: `~/.claude/skills/document-archive/scripts/archive.py`

## Excalidraw Workflow

### Step 1: Analyze

```bash
python3 ~/.claude/skills/document-archive/scripts/archive.py excalidraw --analyze "<url-or-file>"
```

### Step 2: Generate title and description from the analysis

1. **Title**: Short kebab-case filename (2-5 words). Use largest text elements as signals.
2. **Description**: 1-2 sentence summary.
3. **Initiative**: If identifiable from the content, include the initiative/project name.

### Step 3: Save

```bash
python3 ~/.claude/skills/document-archive/scripts/archive.py excalidraw "<url-or-file>" "<name>" --description "<desc>" --tags "<tags>" --initiative "<initiative>"
```

## Google Doc Workflow

### Step 1: Read the document

Use the `get_document_structure` MCP tool to see sections:

```
mcp__google-drive-mcp__get_document_structure(fileId="<doc-id>")
```

Then use `get_document_section` to read all sections. Also use `get_drive_file_metadata` for the doc title.

### Step 2: Generate title, description, and identify initiative

From the document content:

1. **Title**: Short kebab-case filename derived from the doc title
2. **Description**: 1-2 sentence summary of the document's purpose
3. **Initiative**: Look for Groove initiative references (INIT-xxx), project names, or bet references

### Step 3: Export and save

Write the full document content as markdown to a temp file, then:

```bash
python3 ~/.claude/skills/document-archive/scripts/archive.py google-doc "<name>" \
  --content-file /tmp/doc-export.md \
  --source "https://docs.google.com/document/d/<doc-id>/edit" \
  --title "<doc title>" \
  --description "<desc>" \
  --tags "<tags>" \
  --initiative "<initiative>"
```

### Skip analysis when user provides a name

If the user explicitly provides a name, skip the analysis/generation steps.

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
