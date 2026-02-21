# .claude
My claude files

## MCP Servers

I have some MCP servers I use for various tasks

```
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking -s user
claude mcp add --transport http context7 https://mcp.context7.com/sse -s user
claude mcp add --transport http aika-search https://mcp-gateway.spotify.net/aika-search-mcp -s user
claude mcp add --transport http code-search https://mcp-gateway.spotify.net/code-search-mcp -s user
claude mcp add --transport http ghe-mcp https://ghe-mcp.spotify.net/mcp/ -s user
claude mcp add --transport http backstage-mcp-actions http://backstage-mcp-actions.services.gew1.spotify.net:7007/api/mcp-actions/v1 -s user
claude mcp add --transport http atlassian-mcp https://mcp-gateway.spotify.net/atlassian-mcp -s user
claude mcp add --transport http bigquery-mcp https://mcp-gateway.spotify.net/bigquery-mcp -s user
claude mcp add --transport http cloud-logging-mcp https://mcp-gateway.spotify.net/cloud-logging-mcp -s user
claude mcp add --transport http context-mcp https://mcp-gateway.spotify.net/context-mcp -s user
claude mcp add --transport http google-calendar-mcp https://mcp-gateway.spotify.net/google-calendar-mcp -s user
claude mcp add --transport http o11y-agg-mcp https://mcp-gateway.spotify.net/o11y-agg-mcp -s user
claude mcp add --transport http google-drive-mcp https://mcp-gateway.spotify.net/google-drive-mcp -s user
claude mcp add --transport http honk-coding-agent-mcp https://mcp-gateway.spotify.net/honk-coding-agent -s user
claude mcp add --transport http component-metadata-mcp https://mcp-gateway.spotify.net/component-metadata-mcp -s user
claude mcp add --transport http dataplatform https://mcp-gateway.spotify.net/dataplatform -s user
claude mcp add --transport http deployments-mcp https://mcp-gateway.spotify.net/deployments-mcp -s user
claude mcp add --transport http grodor-mcp https://mcp-gateway.spotify.net/grodor-mcp -s user
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
