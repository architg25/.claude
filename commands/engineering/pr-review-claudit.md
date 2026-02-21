---
description: Integrated PR review with claudit for reviewing and submitting inline comments
argument-hint: <pr-number-or-review-doc-path>
---

# PR Review with Claudit

Conduct a comprehensive PR review using claudit for interactive review and editing, then submit inline comments to the PR.

## Workflow Overview

```
Step 1: Parse Arguments
   ├─ PR number → generate/find review doc
   └─ Review doc path → use existing
   ↓
Step 2: Claudit Plan Mode (review doc)
   └─ User edits/removes recommendations
   ↓
Step 3: Process Plan Comments
   └─ Apply edits, track removals
   ↓
Step 4: Checkout PR Branch
   └─ git fetch && checkout
   ↓
Step 5: Claudit Diff Mode (code)
   └─ User adds inline code comments
   ↓
Step 6: Collate Comments
   └─ Combine remaining recommendations + diff comments
   ↓
Step 7: Choose Review Status
   └─ Approve / Request Changes / Comment
   ↓
Step 8: Submit PR Review
   └─ GitHub API submission
   ↓
Step 9: Cleanup & Summary
```

## Step 1: Parse Arguments

Argument: `$1`

**Determine argument type**:

If argument is empty:
- Ask user: "Please provide a PR number or path to an existing review document."
- Wait for response, then continue with the provided value.

If argument looks like a number or PR URL (matches `^[0-9]+$` or contains `pull/[0-9]+`):
- Extract PR number: `echo "$1" | grep -oE '[0-9]+$'`
- Validate PR exists:
  ```bash
  gh pr view $PR_NUMBER --json number -q '.number' 2>/dev/null
  ```
- If invalid, tell user and STOP.
- Check for existing review doc:
  ```bash
  ls -t ~/.claude/thoughts/shared/reviews/review_*${PR_NUMBER}*.md 2>/dev/null | head -1
  ```
- If found, ask user: "Found existing review document: `<path>`. Use this or generate fresh?"
  - Use AskUserQuestion with options: "Use existing" / "Generate fresh"
- If generating fresh or no doc found:
  - Run the `/pr-review` workflow to generate a review document
  - Store the output path as `REVIEW_DOC_PATH`

If argument looks like a file path (contains `/` or `.md`):
- Convert to absolute path:
  ```bash
  realpath "$1" 2>/dev/null || echo "$1"
  ```
- Verify file exists:
  ```bash
  test -f "<absolute-path>" && echo "exists" || echo "not found"
  ```
- If not found, tell user and STOP.
- Extract PR number from filename or content:
  1. Try filename: `basename "$1" | grep -oE '_[0-9]+_' | tr -d '_'`
  2. If not found, search content: `grep -oE 'PR #[0-9]+' "$1" | head -1 | grep -oE '[0-9]+'`
  3. If still not found, ask user: "Could not determine PR number. Please provide:"
- Store `REVIEW_DOC_PATH` and `PR_NUMBER`

**Output**:
```
Using review document: $REVIEW_DOC_PATH
PR Number: #$PR_NUMBER
```

## Step 2: Claudit Plan Mode - Review Document

Kill any existing claudit instance:
```bash
pkill -f "claudit" 2>/dev/null || true
```

Start claudit in plan mode, explicitly setting the project directory:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CLAUDE_MODE=plan CLAUDE_PLAN_FILE="$REVIEW_DOC_PATH" CLAUDE_PROJECT_DIR="$PROJECT_ROOT" claudit &
```

Tell the user:
```
Claudit is running at http://localhost:3456 in **plan review mode**.

Reviewing: `$REVIEW_DOC_PATH`

Please:
1. Open the URL in your browser
2. Review the recommendations
3. Add comments like "Remove this" on any recommendations you want to EXCLUDE from the PR review
4. Add comments for any edits you want to make to the document
5. Come back here and say "done" when finished
```

**IMPORTANT**: Stop here and wait for the user to respond. Do NOT proceed until the user indicates they are done reviewing.

## Step 3: Process Plan Comments

Read plan comments using an absolute path:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
COMMENTS_FILE="$PROJECT_ROOT/.claude/plan-comments.json"
echo "Comments file: $COMMENTS_FILE"
cat "$COMMENTS_FILE" 2>/dev/null || echo '{"comments":[]}'
```

Then use the Read tool on the absolute path printed above to read the comments JSON.

**Categorize each comment**:

For each comment in the JSON:

1. **Check if it's a removal comment**:
   - Lowercase the comment text
   - Check if it contains any of: "remove", "delete", "skip", "exclude", "drop"
   - If yes: Mark this recommendation for exclusion
     - Find the recommendation at `sourceLine`
     - Extract recommendation number (e.g., "Recommendation 3")
     - Add to `EXCLUDED_RECOMMENDATIONS` list

2. **If not a removal comment**:
   - Treat as an edit request
   - Read the review doc
   - Navigate to `sourceLine`
   - Apply the requested edit using Edit tool
   - Confirm change to user

**After processing all comments**:

Kill claudit:
```bash
pkill -f "claudit" 2>/dev/null || true
```

Clean up plan comments:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
rm -f "$PROJECT_ROOT/.claude/plan-comments.json" 2>/dev/null
```

**Output**:
```
Processed X comments:
- Y recommendations marked for exclusion: [list numbers]
- Z edits applied to review document
```

## Step 4: Checkout PR Branch

Get branch name:
```bash
BRANCH_NAME=$(gh pr view $PR_NUMBER --json headRefName -q '.headRefName')
```

Attempt checkout:
```bash
git fetch origin $BRANCH_NAME 2>&1
git checkout $BRANCH_NAME 2>&1
```

**Error handling**:

1. **If checkout fails due to uncommitted changes** (output contains "uncommitted changes" or "would be overwritten"):
   - Use AskUserQuestion:
     - "Cannot checkout branch - you have uncommitted changes."
     - Options:
       - "Stash and continue" - Run `git stash` then retry checkout
       - "Skip checkout, use PR diff only" - Continue without local checkout

2. **If branch doesn't exist or other error**:
   - Warn user with the error message
   - Ask: "Continue with claudit diff review? (Claudit can still show the PR diff via GitHub API)"
   - If yes, continue. If no, STOP.

## Step 5: Claudit Diff Mode - Code Review

Start claudit in diff mode, explicitly setting the project directory:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CLAUDE_PROJECT_DIR="$PROJECT_ROOT" claudit &
```

Tell the user:
```
Claudit is running at http://localhost:3456 showing the code diff.

Please:
1. Open the URL in your browser
2. Review the actual code changes
3. Add inline comments for any additional feedback (beyond the review document)
4. Come back here and say "done" when finished
```

**IMPORTANT**: Stop here and wait for the user to respond.

## Step 6: Collate Comments

Read diff comments using an absolute path:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
COMMENTS_FILE="$PROJECT_ROOT/.claude/diff-comments.json"
echo "Comments file: $COMMENTS_FILE"
cat "$COMMENTS_FILE" 2>/dev/null || echo '{"comments":[]}'
```

Then use the Read tool on the absolute path printed above to read the comments JSON.

**Build final comment list**:

1. **Parse remaining recommendations from review document**:
   - Read `$REVIEW_DOC_PATH`
   - Find all lines matching: `- Recommendation [0-9]+ - .* <!-- diff-position:`
   - For each recommendation:
     - Skip if recommendation number is in `EXCLUDED_RECOMMENDATIONS`
     - Extract: file path, line number, diff position, issue text, fix text
     - Add to `FINAL_COMMENTS` list

2. **Parse diff comments from claudit**:
   - For each comment in diff-comments.json:
     - File path: comment.file
     - Line number: comment.line
     - Text: comment.text
     - Need to calculate diff position (see below)
     - Add to `FINAL_COMMENTS` list

**Calculate diff positions for claudit comments**:

For each claudit diff comment that doesn't have a position:

1. Get the PR diff:
   ```bash
   gh pr diff $PR_NUMBER
   ```

2. Parse the diff to find the position:
   - Find the file's section in the diff
   - Parse each hunk header: `@@ -old,count +new,count @@`
   - Position = 1 after the @@ line
   - For each line in the hunk:
     - If line starts with `+` or ` `: map new_line_number to current position
     - Increment position for every line
     - Increment new_line_number only for `+` and ` ` lines
   - Look up the comment's line in the mapping

3. If position not found (line not in diff):
   - Add comment to `BODY_COMMENTS` list instead (for review body)

Kill claudit:
```bash
pkill -f "claudit" 2>/dev/null || true
```

Clean up diff comments:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
rm -f "$PROJECT_ROOT/.claude/diff-comments.json" 2>/dev/null
```

**Output**:
```
Collated comments:
- X inline comments (from review doc)
- Y inline comments (from claudit)
- Z comments will go in review body (not in diff)
```

## Step 7: Choose Review Status

Use AskUserQuestion:

"How would you like to submit this review?"

Options:
1. **Comment (default)** - Submit feedback without explicit approval or rejection
2. **Approve** - Approve the PR with your comments
3. **Request Changes** - Request changes before the PR can be merged

Map selection to GitHub event:
- Comment → "COMMENT"
- Approve → "APPROVE"
- Request Changes → "REQUEST_CHANGES"

## Step 8: Submit PR Review

Get commit SHA:
```bash
HEAD_SHA=$(gh pr view $PR_NUMBER --json headRefOid -q '.headRefOid')
```

Get repository info:
```bash
REPO_INFO=$(gh repo view --json owner,name -q '"\(.owner.login)/\(.name)"')
# OR from remote
REPO_INFO=$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
```

**Build review body**:

Combine:
- High-level summary from review doc (first few sentences)
- Any `BODY_COMMENTS` that couldn't be attached to specific lines

**Build inline comments array**:

For each comment in `FINAL_COMMENTS`:
```json
{
  "path": "<file_path>",
  "position": <diff_position>,
  "body": "<comment_text>"
}
```

**Submit review**:
```bash
cat << 'EOF' | gh api repos/$REPO_INFO/pulls/$PR_NUMBER/reviews -X POST --input -
{
  "commit_id": "$HEAD_SHA",
  "event": "$EVENT",
  "body": "$REVIEW_BODY",
  "comments": [
    // inline comments array
  ]
}
EOF
```

**Handle errors**:
- If API returns error about invalid position:
  - Log which comment failed
  - Move that comment to the review body
  - Retry without that inline comment
- If other error:
  - Show error to user
  - Offer to save comments to file for manual submission

**Output**:
```
Review submitted successfully!

PR: #$PR_NUMBER
Status: $EVENT
Inline comments: X
Body comments: Y

View at: https://github.com/$REPO_INFO/pull/$PR_NUMBER
```

## Step 9: Cleanup and Summary

Ensure claudit is stopped:
```bash
pkill -f "claudit" 2>/dev/null || true
```

Ensure comment files are cleaned:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
rm -f "$PROJECT_ROOT/.claude/plan-comments.json" "$PROJECT_ROOT/.claude/diff-comments.json" 2>/dev/null
```

**Final summary**:
```
## PR Review Complete

**PR**: #$PR_NUMBER
**Review Status**: $EVENT
**Inline Comments Submitted**: X
**Recommendations Excluded**: Y
**Review Document**: $REVIEW_DOC_PATH
**View Review**: https://github.com/$REPO_INFO/pull/$PR_NUMBER

Note: The review document has been updated with your edits.
```

## Important Notes

- This command orchestrates multiple tools and waits for user input at each claudit stage
- Comments marked for removal in plan mode are excluded from the final PR review
- The review document is updated with any edits made during plan mode review
- If diff position calculation fails for a recommendation, it's included in the review body instead
- The command handles both PR numbers and existing review doc paths
