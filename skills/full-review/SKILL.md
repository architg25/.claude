---
name: full-review
description: "Run a comprehensive PR review using Claude and Codex in parallel. Synthesizes independent reviews into actionable feedback."
---

# Full PR Review

Run a comprehensive code review on a GitHub PR using two AI reviewers in parallel: Claude (standard review) and Codex (adversarial review). Each reviewer independently analyzes the PR, then you synthesize their findings.

## Usage

```
/full-review [PR_URL] [--post]
```

**IMPORTANT**: Always use full PR URLs (e.g., `https://github.com/org/repo/pull/123`).

Use `--post` to automatically post the synthesized review as a PR comment after synthesis.

## Policy / Safety

**Enterprise authentication required:**

- Both providers (Claude, Codex) must use enterprise accounts where applicable
- Do not use personal API keys for internal repositories

## Instructions

### Step 0: Parse the PR URL

Extract components from the URL using this regex: `^https?://([^/]+)/([^/]+/[^/]+)/pull/([0-9]+)`

- `HOST` — the GitHub host (e.g., `github.com` or `ghe.example.com`)
- `REPO` — owner/repo (e.g., `org/my-repo`)
- `PR_NUMBER` — the PR number

**GitHub Enterprise:** If `HOST` is not `github.com`, set `GH_HOST` env var for all `gh` commands:

```bash
export GH_HOST="<HOST>"
```

**If no URL provided:** Try to detect the current PR:

```bash
gh pr view --json url --jq .url
```

**If just a PR number:** Ask the user for the full URL. We need the host and repo.

### Step 1: Fetch PR data

Fetch the diff and metadata. These work without cloning the repo — they're API calls.

```bash
gh pr diff <PR_NUMBER> -R <REPO>
gh pr view <PR_NUMBER> -R <REPO> --json title,body,baseRefName,headRefName,additions,deletions,changedFiles
```

Save the diff to a variable for passing to reviewers.

### Step 2: Dispatch reviewers in parallel

Launch both reviewers in a SINGLE message with `run_in_background: true` on both.

**Claude subagent (standard review):**

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: |
    Review this PR diff. Focus on bugs, logic errors, edge cases, and code quality.

    PR: <REPO>#<PR_NUMBER> - <title>
    Base: <baseRefName> <- <headRefName>

    <diff content>

    Produce a structured review with:
    - Critical issues (bugs, security, data loss)
    - Important issues (logic errors, edge cases, missing validation)
    - Suggestions (style, readability, minor improvements)
    Include file paths and line numbers for every finding.
  run_in_background: true
  name: "claude-review"
  model: "opus"
```

**Codex rescue subagent (adversarial review):**

```
Agent tool:
  subagent_type: "codex:codex-rescue"
  prompt: |
    --fresh
    You are an adversarial code reviewer. Your job is NOT to do a standard review — it's to challenge the implementation approach, question design choices, and find what a standard reviewer would miss.

    PR: <REPO>#<PR_NUMBER> - <title>
    Base: <baseRefName> <- <headRefName>

    <diff content>

    Focus on:
    - Is this the right approach? What alternatives were there?
    - What assumptions does this code make that could break?
    - What happens under load, with bad input, or in failure modes?
    - Are there subtle interactions with code outside the diff?

    Produce structured output:
    - Verdict: approve | needs-attention
    - Findings: array of { severity (critical/high/medium/low), file, line, description, recommendation }
    - Next steps: what should the author address before merging
  run_in_background: true
  name: "codex-adversarial-review"
```

### Step 3: Synthesize

After both reviewers complete:

1. **Identify consensus**: Issues flagged by both reviewers are highest priority
2. **Note unique insights**: Each reviewer catches different things — Claude is thorough on implementation details, Codex challenges the approach itself
3. **Investigate conflicts**: If reviewers disagree, investigate the code yourself using the diff
4. **Verify claims**: Spot-check specific line numbers or code references

### Step 4: Present results

```markdown
## Synthesized PR Review

**PR:** <REPO>#<PR_NUMBER>
**Reviewers:** Claude (standard), Codex (adversarial)

### Critical Issues (consensus)

- Issues identified by both reviewers

### Important Issues

- Significant issues from individual reviewers

### Design Challenges (from adversarial review)

- Approach concerns, assumption risks, alternative suggestions

### Suggestions

- Minor improvements and style suggestions

### Reviewer Notes

- Any conflicts or interesting differences between reviews
```

Prioritize:

1. **Security issues** — any security concern from any reviewer
2. **Bugs** — logic errors, edge cases, null handling
3. **Design concerns** — approach problems, bad assumptions
4. **Performance** — inefficiencies or scalability concerns
5. **Code quality** — maintainability, readability, testing

### Step 5: Post (if --post flag)

If `--post` was specified:

1. Save synthesized review to `/tmp/pr-review-<PR_NUMBER>/synthesized.md`
2. Post as PR comment:

```bash
gh pr comment <PR_NUMBER> -R <REPO> --body-file /tmp/pr-review-<PR_NUMBER>/synthesized.md
```

## Common Mistakes

| Mistake                                  | Fix                                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------------- |
| Not fetching the diff before dispatching | Both reviewers need the full diff in their prompt — fetch it first              |
| Forgetting GH_HOST for enterprise URLs   | Parse the host from URL and export GH_HOST if not github.com                    |
| Trusting line numbers blindly            | Reviewers hallucinate line numbers — spot-check references against the diff     |
| Binary pass/fail synthesis               | Both reviewers can be partially right — synthesize, don't pick a winner         |
| Skipping adversarial insights            | The adversarial review catches different things — don't dismiss design concerns |
