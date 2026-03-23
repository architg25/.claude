#!/bin/bash

# Script to add MCP servers to Claude Code

echo "Adding MCP servers to Claude Code"
echo "==================================="
echo ""

# Add Context7 MCP
echo "Adding context7..."
claude mcp add --transport http --scope user context7 https://mcp.context7.com/mcp

# sequential-thinking: REMOVED — unused
# aika-search: REMOVED — duplicate of claude.ai AiKA Search MCP

# Add Code Search MCP
echo "Adding code-search..."
claude mcp add --transport http --scope user code-search http://code-search-mcp.services.gew1.spotify.net/mcp/

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
# o11y-agg-mcp: REMOVED — unused
# google-drive-mcp: REMOVED — duplicate of claude.ai GDrive MCP
# honk-coding-agent-mcp: REMOVED
# component-metadata-mcp: REMOVED
# dataplatform: REMOVED
# deployments-mcp: REMOVED
# grodor-mcp: REMOVED

# Add Groove MCP
echo "Adding groove-mcp..."
claude mcp add --transport http --scope user groove-mcp https://mcp-gateway.spotify.net/groove-mcp

# Add Oliver MCP
echo "Adding oliver..."
claude mcp add --transport http --scope user oliver https://mcp-gateway.spotify.net/oliver

# Add Text2SQL MCP
echo "Adding text2sql-mcp..."
claude mcp add --transport http --scope user text2sql-mcp https://mcp-gateway.spotify.net/text2sql-mcp

# Add Dynamo MCP (gRPC service discovery/calling)
echo "Adding dynamo-mcp..."
claude mcp add dynamo-mcp --scope user -- uvx --index-url https://artifactory.spotify.net/artifactory/api/pypi/pypi/simple/ dynamo-mcp

echo ""
echo "All MCP servers added successfully!"
