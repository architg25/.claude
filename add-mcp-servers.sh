#!/bin/bash

# Script to add MCP servers to Claude Code

echo "Adding MCP servers to Claude Code"
echo "==================================="
echo ""

# Add Google Drive MCP
echo "Adding google-drive-mcp..."
claude mcp add --transport http --scope user google-drive-mcp https://mcp-gateway.spotify.net/google-drive-mcp

# Add Code Search MCP
echo "Adding code-search-mcp..."
claude mcp add --transport http --scope user code-search-mcp https://mcp-gateway.spotify.net/code-search-mcp

# Add Atlassian MCP
echo "Adding atlassian-mcp..."
claude mcp add --transport http --scope user atlassian-mcp https://mcp-gateway.spotify.net/atlassian-mcp

# Add Aika Search MCP
echo "Adding aika-search-mcp..."
claude mcp add --transport http --scope user aika-search-mcp https://mcp-gateway.spotify.net/aika-search-mcp

# Oliver MCP removed - replaced by o11y-agg-mcp (its official successor)

# Add Honk Coding Agent MCP
echo "Adding honk-coding-agent-mcp..."
claude mcp add --transport http --scope user honk-coding-agent-mcp https://mcp-gateway.spotify.net/honk-coding-agent

# Add Cloud Logging MCP
echo "Adding cloud-logging-mcp..."
claude mcp add --transport http --scope user cloud-logging-mcp https://mcp-gateway.spotify.net/cloud-logging-mcp

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

# Nameless Callgraph removed - subsumed by o11y-agg-mcp's dependency tools

# Add Observability Aggregation MCP
echo "Adding o11y-agg-mcp..."
claude mcp add --transport http --scope user o11y-agg-mcp https://mcp-gateway.spotify.net/o11y-agg-mcp

echo ""
echo "All MCP servers added successfully!"
