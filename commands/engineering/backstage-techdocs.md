---
description: Read Backstage techdocs by URL. Use when a user pastes a Backstage URL (https://backstage.spotify.net/docs/...) and wants to read, navigate, or search the documentation.
---

# Backstage TechDocs Reader

Read Backstage techdocs by converting URLs to Code Search MCP queries.

## URL Patterns

- **Shorthand**: `https://backstage.spotify.net/docs/<name>`
- **Full**: `https://backstage.spotify.net/docs/<namespace>/<kind>/<name>`

Extract the component name from the last path segment.

## Step 1: Find Source Repository

```
mcp__code-search-mcp__search_code(
  query = '"name: <component-name>" f:catalog-info.yaml',
  output_mode = "content"
)
```

Extract the repository name from results (format: `owner/repo-name`).

## Step 2: Read Main Documentation

```
mcp__code-search-mcp__read_file("docs/index.md", "<repo-name>")
```

**Fallback order** if index.md not found:

1. `docs/README.md`
2. `README.md` (root)
3. List all markdown: `mcp__code-search-mcp__search_code("", repo="<repo>", lang="markdown")`

## Step 3: Fallback for Private Repos

If Code Search returns no results, use Aika MCP:

```
mcp__claude_ai_AiKA_Search_MCP__spotify_internal_search(
  query = "<component-name>",
  data_source = "techdocs"
)
```

Note: Aika returns indexed content, not raw markdown.

## Navigating to Specific Pages

When the user asks for a specific section or page:

1. **List available pages**:

   ```
   mcp__code-search-mcp__search_code("", repo="<repo>", lang="markdown")
   ```

2. **Read the specific page**:
   ```
   mcp__code-search-mcp__read_file("docs/<page-name>.md", "<repo>")
   ```

Common page patterns:

- `docs/getting-started.md` or `docs/getting-started/index.md`
- `docs/api-reference.md` or `docs/api/index.md`
- `docs/configuration.md`

## Searching Within Docs

When the user wants to find specific content:

```
mcp__code-search-mcp__search_code(
  query = "<search-term>",
  repo = "<repo>",
  lang = "markdown",
  output_mode = "content"
)
```

## Examples

### Example 1: Read docs from URL

**User**: "Read https://backstage.spotify.net/docs/spcurl-cli"

1. Extract: `spcurl-cli`
2. Search: `"name: spcurl-cli" f:catalog-info.yaml` → finds `ads/spcurl-cli`
3. Read: `docs/index.md` from `ads/spcurl-cli`

### Example 2: Navigate to specific page

**User**: "Show me the getting started section"

1. Search: `"" repo:ads/spcurl-cli lang:markdown` to list pages
2. Read: `docs/getting-started.md` or similar

### Example 3: Search within docs

**User**: "Find authentication info in the docs"

1. Search: `"authentication" repo:ads/spcurl-cli lang:markdown`
2. Return matching sections with file:line references
