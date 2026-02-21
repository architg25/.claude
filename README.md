# .claude
My claude files

## MCP Servers

I have some MCP servers I use for various tasks

```
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking -s user
claude mcp add --transport http context7 https://mcp.context7.com/sse -s user
claude mcp add --transport http aika-search http://aika-search-mcp.services.gew1.spotify.net/mcp/ -s user
claude mcp add --transport http code-search http://code-search-mcp.services.gew1.spotify.net/mcp/ -s user
claude mcp add --transport http ghe-mcp https://ghe-mcp.spotify.net/mcp/ -s user
claude mcp add --transport http backstage-mcp-actions http://backstage-mcp-actions.services.gew1.spotify.net:7007/api/mcp-actions/v1 -s user
claude mcp add --transport http --scope user atlassian-mcp https://mcp-gateway.spotify.net/atlassian-mcp
claude mcp add --transport http bigquery-mcp https://mcp-gateway.spotify.net/bigquery-mcp -s user
claude mcp add --transport http cloud-logging-mcp https://mcp-gateway.spotify.net/cloud-logging-mcp -s user
claude mcp add --transport http context-mcp https://mcp-gateway.spotify.net/context-mcp -s user
claude mcp add --transport http google-calendar-mcp https://mcp-gateway.spotify.net/google-calendar-mcp -s user
claude mcp add --transport http o11y-agg-mcp https://mcp-gateway.spotify.net/o11y-agg-mcp -s user
```

## Plugins

Has some useful agents/custom commands I'm testing

```shell
/plugin marketplace add anthropics/claude-code
/plugin install feature-dev
/plugin install pr-review-toolkit
/plugin install commit-commands
/plugin install agent-sdk-dev

/plugin marketplace add thedotmack/claude-mem 
/plugin install claude-mem 
```
