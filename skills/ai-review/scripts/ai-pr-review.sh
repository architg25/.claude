#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./ai-pr-review.sh <provider> <PR_URL_or_number> [--post]
# Providers: claude, codex
# Examples:
#   ./ai-pr-review.sh claude 123
#   ./ai-pr-review.sh codex https://github.com/org/repo/pull/123 --post
#   ./ai-pr-review.sh codex 123 --post

PROVIDER="${1:-}"
PR="${2:-}"
POST="${3:-}"

if [[ -z "$PROVIDER" ]] || [[ -z "$PR" ]]; then
  echo "Usage: $0 <provider> <PR_URL_or_number> [--post]" >&2
  echo "Providers: claude, codex" >&2
  exit 2
fi

# Validate provider
case "$PROVIDER" in
  claude|codex) ;;
  *)
    echo "Error: Invalid provider '$PROVIDER'. Must be one of: claude, codex" >&2
    exit 2
    ;;
esac

# Check if the selected provider CLI is installed
case "$PROVIDER" in
  claude)
    if ! command -v claude &> /dev/null; then
      echo "Error: Claude CLI is not installed." >&2
      echo "Install with: npm install -g @anthropic-ai/claude-code" >&2
      exit 1
    fi
    ;;
  codex)
    if ! command -v codex &> /dev/null; then
      echo "Error: Codex CLI is not installed." >&2
      echo "" >&2
      echo "To install:" >&2
      echo "  npm install -g @openai/codex" >&2
      echo "" >&2
      echo "Then sign in with Spotify SSO:" >&2
      echo "  codex --provider openai" >&2
      echo "  # Select 'Sign in with SSO' and use your Spotify enterprise account" >&2
      exit 1
    fi
    ;;
esac

# Detect GH_HOST and REPO from PR URL or require them as environment variables
# This handles GitHub Enterprise (e.g., ghe.spotify.net)
REPO=""
GH_HOST_FOR_CLONE="github.com"
if [[ "$PR" =~ ^https?://([^/]+)/([^/]+/[^/]+)/pull/([0-9]+) ]]; then
  # Extract host, repo, and PR number from full URL
  DETECTED_HOST="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  PR_NUMBER="${BASH_REMATCH[3]}"
  GH_HOST_FOR_CLONE="$DETECTED_HOST"
  if [[ "$DETECTED_HOST" != "github.com" ]]; then
    export GH_HOST="$DETECTED_HOST"
    echo "Detected GitHub Enterprise host: $GH_HOST"
  else
    unset GH_HOST  # Clear any leftover GH_HOST from environment
  fi
  echo "Detected repo: $REPO"
  # Use the PR number for gh commands
  PR="$PR_NUMBER"
else
  # PR is a number - require GH_REPO environment variable
  if [[ -z "${GH_REPO:-}" ]]; then
    echo "Error: When using PR number, you must set GH_REPO environment variable (e.g., GH_REPO=org/repo)" >&2
    echo "Or provide a full PR URL instead." >&2
    exit 2
  fi
  REPO="$GH_REPO"
  echo "Using repo from GH_REPO: $REPO"

  # Detect host from GH_HOST or default to github.com
  if [[ -n "${GH_HOST:-}" ]]; then
    echo "Using GitHub Enterprise host: $GH_HOST"
    GH_HOST_FOR_CLONE="$GH_HOST"
  fi
fi

# Fetch PR metadata + diff using gh with explicit repo (handles private repos via your gh auth)
echo "Fetching PR metadata..."
TITLE="$(gh pr view "$PR" -R "$REPO" --json title --jq .title)"
BASE_REF="$(gh pr view "$PR" -R "$REPO" --json baseRefName --jq .baseRefName)"
HEAD_REF="$(gh pr view "$PR" -R "$REPO" --json headRefName --jq .headRefName)"
URL="$(gh pr view "$PR" -R "$REPO" --json url --jq .url)"
DIFF="$(gh pr diff "$PR" -R "$REPO")"

echo "PR: $TITLE"
echo "Branch: $HEAD_REF -> $BASE_REF"

# Clone the repo to a temp directory so AI can explore the codebase
TEMP_DIR=$(mktemp -d)
CLONE_URL="git@${GH_HOST_FOR_CLONE}:${REPO}.git"

echo "Cloning repo to temp directory for codebase exploration..."
echo "Clone URL: $CLONE_URL"

# Use shallow clone with the PR's head branch for speed
if ! git clone --depth 50 --branch "$HEAD_REF" "$CLONE_URL" "$TEMP_DIR" 2>/dev/null; then
  # If branch clone fails (might be from a fork), try default branch and fetch the PR
  echo "Direct branch clone failed, trying default branch..."
  git clone --depth 50 "$CLONE_URL" "$TEMP_DIR"
  cd "$TEMP_DIR"
  # Fetch the PR ref
  git fetch origin "pull/${PR}/head:pr-${PR}" --depth 50 2>/dev/null || true
  git checkout "pr-${PR}" 2>/dev/null || echo "Warning: Could not checkout PR branch, using default branch"
fi

cd "$TEMP_DIR"
echo "Cloned to: $TEMP_DIR"
echo "Current branch: $(git branch --show-current 2>/dev/null || echo 'detached HEAD')"

# Cleanup function
cleanup() {
  echo "Cleaning up temp directory..."
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Build the review prompt
REVIEW_PROMPT='You are a senior engineer doing a GitHub PR review.

IMPORTANT: You have access to the full codebase via your file reading tools. USE THEM.
Do not just review the diff in isolation - explore the codebase to do a thorough review.

## Before You Start - Read the Codebase

1. Read CLAUDE.md in the repository root (use your file reading tools)
2. Follow any links to documentation referenced in CLAUDE.md and read those too
3. Check for AGENTS.md or similar guideline files
4. Look at files in the same directory as the changed files to understand conventions
5. Find similar implementations elsewhere in the codebase for comparison

## Review Criteria

Evaluate the PR against THREE levels of guidelines:

### 1. Explicit Guidelines (CLAUDE.md & Documentation)
- What do CLAUDE.md and linked docs say about this type of code?
- Quote the specific guidelines that apply
- The PR MUST comply with all documented standards

### 2. Implicit Guidelines (Codebase Conventions)
- USE YOUR TOOLS to read similar code in the codebase
- Look at neighboring files, sibling modules, and analogous implementations
- How is similar functionality implemented elsewhere?
- The PR should follow established patterns even if not explicitly documented

### 3. General Best Practices
- Security: no vulnerabilities, proper input validation, safe defaults
- Performance: efficient algorithms, no unnecessary overhead
- Maintainability: clear code, appropriate abstractions, good naming
- Testing: adequate coverage, meaningful test cases
- Error handling: graceful failures, informative messages

## Output Format

Return Markdown with exactly these sections:

## Summary
Brief description of what the PR does.

## Explicit guidelines compliance
- Compliance with CLAUDE.md and linked documentation
- Quote relevant sections when citing violations

## Implicit guidelines compliance
- Consistency with codebase conventions and patterns
- Reference specific files/modules that demonstrate the expected pattern

## Best practices
- Security, performance, maintainability concerns
- Industry standard violations

## Major issues (must-fix)
- Bullet points. If none, say "None found."

## Minor issues / suggestions
- Bullet points.

## Tests & verification
- Concrete commands or test cases to add/run.

## Risk assessment
- Call out compatibility, perf, security, rollout risk.

## Review Guidelines
- Be specific and reference filenames and line numbers
- When citing guideline violations, quote the relevant guideline
- When citing convention violations, reference the file that shows the correct pattern
- If you need more context to complete the review, state what you would look for'

# Build the context input
CONTEXT=$(cat <<EOF
PR: $URL
Title: $TITLE
Base: $BASE_REF
Head: $HEAD_REF

==== BEGIN DIFF ====
$DIFF
==== END DIFF ====

$REVIEW_PROMPT
EOF
)

# Create unique output directory per PR
OUTPUT_DIR="/tmp/pr-review-${PR}"
mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="${OUTPUT_DIR}/${PROVIDER}.md"
> "$OUTPUT_FILE"  # Clear stale content from previous runs

# Unset CLAUDECODE so spawned claude processes don't think they're nested sessions
unset CLAUDECODE

echo ""
echo "Running PR review with $PROVIDER..."
echo "Working directory: $(pwd)"
echo "Output file: $OUTPUT_FILE"
echo ""

case "$PROVIDER" in
  claude)
    # Claude CLI uses -p for headless mode, --model to specify model
    # Running from the cloned repo directory so Claude can explore the codebase
    echo "$CONTEXT" | claude -p --model claude-opus-4-5 "Write the PR review." | tee "$OUTPUT_FILE"
    ;;
  codex)
    # Codex CLI uses exec for headless mode
    # Use -o to write just the final response to file (avoids verbose progress output)
    # Running from the cloned repo directory so Codex can explore the codebase
    echo "$CONTEXT" | codex exec --model gpt-5.3-codex -o "$OUTPUT_FILE" "Write the PR review."
    cat "$OUTPUT_FILE"
    ;;
esac

if [[ "$POST" == "--post" ]]; then
  # Post as a PR comment (needs gh auth + permission to comment)
  gh pr comment "$PR" -R "$REPO" --body-file "$OUTPUT_FILE"
  echo "Posted review comment to PR."
fi

echo ""
echo "Review saved to: $OUTPUT_FILE"