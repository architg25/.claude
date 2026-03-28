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
[[ "$TOOL" =~ ^(Task|Skill|EnterWorktree)$ ]] && allow "Agent tool"
[[ "$TOOL" =~ ^(TaskCreate|TaskUpdate|TaskGet|TaskList)$ ]] && allow "Task tool"
[[ "$TOOL" =~ ^(TeamCreate|TeamDelete|SendMessage)$ ]] && allow "Team tool"

# ── Bash commands ───────────────────────────────────────────
if [[ "$TOOL" == "Bash" ]]; then
  COMMAND=$(jq -r '.tool_input.command' <<< "$INPUT")
  COMMAND="${COMMAND#"${COMMAND%%[![:space:]]*}"}"  # trim leading whitespace
  COMMAND="${COMMAND#GH_HOST=ghe.spotify.net }"     # strip GH_HOST prefix
  COMMAND="${COMMAND#GH_HOST=github.com }"          # strip GH_HOST prefix (public GitHub)

  # Deny
  [[ "$COMMAND" =~ ^bazel\ clean ]] && deny "bazel clean is not allowed"
  [[ "$COMMAND" =~ ^(find|ls|grep|rg|cat|head|tail|sed|awk)( |$) ]] && deny "Use dedicated tools (Glob, Grep, Read, Edit) instead"
  [[ "$COMMAND" =~ ^echo\ .*\> ]] && deny "Use Write tool instead of echo redirection"

  # Git
  [[ "$COMMAND" =~ ^git\ (-[a-zA-Z]\ [^ ]+\ )*(status|log|diff|branch|show|fetch|checkout|pull|add|commit|cherry-pick|remote|stash|rev-parse|rebase) ]] && allow "Git"

  # GitHub CLI
  [[ "$COMMAND" =~ ^gh\ pr\ (list|view|checks|diff|create|ready|review|comment) ]] && allow "GitHub CLI"
  [[ "$COMMAND" =~ ^gh\ (api|issue|run) ]] && allow "GitHub CLI"

  # Maven
  [[ "$COMMAND" =~ ^mvn(d)?\ (clean|compile|test|verify|package|dependency:|help:|com\.spotify) ]] && allow "Maven"
  [[ "$COMMAND" =~ ^mvn(d)?\ -[a-zA-Z] ]] && allow "Maven flags"

  # Bazel
  [[ "$COMMAND" =~ ^bazel\ (build|cquery|query|test) ]] && allow "Bazel"
  [[ "$COMMAND" =~ ^bazel\ run\ (//:format|//tools/importer) ]] && allow "Bazel run"

  # Go
  [[ "$COMMAND" =~ ^go\ (build|test|vet|fmt|mod|list|doc|version|env|generate|tool|run|get|install|clean|work)( |$) ]] && allow "Go"

  # Cargo (Rust)
  [[ "$COMMAND" =~ ^cargo\ (build|test|check|clippy|fmt|run|bench|doc|clean|update|add|remove|tree|fix|search|version|metadata|generate-lockfile)( |$) ]] && allow "Cargo"

  # Common CLI
  [[ "$COMMAND" =~ ^(python3|fd|cd|mkdir|backstagecli|wc|lsof|ps|gofmt|jq)( |$) ]] && allow "CLI tool"
fi

# ── MCP tools (read-only only) ─────────────────────────────
[[ "$TOOL" =~ ^mcp__code-search__ ]]          && allow "Code search"
[[ "$TOOL" =~ ^mcp__context7__ ]]             && allow "Context7"
[[ "$TOOL" =~ ^mcp__cloud-logging-mcp__ ]]    && allow "Cloud logging"
[[ "$TOOL" =~ ^mcp__ide__ ]]                  && allow "IDE diagnostics"

# claude_ai MCP servers
[[ "$TOOL" =~ ^mcp__claude_ai_AiKA_Search_MCP__ ]] && allow "AiKA search"
[[ "$TOOL" =~ ^mcp__claude_ai_Big_Query_MCP__ ]]   && allow "BigQuery"
[[ "$TOOL" =~ ^mcp__claude_ai_GDrive_MCP__ ]]      && allow "GDrive"
[[ "$TOOL" =~ ^mcp__claude_ai_Slack__slack_(read|search) ]] && allow "Slack read"
[[ "$TOOL" =~ ^mcp__sequential-thinking__ ]]        && allow "Sequential thinking"

# EnterPlanMode (agent workflow)
[[ "$TOOL" == "EnterPlanMode" ]] && allow "Plan mode"
[[ "$TOOL" == "ExitPlanMode" ]] && ask "Plan mode"

# ── No match → show permission dialog to user ──────────────
exit 0
