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

# aika-search: REMOVED — duplicate of claude.ai AiKA Search MCP

# Add Code Search MCP
echo "Adding code-search..."
claude mcp add --transport http --scope user code-search https://mcp-gateway.spotify.net/code-search-mcp

# ghe-mcp: REMOVED — not loading (0 tools)
# backstage-mcp-actions: REMOVED — not loading (0 tools)

# Add Atlassian MCP
echo "Adding atlassian-mcp..."
claude mcp add --transport http --scope user atlassian-mcp https://mcp-gateway.spotify.net/atlassian-mcp

# bigquery-mcp: REMOVED — duplicate of claude.ai Big Query MCP

# Add Cloud Logging MCP
echo "Adding cloud-logging-mcp..."
claude mcp add --transport http --scope user cloud-logging-mcp https://mcp-gateway.spotify.net/cloud-logging-mcp

# Add Context MCP
echo "Adding context-mcp..."
claude mcp add --transport http --scope user context-mcp https://mcp-gateway.spotify.net/context-mcp

# google-calendar-mcp: REMOVED — not loading; calendar available via search_workplace_knowledge

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
