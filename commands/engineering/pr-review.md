---
description: Comprehensive code review using specialized subagents with context gathering and synthesis
argument-hint: [pr-number-or-branch]
---

# PR/Code Review

Conduct a comprehensive code review by gathering context, analyzing patterns, and running specialized review subagents in parallel.

**IMPORTANT**: This is a review command. DO NOT make any code changes. Only provide constructive, actionable recommendations.

## Workflow Overview

```
Step 1: Get Code Changes
   ↓
Step 2: Gather Context
   ↓
Step 3: Find Patterns ← 🛑 BLOCKING STEP - MUST COMPLETE BEFORE STEP 4
   ├─ codebase-pattern-finder
   └─ spotify-tool-researcher (if Spotify tooling detected)
   ↓
   📋 CHECKPOINT: Verify pattern findings captured
   ↓
Step 4: Run Review Agents ← 🛑 BLOCKING STEP - MUST COMPLETE BEFORE STEP 5
   ├─ Language-specific review agents (e.g., java-code-simplification-reviewer)
   ├─ Test review agents (e.g., java-test-reviewer)
   └─ general-code-reviewer
   (ALL prompts MUST include findings from step 3)
   ↓
Step 5: Synthesize Findings
   ↓
Step 6: Generate Review Document
```

## Instructions

### 1. Get Relevant Code Changes

**Determine what to review**:
- If the user provided an argument (PR number or branch name), use that
- If no argument provided, check the current branch and ask the user to clarify:
  - "Do you want to review local changes on the current branch against master?"
  - "Or should I review a specific PR/branch? Please provide the PR number or branch name."

**Fetch the code changes**:
- If reviewing a PR:
  - Get PR info: `gh pr view {{PR_NUMBER}} --json number,title,body,headRefName`
  - Get PR diff: `gh pr diff {{PR_NUMBER}}`
- If reviewing a branch against master:
  - Fetch latest: `git fetch origin master`
  - Get diff: `git diff origin/master...{{BRANCH_NAME}}`
  - Get commit history: `git log --oneline origin/master..{{BRANCH_NAME}}`

**Identify primary language(s)**:
- Analyze the diff to determine if the code is primarily Java, Scala/Scio, or other languages
- This will determine which specialized subagents to use in step 4

### 2. Gather Context to Understand Objectives

**IMPORTANT**: Read all context documents in FULL. DO NOT use limit/offset parameters when reading files.

**Gather context from multiple sources**:

a. **PR Description** (if reviewing a PR):
   - Extract the PR description from the output of `gh pr view`
   - Look for objectives, goals, linked issues, and context

b. **Attached Documents**:
   - Check PR description for Google Docs links (e.g., `https://docs.google.com/document/d/...`)
   - If Google Docs are referenced:
     - Use the `mcp__google-drive__get_drive_file_content` tool to read them in FULL
     - DO NOT set limit or offset parameters - read the entire document
   - Check for other referenced documents or design docs

c. **JIRA/Issue Links**:
   - Look for ticket references in PR description or commits
   - Extract context from linked tickets if available

d. **Fallback**:
   - If no PR description and no attached documents exist, ask the user:
     - "I couldn't find a PR description or attached documents. Can you provide context about:"
     - "- What is the objective of these code changes?"
     - "- What problem is being solved?"
     - "- Are there any specific requirements or constraints?"

**Check for domain-specific patterns in the code changes:**

Analyze the diff for domain-specific patterns (reference `commands/shared/domain-agent-registry.md`):

| Domain | Patterns in Diff | Expert Agent | Detected? |
|--------|-----------------|--------------|-----------|
| Flyte/Liftoff | SimpleLiftOffWorkflow, @workflow, @task, FlyteRemote | flyte-liftoff-expert | Yes/No |
| Luigi | luigi.Task, IceScioTask, requires(), Styx | luigi-workflow-expert | Yes/No |
| Scio/Beam | SCollection, JobTest, PipelineSpec, saveAsBigQuery | scio-pipeline-optimization-analyzer | Yes/No |
| Data Annotations | @BigQueryType, @description, semantic_type | data-annotation-reviewer | Yes/No |
| Hendrix/ML | TorchTrainer, Ray, salem, Jukebox, MLflow | hendrix-expert | Yes/No |
| Backend Infra | Decibel, Locus, MMA, Bigtable, Memcached | backend-infrastructure-expert | Yes/No |
| Search/Indexing | Vespa, Ratatoskr, vespa-info.yaml, YQL | search-indexing-expert | Yes/No |
| RCS/Experimentation | RcsProperty, feature flag, experiment | experimentation-expert | Yes/No |

Also check file paths for context signals:
- Files in `ml/`, `training/`, `model/` → Hendrix/ML domain
- Files in `search/`, `indexing/`, `ranking/` → Search/Indexing domain
- Files in `infra/`, `cache/`, `db/` → Backend Infra domain
- `.sd` files → Search/Indexing domain

**Output for user:**
```
## Domains Detected in Code Changes

- ✓ [Domain]: Found "[pattern]" in [file] → Will add [agent-name] to review
- ✗ [Domain]: Not detected
```

Store detected domains for use in Step 4.

**Required: Agent Type Verification**

After detecting domains, create an explicit agent contract:

```
## Agent Type Verification

Based on the language and domains detected above, I will spawn the following agents:

**Language-based agents** (required for [Java/Scala/other]):
- [List from Step 4a based on language]

**Domain-based agents** (added based on detection):
- [For each domain with "Yes" in Detected column: [Domain] → [agent-name]]

**Full agent list for Step 4:**
1. [agent-1]
2. [agent-2]
...

Total agents to spawn: [N]

⚠️ This list is my CONTRACT. All agents listed here MUST be spawned in Step 4.
```

Reference: See `commands/shared/agent-verification-pattern.md` for the full pattern.

---

### 3. Find Existing Code Patterns

⚠️ **BLOCKING STEP - DO NOT PROCEED TO STEP 4 UNTIL THIS IS COMPLETE**

This step discovers existing patterns and best practices in the codebase and Spotify ecosystem. These findings will be included in the prompts for review agents in step 4.

#### Step 3a: Launch Pattern-Finding Agents

**ALWAYS run the codebase-pattern-finder subagent**:

Prompt template:
```
Based on the code changes in [PR #{{PR_NUMBER}} / branch {{BRANCH_NAME}}], find existing code and architectural patterns in the codebase that are relevant to these changes. Focus on:
- Similar implementations that can be used as reference
- Common patterns and idioms used in this codebase
- Architectural conventions that should be followed
- Configuration patterns and feature flag usage
- Error handling and logging patterns
- Testing patterns and conventions

Provide specific examples with file paths and line numbers.
```

**If Spotify-specific tooling was detected in step 2**:

ALSO run the spotify-tool-researcher subagent **IN PARALLEL** with codebase-pattern-finder.

Prompt template:
```
Research the best tools, approaches, and patterns for [specific Spotify tools/systems mentioned: {{LIST_SPOTIFY_TOOLS}}]. Find:
- How these tools are properly used in the Spotify ecosystem
- Best practices and conventions from internal documentation
- Common patterns and anti-patterns
- Integration examples
- Configuration and setup guidelines

Focus on providing concrete guidance that can inform code review.
```

**Launch both agents in parallel**: Use a single message with multiple Task tool calls to launch codebase-pattern-finder and spotify-tool-researcher (if applicable) at the same time.

#### Step 3b: Wait for Completion

🛑 **STOP**: Do not proceed to step 4 until the pattern-finding agents have completed.

Wait for BOTH agents to finish executing. Monitor their progress and do not move forward until you have their complete outputs.

#### Step 3c: Capture Findings

Once the agents complete, capture their findings:
- **Codebase patterns**: Store the output from codebase-pattern-finder
- **Spotify tool research**: Store the output from spotify-tool-researcher (if run)

These findings will be included in the review agent prompts in step 4.

---

**📋 CHECKPOINT: Before proceeding to step 4, verify:**
- [ ] codebase-pattern-finder has completed and you have captured its findings
- [ ] spotify-tool-researcher has completed (if it was launched) and you have captured its findings
- [ ] You have the actual findings content ready to include in step 4 prompts (not just placeholders)
- [ ] You are ready to construct prompts that incorporate these findings

**REQUIRED**: Do not proceed to step 4 unless ALL checkboxes above are verified.

---

### 4. Run Specialized Review Subagents in Parallel

⚠️ **IMPORTANT**: This step runs REVIEW subagents only. The pattern-finding agents from step 3 should already be complete.

#### Step 4a: Determine Which Review Subagents to Run

Based on the primary language(s) identified in step 1, select the appropriate **REVIEW** subagents (see `commands/shared/language-agent-registry.md` for full language mappings):

**For Java code**:
- java-code-simplification-reviewer
- java-test-reviewer
- general-code-reviewer

**For Scala code**:
- scala-scio-code-simplification-reviewer
- scala-scio-test-reviewer
- general-code-reviewer

**For Python code**:
- python-code-simplification-reviewer
- python-test-reviewer
- general-code-reviewer

**For TypeScript/JavaScript code**:
- typescript-code-simplification-reviewer
- typescript-test-reviewer
- general-code-reviewer

**For any other language**:
- general-code-reviewer

**Note**: Domain-based agents (like `scio-pipeline-optimization-analyzer`, `data-annotation-reviewer`) are handled separately via the domain-agent-registry. These are additive - a Scala file using Scio patterns would get both language agents (scala-scio-*) AND domain agents (scio-pipeline-optimization-analyzer).

**Domain-based reviewers (add if detected in Step 2):**

For each domain detected in Step 2, add the corresponding expert to the review agent list:

- Flyte/Liftoff detected → Add `flyte-liftoff-expert`
- Luigi detected → Add `luigi-workflow-expert`
- Scio patterns detected → Add `scio-pipeline-optimization-analyzer`
- Data annotations detected → Add `data-annotation-reviewer`
- Hendrix/ML detected → Add `hendrix-expert`
- Backend Infra detected → Add `backend-infrastructure-expert`
- Search/Indexing detected → Add `search-indexing-expert`
- RCS/Experimentation detected → Add `experimentation-expert`

**Prompt template for domain experts:**
```
Review the [DOMAIN] code changes in this PR.

## Context and Objectives
{{CONTEXT_FROM_STEP_2}}

## Existing Patterns
{{CODEBASE_PATTERN_FINDINGS}}

## Code Access
- PR Number: {{PR_NUMBER}}
- To get the diff: gh pr diff {{PR_NUMBER}}

## Review Focus
- Check adherence to [DOMAIN] patterns and conventions
- Identify [DOMAIN]-specific issues or anti-patterns
- Suggest [DOMAIN] best practices where applicable
- Verify proper use of [DOMAIN] APIs and configurations
```

**Combined agent list**: Merge language-based and domain-based agents, launch all in parallel in Step 4c.

**DO NOT include in this step**: codebase-pattern-finder and spotify-tool-researcher (they were already run in step 3)

#### Step 4b: Construct Prompts with Pattern Findings

⚠️ **CRITICAL**: Each review agent prompt MUST include the findings from step 3.

**Before constructing prompts, verify:**
- [ ] You have the codebase pattern findings from step 3
- [ ] You have the Spotify tool research findings from step 3 (if applicable)
- [ ] You are ready to populate the placeholders with actual content

**Prompt template for each review subagent**:

```
Review the code changes in [PR #{{PR_NUMBER}} / branch {{BRANCH_NAME}}].

## Context and Objectives
{{CONTEXT_FROM_STEP_2}}

## Existing Patterns and Best Practices
**IMPORTANT**: The following sections contain findings from step 3 that should inform your review.

### Codebase Patterns
{{CODEBASE_PATTERN_FINDINGS}}

### Spotify Tool Best Practices
{{SPOTIFY_TOOL_RESEARCH_FINDINGS}}

## Code Access
- PR Number: {{PR_NUMBER}} (if applicable)
- Branch: {{BRANCH_NAME}} (if applicable)
- To get the diff: gh pr diff {{PR_NUMBER}} OR git diff origin/master...{{BRANCH_NAME}}

## Review Focus
Focus on your specialized area of review:
- [Customize based on subagent type - e.g., "code simplification opportunities" for java-code-simplification-reviewer]
- Compare the implementation against the patterns identified above
- Do not duplicate efforts with other subagents
- Provide specific, actionable recommendations with file paths and line numbers
```

**Replace placeholders with actual content**:
- `{{CONTEXT_FROM_STEP_2}}`: Replace with the actual context gathered in step 2
- `{{CODEBASE_PATTERN_FINDINGS}}`: Replace with the actual findings from codebase-pattern-finder
- `{{SPOTIFY_TOOL_RESEARCH_FINDINGS}}`: Replace with the actual findings from spotify-tool-researcher (or remove this section if not applicable)

#### Step 4c: Launch Review Agents in Parallel

**REQUIRED: Pre-Spawn Verification Table**

Before making Task tool calls, output a verification table:

```
## Pre-Spawn Verification

Cross-checking Agent Type Verification from Step 2 against Task calls I'm about to make:

| # | Agent Type (from Contract) | Will Spawn? | Reason if Skipping |
|---|---------------------------|-------------|-------------------|
| 1 | [agent-1] | ✓ Yes | - |
| 2 | [agent-2] | ✓ Yes | - |
...

**Verification Result:**
- Agents in contract: [N]
- Agents to spawn: [M]

✓ All agents will be spawned? [YES/NO]
```

**BLOCKER**: If any agent is skipped, you MUST provide a reason in the table AND inform the user.

**CRITICAL**: Launch ALL applicable REVIEW subagents (from the list in step 4a) IN PARALLEL using a single message with multiple Task tool calls.

Example for Java code:
- Launch java-code-simplification-reviewer with its prompt
- Launch java-test-reviewer with its prompt
- Launch general-code-reviewer with its prompt

All three should be launched in the same message with three separate Task tool calls.

#### Step 4d: Wait for Completion

🛑 **STOP**: Do not proceed to step 5 until all review agents have completed.

Wait for ALL review agents to finish executing before moving to synthesis.

---

**📋 CHECKPOINT: Before proceeding to step 5, verify:**
- [ ] All review agents have completed
- [ ] You have captured the findings from each review agent
- [ ] You are ready to synthesize and deduplicate the findings

---

### 5. Synthesize Findings

**REQUIRED: Pre-Synthesis Agent Verification**

Before synthesizing, verify all contracted agents completed:

```
## Pre-Synthesis Agent Verification

From Agent Type Verification (Step 2):
- Total agents contracted: [N]

Agents actually spawned:
- [List each agent and whether it completed]
- Total spawned: [M]

✓ Verification: N = M? [YES/NO]

If NO: List missing agents and either spawn them now OR explain to user why they're being skipped.
```

**BLOCKER**: Do not proceed with synthesis if N ≠ M without user acknowledgment.

Once all review subagents have completed:

1. **Collect all findings** from each subagent:
   - Findings from java-code-simplification-reviewer (or other language-specific reviewer)
   - Findings from test reviewer
   - Findings from general-code-reviewer

2. **Identify common themes** across multiple subagents:
   - Issues that multiple agents identified
   - Patterns that appear in multiple parts of the code

3. **Prioritize issues** by severity:
   - **Critical**: Must fix before merge (correctness, security, breaking changes, memory leaks)
   - **Major**: Should fix before merge (design issues, missing tests, performance problems, unused code)
   - **Minor**: Nice to have (style, small improvements, code clarity)
   - **Enhancement**: Future improvements (refactoring opportunities, optimizations)

4. **Deduplicate**: If multiple subagents identified the same issue, consolidate into a single entry:
   - Keep the most detailed explanation
   - Cite which agents identified the issue
   - Combine recommendations if they differ

5. **Extract highlights**: Positive patterns, good practices, well-executed implementations:
   - What was done well?
   - What should be maintained in future work?
   - What can be learned from this implementation?

### 5.5 Calculate Diff Positions

For each recommendation that will be included in the review document, calculate the GitHub diff position.

**Get the full diff**:
```bash
gh pr diff {{PR_NUMBER}}
```

**Algorithm for each recommendation**:

1. Extract file path and line number from the recommendation
2. Find the file in the diff output
3. Parse hunk headers: `@@ -old_start,old_count +new_start,new_count @@`
4. For each hunk:
   - Position starts at 1 after the `@@` line
   - For each line in the hunk:
     - If line starts with `+` or ` ` (added or context): this is a "new file" line
     - Track mapping: {new_line_number → position}
     - Increment position for every line (including `-` lines)
     - Increment new_line_number only for `+` and ` ` lines
5. Look up the recommendation's line number in the mapping

**Position calculation pseudocode**:
```
for each file in diff:
    position = 0
    new_line = <start from hunk header +new_start>

    for each line in file's hunks:
        position += 1

        if line starts with '+' or ' ':
            position_map[file][new_line] = position
            new_line += 1
        elif line starts with '-':
            # Don't increment new_line for removed lines
            pass
```

**Result categories**:
- **Has position**: Line is in the diff → use `<!-- diff-position:N -->`
- **Not in diff**: Line exists but not in any hunk → use `<!-- diff-position:body -->`
- **File not in diff**: File wasn't changed in PR → use `<!-- diff-position:body -->`

Store the position mapping for use in Step 6.

---

### 6. Generate Review Document

**Ensure the output directory exists**:
```bash
mkdir -p ~/.claude/thoughts/shared/reviews/
```

**Create a unique filename**:
- Format: `review_{{PR_NUMBER}}_{{TIMESTAMP}}.md` OR `review_{{BRANCH_NAME}}_{{TIMESTAMP}}.md`
- Example: `review_pr_1234_2025-10-16.md`

**Write the review document** to `~/.claude/thoughts/shared/reviews/{{FILENAME}}` using this exact format:

```markdown
# [PR #{{PR_NUMBER}}: {{PR_TITLE}}] Review
OR
# [Branch: {{BRANCH_NAME}}] Review

## High level summary

[2-3 sentences summarizing the review findings. Include overall assessment, key concerns, and general recommendation.]

## Do the code changes align with the PR objective?

["Yes" or "No" answer with an explanation why]

## Highlights

- [Positive pattern or well-executed implementation from the code]
- [Commendable architectural decision or design choice]
- [Excellent test coverage or documentation example]
- [Any other noteworthy positive aspects]

## Prioritized Issues

### Summary

[2-3 sentence summary of the critical and major issues that must be addressed. Provide context on impact and urgency.]

### Critical

[If no critical issues, write "None found."]

- Recommendation [i] - `path/to/file.ext:line` <!-- diff-position:N -->
**Issue**: [Detailed description of the root problem]
**Fix**: [Specific, actionable resolution steps]

### Major

[If no major issues, write "None found."]

- Recommendation [i] - `path/to/file.ext:line` <!-- diff-position:N -->
**Issue**: [Detailed description of the root problem]
**Fix**: [Specific, actionable resolution steps]

### Minor

[If no minor issues, write "None found."]

- Recommendation [i] - `path/to/file.ext:line` <!-- diff-position:N -->
**Issue**: [Detailed description of the root problem]
**Fix**: [Specific, actionable resolution steps]

### Enhancement

[If no enhancements, write "None found."]

- Recommendation [i] - `path/to/file.ext:line` <!-- diff-position:N -->
**Issue**: [Description of the improvement opportunity]
**Fix**: [Specific suggestion for enhancement]
```

**Note on diff positions**: Each recommendation includes a hidden HTML comment with the GitHub diff position (calculated in Step 5.5). This enables automated PR comment submission via `/pr-review-claudit`. If the line is not in the diff, use `<!-- diff-position:body -->` to indicate it should go in the review body. Replace `[i]` with sequential integers starting at 1.

**Confirm completion**:
- Display the path to the generated review document
- Provide a brief summary of the findings (e.g., "Found 2 critical, 5 major, 3 minor issues, and 4 enhancement opportunities")
- Remind the user that this was a review only - no code changes were made

## Important Notes

- **No code modifications**: This command only reviews and generates a report. Never modify code files.
- **Read documents fully**: Always read context documents completely without limit/offset parameters
- **Sequential execution of steps 3 and 4**: Step 3 (pattern finding) MUST complete before step 4 (review agents) begins
- **Parallel execution within steps**: Within step 3, launch pattern-finding agents in parallel. Within step 4, launch review agents in parallel.
- **Include patterns in prompts**: Review agent prompts in step 4 MUST include the findings from step 3
- **Constructive feedback**: Ensure all feedback is actionable, specific, and constructive
- **Deduplication**: Consolidate duplicate findings from multiple subagents
- **File references**: Always include specific file paths and line numbers in issue descriptions
