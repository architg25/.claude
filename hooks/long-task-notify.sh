#!/bin/bash
# Notify when a Claude Code task takes longer than CLAUDE_NOTIFY_THRESHOLD (default: 300s / 5min)
THRESHOLD="${CLAUDE_NOTIFY_THRESHOLD:-300}"

INPUT=$(cat)
EVENT=$(echo "$INPUT" | jq -r '.hook_event_name')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')
TIMER_FILE="/tmp/claude-task-${SESSION_ID}"

if [ "$EVENT" = "UserPromptSubmit" ]; then
    # Start timer on every prompt
    date +%s > "$TIMER_FILE"

elif [ "$EVENT" = "Notification" ]; then
    NOTIF_TYPE=$(echo "$INPUT" | jq -r '.notification_type')
    if [ "$NOTIF_TYPE" = "idle_prompt" ] && [ -f "$TIMER_FILE" ]; then
        START=$(cat "$TIMER_FILE")
        NOW=$(date +%s)
        ELAPSED=$((NOW - START))
        if [ "$ELAPSED" -gt "$THRESHOLD" ]; then
            MINUTES=$((ELAPSED / 60))
            osascript -e "display notification \"Task completed after ${MINUTES} min\" with title \"Claude Code\" sound name \"Glass\""
        fi
        rm -f "$TIMER_FILE"
    fi
fi
