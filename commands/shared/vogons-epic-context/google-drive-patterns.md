# Google Drive MCP — Document Reading Patterns

## Tools Available

- `get_document_structure(fileId)` — sections list with previews. Use first.
- `get_document_section(fileId, sectionIds?, sectionIndex?)` — full content of specific sections
- `get_document_preview(fileId)` — first 1000 chars. Fallback if structure fails.
- `get_drive_file_content(fileId, offset?, limit?)` — raw content, 1000 chars per call

## Workflow

1. Call `get_document_structure` to see all sections with titles and previews
2. Scan section titles/previews for Vogons-relevant keywords:
   - "vogons", "MDS", "content control", "deflector", "CCL"
   - The epic title or DoD title
   - "managed accounts", "content rating", "availability"
3. Call `get_document_section` with only the relevant `sectionIds`
4. If structure call fails with "too large to export", try `get_document_preview`

## Extracting Doc IDs from URLs

Google Doc URLs look like:

```
https://docs.google.com/document/d/1YcbzEGwF0MYIefJT6apMrkbFAcqilYr4rguallhEFUs/edit?tab=t.0#heading=h.xxx
```

The doc ID is between `/d/` and `/edit`: `1YcbzEGwF0MYIefJT6apMrkbFAcqilYr4rguallhEFUs`

Jira markup format:

```
[link text|https://docs.google.com/document/d/DOC_ID/edit...]
```

## Tips

- Batch `sectionIds` into a single `get_document_section` call — up to 8 sections per call
- Skip sections about other squads (Presto, Artemis, etc.) unless they're cross-cutting
- Discovery Day docs are massive with many initiatives — only read the section matching the epic
- Some docs may require account linking — if you get a 403, note it and move on
