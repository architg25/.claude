---
description: Commit, push, and create/update PR using engineering:commit and engineering:pr-description
---

# Ship: Commit, Push, and Create/Update PR

This skill chains `engineering:commit` and `engineering:pr-description` into a single workflow.

## Process

### Step 1: Commit changes

Invoke the `engineering:commit` skill using the Skill tool:

```
Skill: engineering:commit
```

Wait for the commit to complete before proceeding. If there are no changes to commit, skip to Step 2 (there may still be unpushed commits).

### Step 2: Push the branch

After the commit is done:

1. Check the current branch: `git branch --show-current`
2. If on `main` or `master`, **STOP** — do not push directly to the default branch. Ask the user to create a feature branch first. If in services-pilot repo, create a branch with my username prefix, e.g architg/feature-branch. You can also suggest branch name using commits, but be very concise.
3. Check if the branch has an upstream: `git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>&1`
4. Push the branch:
   - If upstream exists: `git push`
   - If no upstream: `git push -u origin HEAD`

### Step 3: Create or update PR

Invoke the `engineering:pr-description` skill using the Skill tool:

```
Skill: engineering:pr-description
```

This skill already handles:

- Generating the PR description from the diff
- Checking if a PR already exists for the branch (`gh pr view`)
- **If PR exists**: Updates the existing PR description (`gh pr edit`)
- **If no PR exists**: Creates a new PR (`gh pr create`)

## Important

- Each step depends on the previous one — run them sequentially, never in parallel.
- If any step fails, stop and report the error. Do not continue to the next step.
- The `engineering:pr-description` skill handles the create-vs-update logic, so this skill does not need to duplicate that check.
