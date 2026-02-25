# Subagent Prompt: Google Docs Context

Read references/google-drive-patterns.md for the reading workflow.

For each Google Doc ID from Phase 1:

1. get_document_structure(fileId) to see sections
2. Scan section titles/previews for: "vogons", "MDS", the epic title,
   the DoD title, "content control", "deflector", "CCL", "managed accounts"
3. get_document_section(fileId, sectionIds) for only relevant sections
4. If structure fails (file too large), try get_document_preview instead

Skip docs clearly about other squads unless cross-cutting.
Return: key findings per doc, organized by doc title.
