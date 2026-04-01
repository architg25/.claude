---
name: ai-review
description: "Run an AI-powered PR review using Claude or Codex CLI. Reviews the PR diff against project guidelines."
allowed-tools: Read, Glob, Grep, Bash, mcp__code-search__search_code, mcp__code-search__read_file, mcp__code-search__count_matches
---

# AI PR Review

Run an AI-powered code review on a GitHub PR using your choice of AI provider.

## Usage

```
/ai-review <provider> [PR_URL] [--post]
```

Where `<provider>` is one of: `claude`, `codex`

**IMPORTANT**: Always use full PR URLs (e.g., `https://github.com/org/repo/pull/123`).
The script fetches the PR diff via `gh` and the AI uses codesearch MCP for codebase exploration (no cloning needed).

## Prerequisites

Depending on the provider you choose:

### Claude

```bash
# Claude Code CLI (you're already using it!)
```

### Codex (OpenAI)

```bash
npm i -g @openai/codex
# First run will prompt you to sign in
```

## Policy / Safety

**Enterprise authentication required:**

- Codex/OpenAI: Use your Spotify enterprise account, not personal
- Claude: Uses Vertex AI with your enterprise credentials

## What This Command Does

1. Fetches the PR metadata and diff using `gh`
2. Sends the diff to the chosen AI for review against three levels of guidelines:
   - **Explicit guidelines**: CLAUDE.md and linked documentation
   - **Implicit guidelines**: Conventions from similar code in the codebase
   - **Best practices**: Security, performance, maintainability standards
3. Returns a structured review with:
   - Summary
   - Explicit guidelines compliance
   - Implicit guidelines compliance (codebase conventions)
   - Best practices assessment
   - Major issues (must-fix)
   - Minor issues / suggestions
   - Tests & verification recommendations
   - Risk assessment
4. Optionally posts the review as a PR comment with `--post`

## Instructions

Run the ai-pr-review.sh script from this skill's scripts directory:

```bash
scripts/ai-pr-review.sh <provider> <PR_URL> [--post]
```

**Getting the PR URL:**

- If the user provides a full URL, use it directly
- If the user provides just a PR number, you must construct the full URL
- If no PR is specified, detect the current PR's URL:

```bash
PR_URL=$(gh pr view --json url --jq .url)
```

### Examples

Review the current branch's PR with Claude:

```bash
PR_URL=$(gh pr view --json url --jq .url)
scripts/ai-pr-review.sh claude "$PR_URL"
```

Review a specific PR with Codex:

```bash
scripts/ai-pr-review.sh codex https://github.com/org/repo/pull/123
```

Review with Codex and post as a comment:

```bash
scripts/ai-pr-review.sh codex https://ghe.spotify.net/org/repo/pull/123 --post
```

## Output Files

Reviews are saved to `/tmp/pr-review-<PR_NUMBER>/<provider>.md`:

- `/tmp/pr-review-123/claude.md`
- `/tmp/pr-review-123/codex.md`

This allows running reviews for multiple PRs simultaneously.

## Models Used

- **Claude**: claude-opus-4-6
- **Codex**: gpt-5.4 (with `--effort high`)
