# .claude
My claude files

## MCP Servers

I have some MCP servers I use for various tasks

```
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking -s user
claude mcp add --transport sse context7 https://mcp.context7.com/sse -s user
claude mcp add --transport http aika-search http://aika-search-mcp.services.gew1.spotify.net/mcp/ -s user
claude mcp add --transport http code-search http://code-search-mcp.services.gew1.spotify.net/mcp/ -s user
```

## Plugins

Has some useful agents/custom commands I'm testing

```shell
/plugin marketplace add anthropics/claude-code
/plugin install feature-dev
/plugin install pr-review-toolkit
/plugin install commit-commands
/plugin install agent-sdk-dev
```