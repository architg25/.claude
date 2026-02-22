# Subagent Prompt: Preflight MCP Check

Verify all three MCP servers are accessible by making these calls in parallel:

1. mcp**groove-mcp**get-auth-status — no params
2. mcp**atlassian-mcp**list_tickets — jql_query: "key = CONACCESS-1", max_results: 1
3. mcp**google-drive-mcp**list_drive_files — query: "test", maxResults: 1

Return a short status report in exactly this format:

- groove: OK | LINKING_REQUIRED | ERROR: {reason}
- jira: OK | LINKING_REQUIRED | ERROR: {reason}
- gdrive: OK | LINKING_REQUIRED | ERROR: {reason}

Nothing else. No raw API responses.
