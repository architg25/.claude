#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./ai-pr-review.sh <provider> <PR_URL_or_number> [--model MODEL] [--effort EFFORT] [--post]
# Providers: claude, codex
# Examples:
#   ./ai-pr-review.sh claude 123
#   ./ai-pr-review.sh codex https://github.com/org/repo/pull/123 --post
#   ./ai-pr-review.sh codex 123 --codex-model gpt-5.4-mini --post

PROVIDER=""
PR=""
POST=""
CLAUDE_MODEL=""
CODEX_MODEL=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --post) POST="--post"; shift ;;
    --claude-model) CLAUDE_MODEL="$2"; shift 2 ;;
    --codex-model) CODEX_MODEL="$2"; shift 2 ;;
    *)
      if [[ -z "$PROVIDER" ]]; then
        PROVIDER="$1"
      elif [[ -z "$PR" ]]; then
        PR="$1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$PROVIDER" ]] || [[ -z "$PR" ]]; then
  echo "Usage: $0 <provider> <PR_URL_or_number> [--claude-model MODEL] [--codex-model MODEL] [--post]" >&2
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
if [[ "$PR" =~ ^https?://([^/]+)/([^/]+/[^/]+)/pull/([0-9]+) ]]; then
  # Extract host, repo, and PR number from full URL
  DETECTED_HOST="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  PR_NUMBER="${BASH_REMATCH[3]}"
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

  if [[ -n "${GH_HOST:-}" ]]; then
    echo "Using GitHub Enterprise host: $GH_HOST"
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

# Build the review prompt
# No repo clone — the AI uses codesearch MCP to explore the codebase on demand.
# This avoids slow clones for monorepos.
REVIEW_PROMPT='You are a senior engineer doing a GitHub PR review.

IMPORTANT: Use codesearch MCP (search_code, read_file) to explore the codebase for context.
Do not just review the diff in isolation — search for related code, conventions, and guidelines.

## Before You Start - Gather Context

1. Use codesearch to find and read CLAUDE.md or AGENTS.md in the repo
2. Follow any links to documentation referenced in those files
3. Search for files in the same directories as the changed files to understand conventions
4. Search for similar implementations elsewhere in the codebase for comparison

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

# Create unique output directory per PR and write context to a file
# (avoids shell argument length limits for large diffs)
OUTPUT_DIR="/tmp/pr-review-${PR}"
mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="${OUTPUT_DIR}/${PROVIDER}.md"
> "$OUTPUT_FILE"  # Clear stale content from previous runs

CONTEXT_FILE="${OUTPUT_DIR}/context-${PROVIDER}.txt"
echo "$CONTEXT" > "$CONTEXT_FILE"

# Unset CLAUDECODE so spawned claude processes don't think they're nested sessions
unset CLAUDECODE

echo ""
echo "Running PR review with $PROVIDER..."
echo "Working directory: $(pwd)"
echo "Output file: $OUTPUT_FILE"
echo ""

# Build provider-specific CLI args
CLAUDE_MODEL_ARG=""
CODEX_MODEL_ARG=""

if [[ -n "$CLAUDE_MODEL" ]]; then
  CLAUDE_MODEL_ARG="--model $CLAUDE_MODEL"
fi

if [[ -n "$CODEX_MODEL" ]]; then
  CODEX_MODEL_ARG="-m $CODEX_MODEL"
fi

START_TIME=$(date +%s)

case "$PROVIDER" in
  claude)
    claude -p $CLAUDE_MODEL_ARG < "$CONTEXT_FILE" | tee "$OUTPUT_FILE"
    ;;
  codex)
    codex exec --full-auto $CODEX_MODEL_ARG --skip-git-repo-check -o "$OUTPUT_FILE" < "$CONTEXT_FILE"
    cat "$OUTPUT_FILE"
    ;;
esac

ELAPSED=$(( $(date +%s) - START_TIME ))
echo ""
echo "[$PROVIDER] Review completed in ${ELAPSED}s"

if [[ "$POST" == "--post" ]]; then
  # Post as a PR comment (needs gh auth + permission to comment)
  gh pr comment "$PR" -R "$REPO" --body-file "$OUTPUT_FILE"
  echo "Posted review comment to PR."
fi

echo ""
echo "Review saved to: $OUTPUT_FILE"