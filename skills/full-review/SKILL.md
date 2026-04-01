---
name: full-review
description: "Run a comprehensive PR review using Claude and Codex in parallel. Synthesizes independent reviews into actionable feedback."
---

# Full PR Review

Run a comprehensive code review on a GitHub PR using two AI reviewers in parallel: Claude and Codex. Each reviewer independently analyzes the PR, then you synthesize their findings.

## Usage

```
/full-review [PR_URL] [--post]
```

**IMPORTANT**: Always use full PR URLs (e.g., `https://github.com/org/repo/pull/123`).
The script needs the full URL to know which repo to clone.

Use `--post` to automatically post the synthesized review as a PR comment after synthesis.

## Policy / Safety

**Enterprise authentication required:**

- All two providers (Claude, Codex) must use Spotify enterprise accounts
- Do not use personal API keys for internal Spotify repositories

## What This Command Does

1. Runs the ai-pr-review.sh script two times in parallel (Claude, Codex)
2. Each reviewer independently:
   - Fetches the PR diff
   - Reads CLAUDE.md guidelines
   - Produces a structured review
3. Saves reviews to separate files
4. You then synthesize the reviews

## Instructions

### Step 1: Run the parallel reviews

Run the full-pr-review.sh script from this skill's scripts directory:

```bash
scripts/full-pr-review.sh <PR_URL> [--post]
```

**Getting the PR URL:**

- If the user provides a full URL, use it directly
- If the user provides just a PR number, you must construct the full URL
- If no PR is specified, detect the current PR's URL:

```bash
PR_URL=$(gh pr view --json url --jq .url)
scripts/full-pr-review.sh "$PR_URL"
```

Add `--post` if the user wants to post the synthesized review as a PR comment.

### Step 2: Read all three reviews

After the script completes, read the review files:

```
/tmp/claude-pr-review.md
/tmp/codex-pr-review.md
```

### Step 3: Synthesize and investigate

After reading all three reviews:

1. **Identify consensus**: Issues flagged by multiple reviewers are higher priority
2. **Note unique insights**: Each AI may catch different issues
3. **Investigate conflicts**: If reviewers disagree, investigate the code yourself
4. **Create a synthesis**: Combine the best insights from each review
5. **Verify claims**: Check any specific line numbers or code references mentioned

### Step 4: Post the synthesized review

If the script output contains `POST_REVIEW=true`, you MUST:

1. Save your synthesized review to `/tmp/synthesized-review.md`
2. Post it as a PR comment using the command shown in the script output

```bash
gh pr comment <PR_URL> --body-file /tmp/synthesized-review.md
```

## Output Files

Reviews are saved to `/tmp/pr-review-<PR_NUMBER>/`:

- `/tmp/pr-review-123/claude.md` - Claude's independent review
- `/tmp/pr-review-123/codex.md` - Codex's independent review
- `/tmp/pr-review-123/synthesized.md` - Your synthesized review (if posting)

This allows running reviews for multiple PRs simultaneously.

## Synthesis Guidelines

When synthesizing reviews, prioritize:

1. **Security issues** - Any security concern from any reviewer
2. **Bugs** - Logic errors, edge cases, null handling
3. **Guidelines violations** - Deviations from CLAUDE.md
4. **Performance** - Inefficiencies or scalability concerns
5. **Code quality** - Maintainability, readability, testing

Format your synthesized review as:

```markdown
## Synthesized PR Review

**Reviewers**: Claude, Codex

### Critical Issues (consensus)

- Issues identified by 2+ reviewers

### Important Issues

- Significant issues from individual reviewers

### Suggestions

- Minor improvements and style suggestions

### Reviewer Notes

- Any conflicts or interesting differences between reviews
```
