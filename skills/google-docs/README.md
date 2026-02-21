# Google Docs Skill

A comprehensive Claude Code skill for creating, reading, and modifying Google Documents.

## Features

- **Create** documents from markdown with automatic diagram rendering
- **Read** existing documents (structure, content, tabs)
- **Edit** documents (insert, replace, format, append)
- **Multi-tab** support for reading and editing
- **Custom formatting** (Proxima Nova text, Consolas code, styled tables)

## Quick Start

### Prerequisites

```bash
# Install dependencies
brew install pandoc jq
pip install google-auth google-auth-httplib2 google-api-python-client

# Configure Google Cloud
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/cloud-platform
gcloud services enable drive.googleapis.com docs.googleapis.com
```

### Installation

```bash
# The skill should already be at ~/.claude/skills/google-docs/
# Verify:
ls ~/.claude/skills/google-docs/

# Add bash helper to PATH (optional)
ln -s ~/.claude/skills/google-docs/scripts/gdocs ~/.local/bin/gdocs
```

### Add Auto-Approve Permissions

Add to `~/.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(gdocs:*)",
      "Bash(jq:*)"
    ]
  }
}
```

## Usage Examples

```bash
# Create from markdown
python ~/.claude/skills/google-docs/scripts/gdocs.py create document.md

# Read document
python ~/.claude/skills/google-docs/scripts/gdocs.py read DOC_ID

# Append markdown to existing doc
python ~/.claude/skills/google-docs/scripts/gdocs.py append DOC_ID more-content.md

# Replace text
python ~/.claude/skills/google-docs/scripts/gdocs.py replace DOC_ID "old" "new"

# List tabs
python ~/.claude/skills/google-docs/scripts/gdocs.py list-tabs DOC_ID
```

## Command Reference

| Command | Description |
|---------|-------------|
| `create <file.md>` | Create new doc from markdown |
| `create-empty <title>` | Create empty document |
| `read <doc_id>` | Read document content |
| `list-tabs <doc_id>` | List all tabs in document |
| `append <doc_id> <file.md>` | Append markdown to existing doc |
| `replace <doc_id> <find> <replace>` | Replace all occurrences |
| `insert <doc_id> <text>` | Insert text at position |
| `update <doc_id> <json_file>` | Apply batchUpdate from JSON |

## See Also

- [SKILL.md](./SKILL.md) - Full skill instructions for Claude
- [Google Docs API Reference](https://developers.google.com/docs/api/reference/rest)
