# Research Problem

You are tasked with conducting comprehensive research across the codebase and beyond to answer user questions by spawning parallel sub-agents and synthesizing their findings.

## Core Principle: Document and Explain What Exists

Your role is to document and explain the codebase as it currently exists:

- Describe what exists, where it exists, how it works, and how components interact
- Focus on creating a technical map/documentation of the existing system
- Suggest improvements, root cause analysis, or enhancements only when the user explicitly requests them
- Keep recommendations and critiques out of scope unless asked

## Initial Setup:

When this command is invoked, respond with:

```
I'm ready to research the problem. Please provide your research question or area of interest, and I'll analyze it thoroughly by exploring relevant components and connections.
```

Then wait for the user's research query.

## Steps to follow after receiving the research query:

1. **Read any directly mentioned files first:**
   - If the user mentions specific files (tickets, docs, JSON, etc.), read them FULLY first
   - Google docs should also be read into the main context using the google-drive mcp tool. Make sure all referenced Google docs files are read in the main context
   - **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files UNLESS the user has given explicit instructions not to read a file in its entirety
   - Read these files yourself in the main context before spawning any sub-tasks
   - This ensures you have full context before decomposing the research.

2. **Analyze and decompose the research question:**
   - **Consider the research problem carefully from multiple angles**
   - **Write out all specific questions in your response text for the user to see**
   - Format the questions clearly in the terminal output:

     ```
     ## Research Questions

     To answer "[user's question]", I need to investigate:

     1. [Question 1] → Will use [subagent-type]
     2. [Question 2] → Will use [subagent-type]
     3. [Question 3] → Will use [subagent-type]
     ...
     ```

   - **List assumptions being made:**
     - After listing questions, identify and document assumptions about the research problem
     - Format assumptions clearly in the terminal output:

     ```
     ## Assumptions

     In approaching "[user's question]", I am making the following assumptions:

     **Explicit assumptions** (directly stated or strongly implied by the query):
     1. [Assumption about scope, e.g., "Research is limited to this repository"]
     2. [Assumption about intent, e.g., "You want documentation, not recommendations"]
     ...

     **Implicit assumptions** (inferred from context):
     1. [Assumption about domain, e.g., "The system uses standard Spotify infrastructure"]
     2. [Assumption about methodology, e.g., "Current codebase is source of truth over old docs"]
     ...

     **Constraints assumed:**
     1. [Time/scope constraints, e.g., "Research should complete in one session"]
     2. [Access constraints, e.g., "All relevant code is in this repository"]
     ```

   - **Define success criteria:**
     - After listing assumptions, define what would constitute a complete answer
     - Format success criteria clearly in the terminal output:

     ```
     ## Success Criteria

     This research will be considered complete when:
     - [ ] [Specific deliverable, e.g., "All authentication entry points are identified with file paths"]
     - [ ] [Level of detail required, e.g., "Each component's role in the flow is documented"]
     - [ ] [Scope of coverage, e.g., "Both happy path and error handling are covered"]
     ```

   - **Define explicit scope boundaries:**
     - After success criteria, clearly state what is OUT of scope
     - Format scope boundaries clearly in the terminal output:

     ```
     ## Scope

     **In scope:**
     - [What will be investigated]
     - [Systems/components to cover]

     **Explicitly out of scope:**
     - [What will NOT be investigated, e.g., "Historical implementations before 2023"]
     - [Systems to exclude, e.g., "Shared libraries outside this repository"]
     - [Depth limits, e.g., "Will not deep-dive into database schemas"]
     ```

   - **Identify known starting points and prior knowledge:**
     - Extract any files, components, or systems mentioned in the user's question
     - Note what the user appears to already understand
     - Format in the terminal output:

     ```
     ## Research Context

     **Known starting points** (extracted from your question):
     - [File/component mentioned, e.g., "`AuthService.java` - mentioned in question"]
     - [Or: "None explicitly mentioned - will discover through research"]

     **Prior knowledge assumed** (what you appear to already understand):
     - [Inferred knowledge, e.g., "Familiar with OAuth flow based on question framing"]
     - [Or: "Assuming standard domain familiarity; will explain system-specific details"]

     **Previous research** (if any):
     - [Link to existing research docs if found in ~/.claude/thoughts/shared/research/]
     - [Or: "No prior research found on this topic"]
     ```

   - **Analyze question dependencies and create an execution plan:**
     - After identifying all questions, evaluate how they relate to each other
     - For each question, consider:
       - Does answering this question first provide context that makes other questions easier or more focused?
       - Does this question depend on knowing the answer to another question?
       - Is this question completely independent and can run in parallel with others?
     - **Types of dependencies to consider:**
       - **Scope narrowing**: Early questions may reveal the specific files/systems to focus on
       - **Vocabulary/terminology**: Early questions may reveal domain-specific terms needed for later searches
       - **Architecture understanding**: Understanding system structure first may make component questions more targeted
       - **Existence validation**: Confirming something exists before researching how it works
     - Create a dependency analysis and execution plan:

     ```
     ## Research Execution Plan

     **Dependency Analysis:**

     | Question | Depends On | Rationale |
     |----------|------------|-----------|
     | Q1 | None | Independent starting point |
     | Q2 | Q1 | Q1's answer about [X] will narrow the scope of Q2's search |
     | Q3 | None | Independent - different system/domain |
     | Q4 | Q2, Q3 | Needs synthesis of both findings to form focused query |

     **Execution Batches:**

     ```

     Batch 1 (parallel): Q1, Q3
     ↓ (wait for completion, extract key context)
     Batch 2 (parallel): Q2 (informed by Q1 findings)
     ↓ (wait for completion)
     Batch 3: Q4 (informed by Q2 + Q3 findings)

     ```

     **Context to pass between batches:**
     - After Batch 1: [What specific information from Q1/Q3 will inform later questions]
     - After Batch 2: [What specific information from Q2 will inform later questions]
     ```

   - **Default to parallelism when uncertain:**
     - If the dependency is weak or speculative, prefer parallel execution for speed
     - Only sequence questions when there's a clear benefit to waiting for earlier answers
     - Over-parallelizing is acceptable; missing dependencies will be caught in the validation loop (Step 6)
   - For each assumption, consider:
     - Is this something the user explicitly stated?
     - Is this something I inferred from the question or context?
     - Could this assumption be wrong, and would that change my approach?
   - For each question identified, determine:
     - What type of information is needed (codebase, Spotify internal docs/tools, external resources)
     - Which subagent type would be most appropriate to answer it
     - What specific areas or components to investigate
   - Create a research plan using TodoWrite to track all subtasks with **GRANULAR agent-level tracking**:
     - **SPECIFIC AGENT SPAWN TASKS** (e.g., "Spawn codebase-locator for deployment", "Spawn codebase-analyzer for deployment files")
     - For codebase research, create SEPARATE todos for locator and analyzer phases
     - **DO NOT add synthesis task to the TODO list yet** - it will be added in step 4 after all initial agents complete
     - **Pattern for iterative research TODO structure:**
       ```
       Phase 1 Research Tasks:
       - Research question 1 with agent X (pending → in_progress → completed)
       - Research question 2 with agent Y (pending → in_progress → completed)
       - Spawn codebase-locator for question 3 (pending → in_progress → completed)
       [After locator completes in step 4]
       - Spawn codebase-analyzer for question 3 (pending → in_progress → completed)
       [After ALL agents complete in step 4]
       - Synthesis attempt 1 (pending → in_progress → completed)
       - Validation iteration 1 (pending → in_progress → completed)
       [If gaps found in step 6]
       Phase 2 Research Tasks:
       - Additional research for gap 1 (pending → in_progress → completed)
       [After new agents complete]
       - Synthesis attempt 2 (pending → in_progress → completed)
       - Validation iteration 2 (pending → in_progress → completed)
       ```
   - **After listing all sections above, ask the user for confirmation:**

     ```
     Do these look correct?
     - Questions to investigate
     - Research execution plan (dependencies and batching)
     - Assumptions (explicit, implicit, constraints)
     - Success criteria
     - Scope (in/out)
     - Research context (starting points, prior knowledge)

     Should I adjust the questions, sequencing, or any other aspect before proceeding?
     ```

   - **Wait for the user to confirm before proceeding to Step 3.** Do not continue until the user explicitly approves or provides adjustments.

   **Required: Agent Type Accounting**

   @commands/shared/agent-verification-pattern.md

   Create the agent contract listing all agent types needed for the research questions above. This list becomes your contract -- all agent types listed must be spawned before synthesis.

3. **Spawn sub-agent tasks according to the execution plan:**

   **REQUIRED: Pre-Spawn Verification Table**

   @commands/shared/pre-spawn-verification.md
   - **Execute batches in sequence, with parallel spawning within each batch**
   - Follow the execution plan from Step 2, spawning agents batch by batch
   - **For each batch in the execution plan:**
     1. Spawn all agents in that batch in parallel
     2. Wait for all agents in the batch to complete
     3. Extract relevant findings to pass as context to the next batch
     4. Update TODO list to reflect batch completion
     5. Proceed to next batch with enriched context

   - **Passing context between batches:**
     - When spawning agents in Batch N+1, include a "Prior Findings" section in their prompts:

       ```
       ## Prior Findings (from earlier research phases)

       The following information was discovered in earlier research and should inform your investigation:

       - [Key finding 1 from previous batch - e.g., "The video detection lives in search-api/video/"]
       - [Key finding 2 - e.g., "The main entry point is VideoDetectionService.java"]
       - [Specific files/paths discovered]
       - [Terminology/vocabulary learned - e.g., "They call it 'content type resolution' not 'video detection'"]

       Use this context to focus your research more precisely.
       ```

   - **Combining questions**: You MAY combine multiple related questions into a single subagent IF:
     - The questions are closely related and can be answered by the same source/agent type
     - It's more efficient than spawning separate agents
     - **Tell the user which questions you're combining and why**
       Example: "Combining questions 1 & 2 into external-repo-explorer since both involve search-api video detection"
   - **Default subagent choice: spotify-tool-researcher** (since we work at Spotify, most questions involve Spotify-specific context)
   - Create multiple Task agents to research different aspects concurrently
   - Select the most appropriate agent type for each question:

   @commands/shared/subagent-types.md

   **IMPORTANT**: All agents are documentarians, not critics. They will describe what exists without suggesting improvements or identifying issues.
   - When using the **spotify-tool-researcher** or **web-search-researcher** agents, instruct them to return LINKS with their findings, and please INCLUDE those links in your final report
   - If the **thoughts** directory doesn't exist at `~/.claude/thoughts`, create it.

   **For domain-specific research:**

   If the research question involves specific technical domains, consider spawning domain experts:

   @commands/shared/domain-agent-registry.md

   Domain experts provide specialized knowledge that general agents may lack. Spawn them when:
   - The research question explicitly mentions domain technologies
   - Initial codebase research reveals domain-specific patterns
   - You need best practices specific to a domain

   The key is to use these agents intelligently:
   - Start with locator agents to find what exists
   - Then use analyzer agents on the most promising findings to document how they work
   - Run multiple agents in parallel when they're searching for different things
   - Each agent knows its job - just tell it what you're looking for
   - Don't write detailed prompts about HOW to search - the agents already know
   - Remind agents they are documenting, not evaluating or improving

   **Example of question decomposition with dependency analysis:**

   User question: "How do we handle automerge for dependency bot PRs?"

   Questions to answer:
   1. What dependency bots are available at Spotify? → **spotify-tool-researcher**
   2. How does automerge work at Spotify? → **spotify-tool-researcher**
   3. What automerge configurations exist in this repository? → **codebase-locator** then **codebase-analyzer**
   4. What automerge patterns do similar repos use? → **codebase-pattern-finder**
   5. What external tools (Renovate, Dependabot) support automerge? → **web-search-researcher**

   **Dependency Analysis:**

   | Question | Depends On | Rationale                                                              |
   | -------- | ---------- | ---------------------------------------------------------------------- |
   | Q1       | None       | Need to know what bots exist before understanding their configs        |
   | Q2       | None       | General Spotify context, independent                                   |
   | Q3       | Q1         | Knowing which bots exist (Q1) tells us what config files to look for   |
   | Q4       | Q1, Q3     | Need to know our bot (Q1) and our config (Q3) to find similar patterns |
   | Q5       | Q1         | Knowing which bot we use (Q1) focuses external research                |

   **Execution Batches:**

   ```
   Batch 1 (parallel): Q1, Q2
      ↓ Q1 reveals: "We use Renovate"
   Batch 2 (parallel): Q3 (search for renovate.json), Q5 (research Renovate automerge)
      ↓ Q3 reveals: "Config at .github/renovate.json5 with automerge disabled"
   Batch 3: Q4 (find repos using Renovate with automerge enabled)
   ```

   **Context passed:**
   - Batch 1 → Batch 2: "We use Renovate bot, search for renovate config files"
   - Batch 2 → Batch 3: "Our config is at .github/renovate.json5, look for similar repos with automerge: true"

4. **Checkpoint - Wait for current batch and spawn next batch if needed:**
   - **Required**: Wait for all agents in the current batch to return results before proceeding
   - Verify you have results from every agent you spawned
   - If any agent failed or returned no output, re-spawn with adjusted prompt
   - Update TODO list: mark completed batch agent tasks as "completed"
   - **Extract context for next batch**: Before spawning the next batch, identify key findings that should inform subsequent agents
   - **Adjusting the plan mid-execution**: If a batch reveals that planned dependencies were unnecessary, you may promote later-batch questions to run sooner. Document any plan adjustments for the user.

   **Step 4 Validation Checklist (show to user):**

   Before proceeding to synthesis, verify ALL of the following and show this checklist to the user:

   ```
   ## Step 4 Validation Checklist

   Reviewing agent commitments from Step 2 against actual agents spawned:

   □ For each question in Step 2 that mentioned "codebase-locator THEN codebase-analyzer":
     - Did locator find files? If YES → codebase-analyzer is REQUIRED (spawn in Batch 2)
     - Have I spawned or planned the analyzer agent? If NO → STOP and add it now

   □ For each question that mentioned "codebase-pattern-finder":
     - Have I spawned the pattern-finder agent? If NO → STOP and spawn it now

   □ For each question that mentioned other Batch 2 agents (thoughts-analyzer, etc.):
     - Have I spawned all mentioned agents? If NO → STOP and spawn them now

   □ Cross-check against Agent Type Verification from Step 2:
     - All agent types listed there must be spawned before synthesis
     - Count: [X agent types listed, Y agent types spawned]
     - If X ≠ Y: STOP and spawn missing agents

   **If any checkbox is unchecked, return and complete missing items before synthesis.**
   ```

   **Batch 2 Spawning Decision (Codebase-Analyzer Agents):**

   If you mentioned "codebase-locator THEN codebase-analyzer" in Step 2, apply this decision tree:

   **RULE 1: If locator found files → analyzer is DEFAULT REQUIRED**
   - The fact that locator provided code snippets does NOT eliminate the need for analyzer
   - Locator's job: Find WHERE files are
   - Analyzer's job: Explain HOW the code works (architecture, data flow, patterns)
   - These are DIFFERENT objectives

   **RULE 2: Analyzer can ONLY be skipped if BOTH conditions are true:**
   1. Locator output already includes comprehensive HOW analysis (not just code listings)
   2. You explicitly tell the user you're skipping it and why

   **Transparency requirement**:
   - If skipping analyzer, tell the user before proceeding:
     ```
     "The codebase-locator output for [question] provides sufficient HOW analysis to answer
     the question without needing a separate codebase-analyzer agent. The locator explained
     [brief summary of what was explained]. I will skip the analyzer agent for this question."
     ```
   - If spawning analyzer: Add new TODO items and mark as "pending"

   **DEFAULT ACTION: When in doubt, spawn the analyzer. Over-researching is better than under-researching.**

   **Spawn Batch 2 (codebase-analyzer agents):**
   - Based on the decision tree above, spawn analyzer agents as needed
   - Mark these new tasks as "in_progress" in the TODO list
   - Wait for Batch 2 agents to complete
   - Mark Batch 2 tasks as "completed" when done

   **ONLY AFTER all research agents complete (Batch 1 + Batch 2):**
   - Add "Synthesize findings from all sub-agents" task to TODO list
   - Mark synthesis task as "pending" (NOT in_progress yet)
   - Add "Validate research completeness (iteration 1)" task as "pending"
   - Proceed to step 5

5. **Synthesize findings from all sub-agents:**

   **Pre-synthesis verification:**

   Run Phase 3 from `commands/shared/agent-verification-pattern.md` to verify all contracted agents were spawned before proceeding.

   **BLOCKER RULES:**
   - Count: Agent types mentioned in Step 2 = Agent types actually spawned
   - If counts don't match: STOP immediately, identify missing agents, spawn them
   - Do NOT proceed to synthesis with incomplete research

   - **Start synthesis only when all agents from the current research phase are complete**
   - **Avoid synthesizing partial results if you plan to spawn more agents**
   - All agent tasks in TODO list should be "completed" before synthesis starts
   - Mark synthesis task as "in_progress" in TODO list now
   - Compile all sub-agent results (codebase, thoughts and external documentation findings)
   - Prioritize live codebase and latest documentation findings as primary source of truth
   - Use ~/.claude/thoughts/ findings as supplementary historical context
   - Connect findings across different components
   - Include specific file paths and line numbers for reference
   - Verify all ~/.claude/thoughts/ paths are correct (e.g., ~/.claude/thoughts/$USER/ not ~/.claude/thoughts/shared/ for personal files)
   - Highlight patterns, connections, and architectural decisions
   - Answer the user's specific questions with concrete evidence
   - Mark synthesis task as "completed" in TODO list after synthesis is done
   - Proceed to step 6 only after synthesis is marked completed

6. **Reflect and validate research completeness (ITERATIVE LOOP):**
   - **This step should be visible to the user**
   - **Output a "Research Completeness Review" section that shows your analysis**
   - Mark validation task as "in_progress" in TODO list
   - Review the questions identified in step 2 against the synthesized findings from step 5

   **Output this section for the user to see:**

   ```
   ## Research Completeness Review (Iteration N of 2)

   Reviewing whether all questions from Step 2 have been adequately answered:

   ✅ Question 1: [Question text]
      Status: ADEQUATELY ANSWERED / NEEDS MORE INFO
      Evidence: [Brief summary of what was found OR what's missing]

   ✅ Question 2: [Question text]
      Status: ADEQUATELY ANSWERED / NEEDS MORE INFO
      Evidence: [Brief summary of what was found OR what's missing]

   ... (for each question)

   **Decision:**
   - [ ] All questions adequately answered → Proceeding to Step 7 (metadata gathering)
   - [ ] Missing information detected → Will spawn additional subagents and repeat Steps 3-6

   **If missing information:**
   Missing information needed:
   1. [Specific gap identified]
   2. [Specific gap identified]

   Additional subagents to spawn:
   1. [subagent-type] to answer: [specific question about the gap]
   2. [subagent-type] to answer: [specific question about the gap]
   ```

   - For EACH question from step 2, evaluate:
     - Do the subagent findings provide sufficient information to answer this question?
     - Are there gaps, ambiguities, or missing details?
     - Would the user be satisfied with the answer based on current information?

   - **If ALL questions are adequately answered:**
     - Mark validation task as "completed" in TODO list
     - Proceed to step 7 (metadata gathering)

   - **If ANY questions are inadequately answered:**
     - Mark validation task as "completed" in TODO list
     - **Update TODO list before spawning new agents:**
       - Remove or mark synthesis task as "needs revision" (DO NOT leave it as "completed")
       - Add new agent spawn tasks with status "pending"
       - Add new synthesis task with status "pending" (for next iteration)
       - Add new validation task with status "pending" (for next iteration)
     - Identify exactly what information is still missing
     - Determine which additional subagents need to be spawned to fill the gaps
     - **RETURN TO STEP 3**: Spawn new targeted subagents to gather missing information
     - **RETURN TO STEP 4**: Wait for new agents to complete
     - **RETURN TO STEP 5**: RE-SYNTHESIZE with ALL findings (old + new)
     - **RETURN TO STEP 6**: Validate again with new iteration number

   - **Maximum 2 iterations**: After completing the steps 3→4→5→6 loop twice total, proceed to step 7 even if some gaps remain (document them as "Open Questions")
   - **Only proceed to step 7 when:**
     - All questions from step 2 are adequately answered, OR
     - You have completed 2 iterations of the research loop
   - Track iteration count and display it in the "Research Completeness Review" header

7. **Gather metadata for the research document:**
   - Run the following script to generate metadata:

     ```bash
     #!/usr/bin/env bash
     set -euo pipefail

     # Collect metadata
     DATETIME_TZ=$(date '+%Y-%m-%d %H:%M:%S %Z')
     FILENAME_TS=$(date '+%Y-%m-%d_%H-%M-%S')

     if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
     REPO_ROOT=$(git rev-parse --show-toplevel)
     REPO_NAME=$(basename "$REPO_ROOT")
     GIT_BRANCH=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)
     GIT_COMMIT=$(git rev-parse HEAD)
     else
     REPO_ROOT=""
     REPO_NAME=""
     GIT_BRANCH=""
     GIT_COMMIT=""
     fi

     # Print similar to the individual command outputs
     echo "Current Date/Time (TZ): $DATETIME_TZ"
     [ -n "$GIT_COMMIT" ] && echo "Current Git Commit Hash: $GIT_COMMIT"
     [ -n "$GIT_BRANCH" ] && echo "Current Branch Name: $GIT_BRANCH"
     [ -n "$REPO_NAME" ] && echo "Repository Name: $REPO_NAME"
     echo "Timestamp For Filename: $FILENAME_TS"
     ```

   - Create the `~/.claude/thoughts/shared/research/` directory if it doesn't exist
   - Filename: `~/.claude/thoughts/shared/research/YYYY-MM-DD-ENG-XXXX-description.md`
     - Format: `YYYY-MM-DD-ENG-XXXX-description.md` where:
       - YYYY-MM-DD is today's date
       - ENG-XXXX is the ticket number (omit if no ticket)
       - description is a brief kebab-case description of the research topic
     - Examples:
       - With ticket: `2025-01-08-ENG-1478-parent-child-tracking.md`
       - Without ticket: `2025-01-08-authentication-flow.md`

8. **Generate research document:**
   - Use the metadata gathered in step 7
   - Structure the document with YAML frontmatter followed by content sections, using the research report template:

     @commands/shared/research-report-template.md

9. **Add GitHub permalinks (if applicable):**
   - Check if on main branch or if commit is pushed: `git branch --show-current` and `git status`
   - If on main/master or pushed, generate GitHub permalinks:
     - Get repo info: `gh repo view --json owner,name`
     - Create permalinks: `https://github.com/{owner}/{repo}/blob/{commit}/{file}#L{line}`
   - Replace local file references with permalinks in the document

10. **Include mcp calls so the findings can be reproduced**

- The output of the spotify tool researcher may contain information from Spotify sources via mcp calls
- Include the relevant information from the **Additional Resources**:
  - query, source and description from an aika mcp search
  - query, repository name and description from a codesearch mcp search
  - links and description of relevant webpages

11. **Sync and present findings:**

- Write the output to the `~/.claude/thoughts` directory (it should already exist from an earlier step)
- Present a concise summary of findings to the user
- Include key file references for easy navigation
- After creating the plan file, ask the user: "Would you like to ask follow-up questions or do you need any clarifications?"

12. **Handle follow-up questions:**

- If the user has follow-up questions, append to the same research document
- Update the frontmatter fields `last_updated` and `last_updated_by` to reflect the update
- Add `last_updated_note: "Added follow-up research for [brief description]"` to frontmatter
- Add a new section: `## Follow-up Research [timestamp]`
- Spawn new sub-agents as needed for additional investigation
- Continue updating the document and syncing

## Iteration Loop Structure

This section clarifies how the iterative research loop works across steps 3, 4, 5, and 6.

**Initial research phase (Iteration 0):**

1. Step 2: Identify questions and create initial TODO list
2. Step 3: Spawn Batch 1 agents (mark as "in_progress")
3. Step 4: WAIT for Batch 1 to complete (mark as "completed"), spawn Batch 2 if needed, wait for completion
4. Step 4: Add synthesis and validation tasks to TODO list (both "pending")
5. Step 5: Mark synthesis as "in_progress", synthesize findings, mark as "completed"
6. Step 6: Mark validation as "in_progress", validate completeness

**If all questions adequately answered (Iteration 0 success):**

1. Step 6: Mark validation as "completed"
2. Step 7: Proceed to metadata gathering

**If gaps found (Iteration N, where N = 1 or 2):**

1. Step 6: Mark validation as "completed"
2. Step 6: **Update TODO list:**
   - Mark or remove previous synthesis task (it needs revision with new data)
   - Add new agent spawn tasks (status: "pending")
   - Add new synthesis task for iteration N (status: "pending")
   - Add new validation task for iteration N (status: "pending")
3. Step 3 (repeat): Spawn new agents to fill gaps (mark as "in_progress")
4. Step 4 (repeat): WAIT for new agents to complete (mark as "completed")
5. Step 5 (repeat): Mark synthesis iteration N as "in_progress", RE-SYNTHESIZE with ALL findings (old + new), mark as "completed"
6. Step 6 (repeat): Mark validation iteration N as "in_progress", validate again
7. If still gaps and N < 2: Repeat from step 3
8. If N = 2 or all questions answered: Proceed to step 7

**Critical rules:**

- Synthesis can ONLY start when ALL current-phase agents are completed
- Validation can ONLY start when synthesis is completed
- New agents can ONLY spawn after validation identifies gaps
- Maximum 2 iterations total (iteration 0, 1)

## State Machine for Research Flow

Visual representation of the research process state transitions:

```
┌─────────────────────────┐
│ Questions Identified    │
│ (Step 2)                │
└────────────┬────────────┘
             │
             │ Create TODO: agents as "pending"
             │ DO NOT add synthesis yet
             v
┌─────────────────────────┐
│ Spawn Agents (Step 3)   │◄────────────────┐
│ Mark agents "in_progress"│                 │
└────────────┬────────────┘                  │
             │                                │
             v                                │
┌─────────────────────────┐                  │
│ All Agents Complete?    │                  │
│ (Step 4 Checkpoint)     │                  │
└────────────┬────────────┘                  │
             │ No: wait                       │
             │ Yes: mark "completed"          │
             v                                │
┌─────────────────────────┐                  │
│ Need Batch 2 Analyzers? │                  │
│ (Step 4)                │                  │
└────────────┬────────────┘                  │
             │                                │
         Yes │  No                            │
             │                                │
      ┌──────┴────────┐                      │
      │               │                      │
      v               v                      │
┌───────────┐  ┌─────────────────────────┐  │
│Spawn      │  │Add synthesis to TODO    │  │
│Batch 2    │  │Mark "pending"           │  │
│Wait       │  └────────────┬────────────┘  │
└─────┬─────┘               │                │
      │                     │                │
      └──────────┬──────────┘                │
                 │                            │
                 v                            │
┌─────────────────────────┐                  │
│ Mark Synthesis          │                  │
│ "in_progress" (Step 5)  │                  │
└────────────┬────────────┘                  │
             │                                │
             v                                │
┌─────────────────────────┐                  │
│ Synthesize Results      │                  │
│ (Step 5)                │                  │
└────────────┬────────────┘                  │
             │                                │
             │ Mark "completed"               │
             v                                │
┌─────────────────────────┐                  │
│ Mark Validation         │                  │
│ "in_progress" (Step 6)  │                  │
└────────────┬────────────┘                  │
             │                                │
             v                                │
┌─────────────────────────┐                  │
│ Validate Completeness   │                  │
│ (Step 6)                │                  │
└────────────┬────────────┘                  │
             │                                │
             v                                │
      ┌──────┴──────┐                        │
      │  Complete?  │                        │
      └──────┬──────┘                        │
             │                                │
        Yes  │  No: Gaps found                │
             │  AND iteration < 2             │
             │                                │
      ┌──────┴────────┐                      │
      │               │                      │
      v               v                      │
┌───────────┐  ┌─────────────────────────┐  │
│Generate   │  │Update TODO:             │  │
│Document   │  │- Mark validation done   │  │
│(Step 7)   │  │- Remove/revise synthesis│  │
│           │  │- Add new agent tasks    │  │
│           │  │- Add new synthesis task │  │
│           │  │- Add new validation task│──┘
│           │  │Mark new agents "pending"│
└───────────┘  └─────────────────────────┘
                Increment iteration N
                RETURN to "Spawn Agents"
```

**Key State Transitions:**

- `pending` → `in_progress` → `completed` for each task
- Synthesis stays `pending` until ALL agents are `completed`
- If gaps found, new iteration creates new pending tasks
- Synthesis is NOT marked `completed` if gaps require more research

## Important notes:

- **Execution plan**: Follow the sequenced execution plan from Step 2; run independent questions in parallel but sequence dependent questions to pass context forward
- **Parallelism vs sequencing**: Default to parallelism when dependency is unclear; only sequence when earlier answers clearly improve later queries
- Always run fresh research - never rely solely on existing research documents
- The ~/.claude/thoughts/ directory provides historical context to supplement live findings
- Focus on finding concrete file paths and line numbers for developer reference
- Research documents should be self-contained with all necessary context
- Each sub-agent prompt should be specific and focused on read-only documentation operations
- Document cross-component connections and how systems interact
- Include temporal context (when the research was conducted)
- Link to GitHub when possible for permanent references
- Keep the main agent focused on synthesis, not deep file reading
- Have sub-agents document examples and usage patterns as they exist
- Explore all of ~/.claude/thoughts/ directory, not just research subdirectory
- You and all sub-agents are documentarians, not evaluators
- Continue the clarification loop in Step 12 until the user explicitly confirms the research is complete
- Document what IS, not what SHOULD BE
- Focus on describing the current state of the codebase and/or the tool/library rather than making recommendations
- **File reading**: Always read mentioned files FULLY (no limit/offset) before spawning sub-tasks (unless otherwise instructed)
- **Ordering**: Follow the numbered steps in sequence
  - Read mentioned files first before spawning sub-tasks (step 1)
  - Wait for all sub-agents to complete before synthesizing (step 5)
  - Validate research completeness before proceeding (step 6 - may loop back to step 3)
  - Gather metadata before writing the document (step 7 before step 8)
  - Write the research document with actual values, not placeholders
- **Path handling**:
  - Preserve the exact directory structure within ~/.claude/thoughts/ (e.g., keep jbrooksbartlett/ as jbrooksbartlett/, not shared/)
  - This ensures paths are correct for editing and navigation
- **Frontmatter consistency**:
  - Always include frontmatter at the beginning of research documents
  - Keep frontmatter fields consistent across all research documents
  - Update frontmatter when adding follow-up research
  - Use snake_case for multi-word field names (e.g., `last_updated`, `git_commit`)
  - Tags should be relevant to the research topic and components studied
