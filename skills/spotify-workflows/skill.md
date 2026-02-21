# Spotify Internal Workflows

## Statements MCP

**IMPORTANT**: The below tools should only be used if we need to debug an entity. There should be no reason to use them when doing feature development.

- You can use statements-cli to extract information about an entity like episode, show, audiobook and audiobookChapter, use -h and my zsh history to figure out commands
- You can use statements-mcp MCP server to extract information about an entity and also search through the catalogue
- **Only for debugging entities, not for feature development**

## Atlassian Server MCP

- If I ever ask information about a JIRA issue, assume it is for project CONACCESS
- Always hyperlink the ticket with the URL so I can go to it if need be, and show the current status next to it
- Pretty print the result as much as you can

## Backstage TechDocs URL Handling

When a user pastes a Backstage techdocs URL (`https://backstage.spotify.net/docs/...`):

1. **Extract component name** from URL path (last segment)
2. **Find source repo**: `mcp__code-search-mcp__search_code('"name: <component>" f:catalog-info.yaml')`
3. **Read docs**: `mcp__code-search-mcp__read_file("docs/index.md", "<repo>")`

Fallback: If Code Search fails, try `mcp__aika-search-mcp__spotify_internal_search(query="<component>", data_source="techdocs")`.

For full instructions, see the `backstage-techdocs` skill.
