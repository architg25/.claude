#!/bin/bash
# Permission hook: single source of truth for all tool permissions.
# Replaces the permissions block in settings.json.
# Unmatched tools fall through to user prompt (exit 0, no JSON).

INPUT=$(cat)
TOOL=$(jq -r '.tool_name' <<< "$INPUT")

allow() {
  jq -n --arg msg "$1" '{hookSpecificOutput:{hookEventName:"PermissionRequest",decision:{behavior:"allow",message:$msg}}}'
  exit 0
}

deny() {
  jq -n --arg msg "$1" '{hookSpecificOutput:{hookEventName:"PermissionRequest",decision:{behavior:"deny",message:$msg}}}'
  exit 0
}

# ── Core tools ──────────────────────────────────────────────
[[ "$TOOL" =~ ^(Read|Write|Edit|MultiEdit|Grep|Glob|NotebookEdit)$ ]] && allow "Core tool"
[[ "$TOOL" =~ ^(WebFetch|WebSearch)$ ]] && allow "Web tool"
[[ "$TOOL" =~ ^(Task|AskUserQuestion|Skill|EnterWorktree)$ ]] && allow "Agent tool"
[[ "$TOOL" =~ ^(TaskCreate|TaskUpdate|TaskGet|TaskList)$ ]] && allow "Task tool"
[[ "$TOOL" =~ ^(TeamCreate|TeamDelete|SendMessage)$ ]] && allow "Team tool"

# ── Bash commands ───────────────────────────────────────────
if [[ "$TOOL" == "Bash" ]]; then
  COMMAND=$(jq -r '.tool_input.command' <<< "$INPUT")

  # Deny
  [[ "$COMMAND" =~ ^bazel\ clean ]] && deny "bazel clean is not allowed"

  # Git
  [[ "$COMMAND" =~ ^git\ (status|log|diff|branch|show|fetch|checkout|pull|push|add|commit|cherry-pick|remote|stash|rev-parse|rebase) ]] && allow "Git"

  # GitHub CLI
  [[ "$COMMAND" =~ ^gh\ pr\ (list|view|checks|diff|create|ready|review) ]] && allow "GitHub CLI"
  [[ "$COMMAND" =~ ^gh\ (api|issue|run) ]] && allow "GitHub CLI"

  # Maven
  [[ "$COMMAND" =~ ^mvn(d)?\ (clean|compile|test|verify|package|dependency:|help:|com\.spotify) ]] && allow "Maven"
  [[ "$COMMAND" =~ ^mvn(d)?\ -[a-zA-Z] ]] && allow "Maven flags"

  # Bazel
  [[ "$COMMAND" =~ ^bazel\ (build|cquery|query|test) ]] && allow "Bazel"
  [[ "$COMMAND" =~ ^bazel\ run\ (//:format|//tools/importer) ]] && allow "Bazel run"

  # Common CLI
  [[ "$COMMAND" =~ ^(echo|sed|python3|find|awk|fd|cat|head|rg|grep|ls|cd|mkdir|backstagecli)( |$) ]] && allow "CLI tool"
fi

# ── MCP tools ───────────────────────────────────────────────
[[ "$TOOL" =~ ^mcp__code-search__ ]]          && allow "Code search"
[[ "$TOOL" =~ ^mcp__aika-search__ ]]          && allow "AiKA search"
[[ "$TOOL" =~ ^mcp__sequential-thinking__ ]]   && allow "Thinking"
[[ "$TOOL" =~ ^mcp__context7__ ]]             && allow "Context7"
[[ "$TOOL" =~ ^mcp__cloud-logging-mcp__ ]]    && allow "Cloud logging"
[[ "$TOOL" =~ ^mcp__context-mcp__ ]]          && allow "Context MCP"
[[ "$TOOL" =~ ^mcp__o11y-agg-mcp__ ]]         && allow "O11y"
[[ "$TOOL" =~ ^mcp__backstage-mcp-actions__ ]] && allow "Backstage"
[[ "$TOOL" =~ ^mcp__bigquery-mcp__ ]]         && allow "BigQuery"
[[ "$TOOL" =~ ^mcp__groove-mcp__ ]]           && allow "Groove"
[[ "$TOOL" =~ ^mcp__google-drive-mcp__ ]]     && allow "Google Drive"

[[ "$TOOL" =~ ^mcp__plugin_claude-mem_claude-mem-search__ ]] && allow "Claude memory"

# Atlassian - read-only operations
[[ "$TOOL" =~ ^mcp__atlassian-mcp__(list_tickets|get_project_info|search_issues_advanced|get_available_transitions)$ ]] && allow "Jira read"

# Google Calendar - read-only operations
[[ "$TOOL" =~ ^mcp__google-calendar-mcp__(list_calendar_events|get_calendar_event|list_calendars)$ ]] && allow "Calendar read"

# Spotify Enterprise Context Agent
[[ "$TOOL" =~ ^mcp__claude_ai_Spotify_s_Enterprise_Context_Agent__ ]] && allow "Enterprise Context"

# Slack tools
[[ "$TOOL" =~ ^mcp__claude_ai_Slack__ ]] && allow "Slack"

# Bandmanager
[[ "$TOOL" =~ ^mcp__claude_ai_Bandmanager_MCP__ ]] && allow "Bandmanager"

# BigQuery (claude_ai variant)
[[ "$TOOL" =~ ^mcp__claude_ai_Big_Query_MCP__ ]] && allow "BigQuery"

# AiKA Search (claude_ai variant)
[[ "$TOOL" =~ ^mcp__claude_ai_AiKA_Search_MCP__ ]] && allow "AiKA search"

# EnterPlanMode (agent workflow)
[[ "$TOOL" == "EnterPlanMode" ]] && allow "Plan mode"
[[ "$TOOL" == "ExitPlanMode" ]] && ask "Plan mode"

# ── No match → show permission dialog to user ──────────────
exit 0
