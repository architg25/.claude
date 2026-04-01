---
name: review
description: Use when the user wants a code review — either local changes before creating a PR, or an existing PR. Triggers on "review my changes", "review my diff", "review this PR", "check my code", /review, or before invoking engineering:pr-description or engineering:ship.
allowed-tools: Read, Glob, Grep, Bash(bash ~/.claude/skills/*/scripts/*), Bash(gh pr *), Bash(codex exec *), Bash(git diff *), Bash(git fetch *), Bash(git rev-parse *), Bash(git symbolic-ref *), Bash(mkdir *), Bash(wc *), Agent, mcp__code-search__search_code, mcp__code-search__read_file, mcp__code-search__count_matches
---

# Review

Review code changes using two AI model families (Claude + Codex) for independent cross-checking. Works on local diffs (pre-PR) and existing PRs.

## Usage

```
/review                       # Local diff, dual-agent
/review <PR_URL>              # PR review, dual-agent
/review <PR_URL> --claude     # PR review, Claude only
/review <PR_URL> --codex      # PR review, Codex only
/review --quick               # Local diff, single-agent (Codex only)
```

**Always use full PR URLs** (e.g., `https://github.com/org/repo/pull/123`).

## Mode Detection

- **PR mode:** URL argument provided
- **Diff mode:** no URL + inside a git repo with changes ahead of target branch
- **Error:** not in a git repo and no URL

## Policy / Safety

All providers must use enterprise accounts. Do not use personal API keys for internal repositories.

## Instructions

### Step 0: Assess complexity and select models

**Before classifying, look at what you're reviewing.** In PR mode, fetch the title and changed files first:

```bash
gh pr view <PR_NUMBER> -R <REPO> --json title,files --jq '{title: .title, files: [.files[].path]}'
```

In diff mode, scan the diff output.

Then classify using `shared:complexity-assessment`. Read `shared:dual-agent-dispatch` for the dispatch pattern. Do NOT use model names from memory.

---

### Diff Mode (no URL argument)

#### Step 1: Get the diff

```bash
git rev-parse --is-inside-work-tree
```

If not in a git repo, stop and tell the user.

Detect target branch and generate diff:

```bash
TARGET=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || echo "master")
git fetch origin "$TARGET"
git diff "origin/$TARGET"...HEAD
```

Empty diff = nothing to review. Stop.

**Size check** (`git diff "origin/$TARGET"...HEAD | wc -l`):

- **<5000 lines:** proceed normally
- **5000-15000:** warn user, filter out tests/generated:
  ```bash
  git diff "origin/$TARGET"...HEAD -- . ':!**/test/**' ':!**/tests/**' ':!**/*Test.*' ':!**/*Spec.*' ':!**/generated/**' ':!**/*.generated.*'
  ```
- **>15000 lines:** abort. Suggest splitting the PR or reviewing specific directories.

#### Step 2: Build context

Check for project guidelines: `Glob: CLAUDE.md, .claude/CLAUDE.md, AGENTS.md`. Read if found.

Write diff to file:

```bash
REVIEW_DIR="/tmp/review-$(date +%s)" && mkdir -p "$REVIEW_DIR"
git diff "origin/$TARGET"...HEAD > "$REVIEW_DIR/diff.patch"
```

#### Step 3: Build review prompt

```
You are reviewing a code diff before it becomes a pull request. Find real problems, not style nitpicks.

<CLAUDE.md content if found>

## Instructions
Read the diff at <path> and review it.

## Review Criteria (priority order)
1. **Bugs** — Logic errors, off-by-ones, null handling, race conditions
2. **Security** — Injection, auth bypass, secrets exposure, OWASP top 10
3. **Breaking changes** — API contract violations, backwards incompatibility
4. **Missing tests** — New logic paths without test coverage
5. **Performance** — N+1 queries, unbounded collections, obvious inefficiencies

Do NOT flag: style preferences, missing comments, "consider X" without concrete problems.

## Output Format
### Critical Issues
[Must-fix before merging. For each: File, Lines, Issue, Impact, Suggested fix]

### Warnings
[Worth considering but not blocking. Same format.]

### Summary
- Files reviewed: N
- Critical issues: N
- Warnings: N
- Verdict: LGTM / HAS ISSUES / NEEDS DISCUSSION
```

#### Step 4: Dispatch

**Dual (default):** Per `shared:dual-agent-dispatch`, launch Claude subagent + Codex in parallel:

- Claude subagent: include diff content directly in prompt (subagents can't read parent's /tmp)
- Codex: reference `$REVIEW_DIR/diff.patch` file path

**Quick (`--quick`):** Codex only, skip Claude subagent.

#### Step 5: Synthesize and present

Per `shared:dual-agent-dispatch` synthesis pattern:

- Consensus issues = critical (both flagged it)
- Single-source issues = warnings (only one flagged it)
- Conflicts = investigate yourself

**If critical issues found:** present and ask user how to proceed. Do NOT auto-create PR.
**If LGTM:** tell the user the diff looks clean. If this was part of `/ship`, proceed.

Output stays at `$REVIEW_DIR/` — print the path.

---

### PR Mode (URL argument)

#### Step 1: Run the review script

The script fetches PR metadata + diff via `gh` and sends it to one AI provider:

```bash
scripts/ai-pr-review.sh <provider> <PR_URL> --claude-model <MODEL> --codex-model <MODEL> [--post]
```

**Getting the PR URL:**

- Full URL provided: use directly
- PR number only: construct full URL from current repo context
- No PR specified: detect with `gh pr view --json url --jq .url`

#### Step 2: Select mode

**Dual (default):** Run the script twice in parallel — once with `claude`, once with `codex`:

```bash
scripts/ai-pr-review.sh claude "$PR_URL" --claude-model <MODEL> &
scripts/ai-pr-review.sh codex "$PR_URL" --codex-model <MODEL> &
wait
```

**Single (`--claude` or `--codex`):** Run the script once with the specified provider.

#### Step 3: Read and synthesize

For dual mode, read both review files and synthesize per `shared:dual-agent-dispatch`.

For single mode, present the review directly.

Reviews are saved to `/tmp/pr-review-<PR_NUMBER>/`:

- `claude.md` — Claude's review
- `codex.md` — Codex's review

#### Step 4: Post (if `--post`)

Save synthesis to `/tmp/pr-review-<PR_NUMBER>/synthesized.md` and post:

```bash
gh pr comment <PR_URL> --body-file /tmp/pr-review-<PR_NUMBER>/synthesized.md
```

---

## Synthesis Format (dual mode)

```markdown
## Synthesized Review

**Reviewers**: Claude, Codex

### Critical Issues (consensus)

[Issues flagged by both reviewers]

### Important Issues

[Issues from individual reviewers]

### Suggestions

[Minor improvements]

### Reviewer Disagreements

[Where they differed — include your investigation]
```

Priority order: security > bugs > guideline violations > performance > code quality.

## Common Mistakes

| Mistake                                 | Fix                                  |
| --------------------------------------- | ------------------------------------ |
| Passing large diff as shell argument    | Write to file, pass path             |
| Running on empty diff                   | Check for changes first              |
| Auto-creating PR after critical issues  | Stop and ask the user                |
| Including style nitpicks                | Prompt explicitly excludes them      |
| Skipping project guidelines             | CLAUDE.md has project-specific rules |
| Not checking if in git repo (diff mode) | Validate with `git rev-parse` first  |
