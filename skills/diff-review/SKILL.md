---
name: diff-review
description: Use when about to create or edit a PR, or when the user wants a pre-PR diff review. Triggers on "review my diff", "check my changes before PR", "diff review", or before invoking engineering:pr-description or engineering:ship.
---

# Diff Review

Dispatch Codex to independently review your diff against the target branch before creating or updating a PR. Catches issues a self-review misses.

## Usage

```
/diff-review                    # Review diff against default branch
/diff-review <target-branch>    # Review diff against specific branch
```

## Why This Exists

You wrote the code. You can't objectively review it. Codex uses different models and search strategies — it catches things you miss. Run this before creating a PR, not after.

## When to Use This vs `/full-review`

- **`/diff-review`**: Pre-PR gate. Lightweight, single reviewer (Codex), fast. Use before creating a PR.
- **`/full-review`**: Post-PR deep review. Multi-reviewer (Claude + Codex + Gemini), thorough. Use on existing PRs.

## Instructions

### Step 0: Validate and get the diff

First, verify you're in a git repo:

```bash
git rev-parse --is-inside-work-tree
```

If this fails, tell the user this skill requires a git repository and stop.

Determine the target branch. If the user provided one, use it. Otherwise detect the default:

```bash
TARGET=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || echo "master")
```

Fetch and generate the diff:

```bash
git fetch origin "$TARGET"
git diff "origin/$TARGET"...HEAD
```

If the diff is empty (no commits ahead of target), stop and tell the user there's nothing to review.

**Diff size check:** Count the diff lines:

```bash
git diff "origin/$TARGET"...HEAD | wc -l
```

- **Under 5000 lines**: Proceed normally — write diff to file and pass file path to Codex.
- **5000-15000 lines**: Warn the user the diff is large. Proceed, but filter out test files and generated code:
  ```bash
  git diff "origin/$TARGET"...HEAD -- . ':!**/test/**' ':!**/tests/**' ':!**/*Test.*' ':!**/*Spec.*' ':!**/generated/**' ':!**/*.generated.*'
  ```
- **Over 15000 lines**: Tell the user the diff is too large for meaningful automated review. Suggest splitting the PR or running `/full-review` on specific directories.

### Step 1: Get repo context

Use Glob to check for project guidelines:

```
Glob: CLAUDE.md, .claude/CLAUDE.md, AGENTS.md
```

Read any guidelines file found. If none exist, proceed without project-specific criteria.

### Step 2: Build the review prompt

Write the diff to a file first — never pass it as a shell argument:

```bash
REVIEW_DIR="/tmp/diff-review-$(date +%s)" && mkdir -p "$REVIEW_DIR"
```

Use the same diff command from Step 0 (filtered for the 5k-15k case, unfiltered otherwise):

```bash
# Under 5000 lines:
git diff "origin/$TARGET"...HEAD > "$REVIEW_DIR/diff.patch"

# 5000-15000 lines (filtered):
git diff "origin/$TARGET"...HEAD -- . ':!**/test/**' ':!**/tests/**' ':!**/*Test.*' ':!**/*Spec.*' ':!**/generated/**' ':!**/*.generated.*' > "$REVIEW_DIR/diff.patch"
```

Construct the review prompt (without the diff inline — Codex reads the file):

```
You are reviewing a code diff before it becomes a pull request. Your job is to find real problems, not nitpick style.

<include CLAUDE.md content if found, otherwise omit the "Project Guidelines" section entirely>

## Instructions
Read the diff file at <REVIEW_DIR>/diff.patch and review it.

## Review Criteria

Focus on (in priority order):
1. **Bugs** — Logic errors, off-by-ones, null handling, race conditions
2. **Security** — Injection, auth bypass, secrets exposure, OWASP top 10
3. **Breaking changes** — API contract violations, backwards incompatibility
4. **Missing tests** — New logic paths without test coverage
5. **Performance** — Obviously inefficient patterns (N+1 queries, unbounded collections)

Do NOT flag:
- Style preferences (naming, formatting)
- Missing comments or documentation
- "Consider using X instead of Y" suggestions without concrete problems
- Anything that's clearly intentional from the diff context

## Output Format

### Critical Issues
[Issues that MUST be fixed before merging. Empty if none found.]

For each issue:
- **File**: path/to/file
- **Line(s)**: line range in the diff
- **Issue**: What's wrong
- **Why it matters**: Impact if not fixed
- **Suggested fix**: Concrete code suggestion

### Warnings
[Issues worth considering but not blocking. Empty if none found.]

Same format as critical issues.

### Summary
- Total files reviewed: N
- Critical issues: N
- Warnings: N
- Verdict: LGTM / HAS ISSUES / NEEDS DISCUSSION
```

### Step 3: Dispatch Codex

Use the `shared:codex-dispatch` pattern. Always use the stronger model — code review benefits from reasoning.

```bash
codex exec --full-auto -m gpt-5.4 -C "$(git rev-parse --show-toplevel)" -o "$REVIEW_DIR/codex-review.md" "<review prompt referencing $REVIEW_DIR/diff.patch>"
```

Run with `run_in_background: true` on the Bash tool.

**Codex fallback:** If Codex is unavailable (`command not found`), dispatch a Claude subagent instead:

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: <same review prompt, but include the diff content directly since the subagent can't read /tmp files from the parent>
  run_in_background: true
  name: "diff-reviewer"
  model: "opus"
```

When using Claude fallback, you must include the diff content in the prompt (the subagent can't access the parent's /tmp files). For large diffs that exceed context, tell the user automated review is unavailable without Codex and suggest `/full-review` instead.

**If both Codex and Claude fallback fail:** Tell the user automated diff review is unavailable and suggest they proceed with manual review or try again later.

### Step 4: Read and present results

Once Codex completes:

1. Validate the output file exists and is non-empty
2. Read the review from `$REVIEW_DIR/codex-review.md`
3. Present the results to the user

**If the verdict is LGTM:** Tell the user the diff looks clean. If this was triggered as part of `/ship` or PR creation, proceed to that next step.

**If critical issues found:** Present them and ask the user how to proceed. Do NOT automatically create the PR. Options:

- Fix the issues, then re-run `/diff-review`
- Proceed anyway (user's call)
- Abort

### Step 5: Save output

Keep the review at `$REVIEW_DIR/codex-review.md`. Print the path so the user can reference it.

## Integration with Other Skills

This skill slots in before PR creation. It does NOT auto-trigger — the user invokes it explicitly:

- **`/diff-review` then `/ship`**: Review first, fix issues, then ship
- **`/diff-review` then `/pr-description`**: Review first, then generate PR description
- **Standalone**: Just review the diff without creating a PR

## Common Mistakes

| Mistake                                | Fix                                                         |
| -------------------------------------- | ----------------------------------------------------------- |
| Passing diff as shell argument         | Write to file first, pass file path to Codex                |
| Running on empty diff                  | Check for commits ahead of target first (Step 0)            |
| Using weak model for review            | Always use stronger model — review needs reasoning          |
| Auto-creating PR after critical issues | Stop and ask the user. Never silently proceed.              |
| Including style nitpicks in prompt     | The prompt explicitly excludes style — keep it that way     |
| Skipping project guidelines            | CLAUDE.md has project-specific rules that matter for review |
| Not checking if in a git repo          | Validate with `git rev-parse` before doing anything         |
