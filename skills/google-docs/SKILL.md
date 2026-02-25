---
name: google-docs
description: Create, read, and modify Google Documents. Converts markdown to Google Docs with full formatting support, with optional visual formatting validation via screenshot comparison. Use when the user wants to create, edit, update, or collaborate on Google Docs - particularly for RFCs, plans, and technical documents.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Google Docs Skill

This skill enables full CRUD operations on Google Documents:

- **Create** new docs from markdown with formatting
- **Read** existing docs via MCP tools or script
- **Update** docs with text, formatting, and structural changes
- **Append** markdown content to existing documents

## Prerequisites

Before using this skill, ensure:

1. **Pandoc is installed**: `brew install pandoc`
2. **jq is installed**: `brew install jq`
3. **Python packages are installed**:
   ```bash
   pip install google-auth google-auth-httplib2 google-api-python-client
   ```
4. **Google Cloud credentials are configured**:
   ```bash
   gcloud auth application-default login \
     --scopes=https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/cloud-platform
   ```
5. **Google APIs are enabled**:
   ```bash
   gcloud services enable drive.googleapis.com docs.googleapis.com
   ```

## Reading Documents

### Via MCP Tools (Recommended for Claude)

```
mcp__google-drive-mcp__get_document_structure(fileId: "DOC_ID")
mcp__google-drive-mcp__get_document_section(fileId: "DOC_ID", sectionIds: [...])
mcp__google-drive-mcp__get_document_preview(fileId: "DOC_ID")
mcp__google-drive-mcp__get_drive_file_content(fileId: "DOC_ID", offset: 0, limit: 1000)
```

### Via Script (for raw JSON with indices)

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py read DOC_ID
python ~/.claude/skills/google-docs/scripts/gdocs.py read DOC_ID --tab TAB_ID
python ~/.claude/skills/google-docs/scripts/gdocs.py list-tabs DOC_ID
```

### Via Bash Helper (quick access)

```bash
gdocs get DOC_ID --tabs > /tmp/doc.json
```

## Creating Documents

### From Markdown (Full Featured)

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py create file.md
python ~/.claude/skills/google-docs/scripts/gdocs.py create file.md --name "Custom Title"
python ~/.claude/skills/google-docs/scripts/gdocs.py create file.md --folder FOLDER_ID
```

Features included:

- Custom fonts (Proxima Nova for text, Consolas for code)
- Table styling (1pt borders, grey header backgrounds)
- Blockquote italicization

### Empty Document (Quick)

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py create-empty "Document Title"
# or
gdocs create "Document Title"
```

## Editing Existing Documents

### Append Markdown to Existing Doc

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py append DOC_ID content.md
python ~/.claude/skills/google-docs/scripts/gdocs.py append DOC_ID content.md --tab TAB_ID
```

This will:

1. Convert to plain text with formatting instructions
2. Insert at the end of the document (or specified tab)
3. Apply formatting (headings, bold, italic, etc.)

### Replace Text

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py replace DOC_ID "find text" "replace text"
python ~/.claude/skills/google-docs/scripts/gdocs.py replace DOC_ID "{{PLACEHOLDER}}" "actual value" --tab TAB_ID
# or
gdocs replace DOC_ID "find" "replace" --tab TAB_ID
```

### Insert Text at Position

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py insert DOC_ID "new text" --index 42
python ~/.claude/skills/google-docs/scripts/gdocs.py insert DOC_ID "new text" --index 42 --tab TAB_ID
# or
gdocs insert-text DOC_ID "text" --index 42 --tab TAB_ID
```

### Complex Updates (batchUpdate)

For advanced operations, write requests to a JSON file and apply:

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py update DOC_ID /tmp/changes.json
# or
gdocs update DOC_ID /tmp/changes.json
```

## Working with Tabs

### List All Tabs

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py list-tabs DOC_ID
```

Output:

```
Tab ID              Title           Level
t.abc123            Main            0
t.def456            Appendix        0
t.ghi789            Details         1
```

### Target Specific Tab

Include `--tab TAB_ID` in any command:

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py append DOC_ID content.md --tab t.abc123
python ~/.claude/skills/google-docs/scripts/gdocs.py replace DOC_ID "old" "new" --tab t.abc123
```

### Tab Limitations (API Constraints)

- Can READ all tabs
- Can EDIT content in any tab
- CANNOT create new tabs (UI only)
- CANNOT delete tabs (UI only)
- CANNOT rename tabs (UI only)

## Markdown to Google Docs Translation

| Markdown         | Google Docs Style |
| ---------------- | ----------------- |
| `# Title`        | TITLE             |
| `## Heading`     | HEADING_1         |
| `### Subheading` | HEADING_2         |
| `#### Minor`     | HEADING_3         |
| `**bold**`       | Bold text         |
| `*italic*`       | Italic text       |
| `~~strike~~`     | Strikethrough     |
| `` `code` ``     | Consolas font     |
| `[link](url)`    | Hyperlink         |
| `- item`         | Bullet list       |
| `1. item`        | Numbered list     |

## Example Workflows

### Workflow 1: Create RFC from Markdown

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py create rfcs/my-rfc.md --name "RFC: Feature X"
```

### Workflow 2: Add Section to Existing Doc

```bash
python ~/.claude/skills/google-docs/scripts/gdocs.py append 1abc...xyz new-section.md
```

### Workflow 3: Update Template Placeholders

```bash
gdocs replace DOC_ID "{{AUTHOR}}" "John Smith"
gdocs replace DOC_ID "{{DATE}}" "2025-01-15"
gdocs replace DOC_ID "{{VERSION}}" "1.0"
```

### Workflow 4: Edit Specific Tab

```bash
# List tabs first
python ~/.claude/skills/google-docs/scripts/gdocs.py list-tabs DOC_ID

# Append to specific tab
python ~/.claude/skills/google-docs/scripts/gdocs.py append DOC_ID notes.md --tab t.appendix123
```

## Visual Formatting Validation (Optional Sub-workflow)

Use this when you need to verify that a Google Doc visually matches the source markdown after creation or formatting changes. Useful for high-fidelity documents like RFCs where formatting accuracy matters.

@visual-formatting.md

## Troubleshooting

### Missing Dependencies

```bash
pip install google-auth google-auth-httplib2 google-api-python-client
brew install pandoc jq
```

### Authentication Errors

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/cloud-platform
```

## Script Locations

- **Main script**: `~/.claude/skills/google-docs/scripts/gdocs.py`
- **Bash helper**: `~/.claude/skills/google-docs/scripts/gdocs`
- **Visual formatting scripts**: `~/.claude/skills/google-docs/scripts/visual-formatting/`

## API Limitations

| Feature       | Status     | Workaround                                 |
| ------------- | ---------- | ------------------------------------------ |
| Create tabs   | Not in API | Create template via UI, copy via Drive API |
| Delete tabs   | Not in API | Manual via UI                              |
| Pageless mode | Not in API | None available                             |
| Rename tabs   | Not in API | Manual via UI                              |
