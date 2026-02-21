#!/bin/bash

# Script to add MCP servers to Claude Code

echo "Adding MCP servers to Claude Code"
echo "==================================="
echo ""

# Add Sequential Thinking MCP
echo "Adding sequential-thinking..."
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking -s user

# Add Context7 MCP
echo "Adding context7..."
claude mcp add --transport http --scope user context7 https://mcp.context7.com/sse

# Add Aika Search MCP
echo "Adding aika-search..."
claude mcp add --transport http --scope user aika-search https://mcp-gateway.spotify.net/aika-search-mcp

# Add Code Search MCP
echo "Adding code-search..."
claude mcp add --transport http --scope user code-search https://mcp-gateway.spotify.net/code-search-mcp

# Add GHE MCP
echo "Adding ghe-mcp..."
claude mcp add --transport http --scope user ghe-mcp https://ghe-mcp.spotify.net/mcp/

# Add Backstage MCP Actions
echo "Adding backstage-mcp-actions..."
claude mcp add --transport http --scope user backstage-mcp-actions http://backstage-mcp-actions.services.gew1.spotify.net:7007/api/mcp-actions/v1

# Add Atlassian MCP
echo "Adding atlassian-mcp..."
claude mcp add --transport http --scope user atlassian-mcp https://mcp-gateway.spotify.net/atlassian-mcp

# Add BigQuery MCP
echo "Adding bigquery-mcp..."
claude mcp add --transport http --scope user bigquery-mcp https://mcp-gateway.spotify.net/bigquery-mcp

# Add Cloud Logging MCP
echo "Adding cloud-logging-mcp..."
claude mcp add --transport http --scope user cloud-logging-mcp https://mcp-gateway.spotify.net/cloud-logging-mcp

# Add Context MCP
echo "Adding context-mcp..."
claude mcp add --transport http --scope user context-mcp https://mcp-gateway.spotify.net/context-mcp

# Add Google Calendar MCP
echo "Adding google-calendar-mcp..."
claude mcp add --transport http --scope user google-calendar-mcp https://mcp-gateway.spotify.net/google-calendar-mcp

# Add Observability Aggregation MCP
echo "Adding o11y-agg-mcp..."
claude mcp add --transport http --scope user o11y-agg-mcp https://mcp-gateway.spotify.net/o11y-agg-mcp

# Add Google Drive MCP
echo "Adding google-drive-mcp..."
claude mcp add --transport http --scope user google-drive-mcp https://mcp-gateway.spotify.net/google-drive-mcp

# Add Honk Coding Agent MCP
echo "Adding honk-coding-agent-mcp..."
claude mcp add --transport http --scope user honk-coding-agent-mcp https://mcp-gateway.spotify.net/honk-coding-agent

# Add Component Metadata MCP
echo "Adding component-metadata-mcp..."
claude mcp add --transport http --scope user component-metadata-mcp https://mcp-gateway.spotify.net/component-metadata-mcp

# Add Data Platform MCP
echo "Adding dataplatform..."
claude mcp add --transport http --scope user dataplatform https://mcp-gateway.spotify.net/dataplatform

# Add Deployments MCP
echo "Adding deployments-mcp..."
claude mcp add --transport http --scope user deployments-mcp https://mcp-gateway.spotify.net/deployments-mcp

# Add Grodor MCP (Kubernetes resources)
echo "Adding grodor-mcp..."
claude mcp add --transport http --scope user grodor-mcp https://mcp-gateway.spotify.net/grodor-mcp

echo ""
echo "All MCP servers added successfully!"
