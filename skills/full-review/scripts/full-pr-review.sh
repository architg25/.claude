#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./full-pr-review.sh <PR_URL> [--post]
# Examples:
#   ./full-pr-review.sh https://github.com/org/repo/pull/123
#   ./full-pr-review.sh https://ghe.spotify.net/org/repo/pull/123 --post
#
# NOTE: Always use full PR URLs to ensure correct repo detection.
# The script can run from any directory when using full URLs.

PR=""
POST=""

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --post)
      POST="--post"
      ;;
    *)
      if [[ -z "$PR" ]]; then
        PR="$arg"
      fi
      ;;
  esac
done

if [[ -z "$PR" ]]; then
  echo "Usage: $0 <PR_URL> [--post]" >&2
  echo "Example: $0 https://github.com/org/repo/pull/123" >&2
  exit 2
fi

# Validate that PR is a full URL (required for reliable repo detection)
if [[ ! "$PR" =~ ^https?://([^/]+)/([^/]+/[^/]+)/pull/([0-9]+) ]]; then
  echo "Error: Please provide a full PR URL (e.g., https://github.com/org/repo/pull/123)" >&2
  echo "PR numbers without URLs are not supported - the script needs to know which repo to query." >&2
  exit 2
fi

# Extract host and repo for display
DETECTED_HOST="${BASH_REMATCH[1]}"
DETECTED_REPO="${BASH_REMATCH[2]}"
PR_NUMBER="${BASH_REMATCH[3]}"

if [[ "$DETECTED_HOST" != "github.com" ]]; then
  export GH_HOST="$DETECTED_HOST"
  echo "GitHub Enterprise host: $GH_HOST"
else
  unset GH_HOST  # Clear any leftover GH_HOST from environment
fi
echo "Repository: $DETECTED_REPO"
echo "PR: #$PR_NUMBER"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_REVIEW_SCRIPT="$SCRIPT_DIR/../../ai-review/scripts/ai-pr-review.sh"

# Check which providers are available
MISSING_PROVIDERS=""
if ! command -v claude &> /dev/null; then
  MISSING_PROVIDERS="${MISSING_PROVIDERS}claude "
fi
if ! command -v codex &> /dev/null; then
  MISSING_PROVIDERS="${MISSING_PROVIDERS}codex "
fi

if [[ -n "$MISSING_PROVIDERS" ]]; then
  echo "Warning: Some provider CLIs are not installed: $MISSING_PROVIDERS" >&2
  echo "" >&2
  if [[ "$MISSING_PROVIDERS" == *"codex"* ]]; then
    echo "To install Codex:" >&2
    echo "  npm install -g @openai/codex" >&2
    echo "  codex --provider openai  # Sign in with Spotify SSO" >&2
    echo "" >&2
  fi
  echo "Continuing with available providers..." >&2
  echo "" >&2
fi

echo ""
echo "Starting parallel PR reviews with Claude and Codex..."
if [[ -n "$POST" ]]; then
  echo "Will post synthesized review as PR comment."
fi
echo ""

# Run all three reviews in parallel
# Each review outputs to its own file in /tmp
# Pass the full URL so ai-pr-review.sh can extract repo info

# Unset CLAUDECODE so spawned claude processes don't think they're nested sessions
unset CLAUDECODE

(
  echo "=== Starting Claude review ==="
  "$AI_REVIEW_SCRIPT" claude "$PR" 2>&1 || echo "Claude review failed"
  echo "=== Claude review complete ==="
) &
CLAUDE_PID=$!

(
  echo "=== Starting Codex review ==="
  "$AI_REVIEW_SCRIPT" codex "$PR" 2>&1 || echo "Codex review failed"
  echo "=== Codex review complete ==="
) &
CODEX_PID=$!

echo "Reviews running in parallel (PIDs: Claude=$CLAUDE_PID, Codex=$CODEX_PID)"
echo "Waiting for all reviews to complete..."
echo ""

# Wait for all to complete
wait $CLAUDE_PID $CODEX_PID 2>/dev/null || true

OUTPUT_DIR="/tmp/pr-review-${PR_NUMBER}"

echo ""
echo "============================================"
echo "All reviews complete!"
echo "============================================"
echo ""
echo "Review directory: $OUTPUT_DIR"
echo "Review files:"
echo "  - Claude: ${OUTPUT_DIR}/claude.md"
echo "  - Codex:  ${OUTPUT_DIR}/codex.md"
echo ""
echo "Read these files and synthesize the reviews."

if [[ -n "$POST" ]]; then
  echo ""
  echo "POST_REVIEW=true"
  echo "GH_HOST=$DETECTED_HOST"
  echo "GH_REPO=$DETECTED_REPO"
  echo "PR_NUMBER=$PR_NUMBER"
  echo "OUTPUT_DIR=$OUTPUT_DIR"
  echo ""
  echo "After synthesizing, save the review to ${OUTPUT_DIR}/synthesized.md and run:"
  echo "  gh pr comment $PR_NUMBER -R $DETECTED_REPO --body-file ${OUTPUT_DIR}/synthesized.md"
fi