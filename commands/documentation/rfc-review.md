---
description: Comprehensive RFC review using specialized subagents with context gathering, technical analysis, and synthesis
argument-hint: [google-doc-url-or-file-path]
---

# RFC Review

Conduct a comprehensive review of an RFC (Request for Comments) by gathering context, researching domain-specific terminology, running specialized review subagents in parallel, and generating a structured review report.

**IMPORTANT**: This is a review command. DO NOT modify the RFC. Only provide constructive, actionable analysis and recommendations.

## Workflow Overview

```
Step 1: Get RFC Input & Read Fully
   ↓
Step 2: Summarize Linked Documents ← BLOCKING
   └─ linked-document-summarizer (all document types)
   ↓
Step 3: Extract Terms/Systems for Research
   ↓
Step 4: Spawn Context-Gathering Agents ← BLOCKING
   ├─ spotify-tool-researcher (Spotify terms)
   ├─ web-search-researcher (external concepts)
   └─ repo-discovery (systems mentioned in RFC)
   ↓
Step 5: Spawn Codebase Exploration Agents (if repos discovered) ← BLOCKING
   ├─ codebase-locator (for local repos)
   └─ external-repo-explorer (for external repos)
   ↓
Step 6: Spawn Review Agents ← BLOCKING
   ├─ rfc-reviewer
   ├─ gemini-rfc-reviewer
   └─ visual-aid-recommender (generates diagram CODE)
   ↓
Step 7: Synthesize All Findings
   ↓
Step 8: Generate Review Report
   ↓
Step 9: Present Review to User
```

## Instructions

### 1. Get RFC Input & Read Fully

**Arguments**:

- `[google-doc-url-or-file-path]` (required): The RFC to review
- `--skip-linked-docs` (optional): Skip summarization of linked documents

**Determine the RFC source**:

- If the user provided a Google Doc URL, extract the document ID and read using the google-drive MCP tool
- If the user provided a file path, read the file directly
- If no argument provided, ask the user: "Please provide the RFC to review (Google Doc URL or file path)"

**Read the RFC completely**:

- **CRITICAL**: Read the ENTIRE RFC into main context before proceeding
- For Google Docs: Use `mcp__google-drive-mcp__get_document_structure` first, then read ALL sections using `mcp__google-drive-mcp__get_document_section` with `includeSubsections: true`
- For local files: Use the Read tool WITHOUT limit/offset parameters
- Do NOT proceed until you have the complete RFC content

**Identify linked documents**:

- As you read the RFC, note any linked documents (Google Docs, Jira tickets, Slack threads, etc.)
- These will be processed in Step 2 unless `--skip-linked-docs` was specified

---

### 2. Summarize Linked Documents

**This step runs by DEFAULT.** To skip, the user must explicitly pass `--skip-linked-docs` or state "skip linked documents" in their prompt.

> **CRITICAL**: Do NOT read linked documents into the main agent context. Only identify them (note URLs and titles from link text), then delegate ALL reading to the linked-document-summarizer subagent. The only exception is if the user explicitly pastes document content in their prompt.

> **CRITICAL**: Do NOT pre-filter documents by type. Send ALL linked documents (Google Docs, Slack threads, Jira tickets, etc.) to the linked-document-summarizer subagent. The subagent has tools to handle each document type and will report success/failure for each. Never assume a document type cannot be accessed - let the subagent try and report.

**Identify linked documents** (without reading them):

- Parse the RFC for URLs and references to external documents:
  - Google Docs URLs (docs.google.com)
  - Jira ticket references (e.g., SEARCH-1234, ENG-5678)
  - Confluence URLs
  - Slack thread links
  - GitHub URLs
  - Other markdown file references
- Output for user visibility:

  ```
  ## Linked Documents Identified

  Found [N] linked documents:

  1. [Doc title/ID]: [URL] (Google Doc)
  2. [Doc title/ID]: [URL] (Jira)
  3. [Doc title/ID]: [URL] (Slack)
  ...
  ```

**Check document count**:

- If more than 10 linked documents are found, ask user to prioritize:

  ```
  ## Many Linked Documents Found

  Found [N] linked documents, which exceeds the recommended limit of 10.

  Processing all documents may take significant time. Please choose:
  1. Process all [N] documents
  2. Select specific documents to process (list numbers)
  3. Skip linked document summarization entirely

  Which option would you prefer?
  ```

- Wait for user response before proceeding.

**Spawn linked-document-summarizer subagent** (BLOCKING):

Prompt template:

```
Summarize the following linked documents to provide context for reviewing an RFC.

## RFC Topic
{{RFC_TITLE}}

## RFC Summary
{{BRIEF_RFC_DESCRIPTION - 2-3 sentences about what the RFC proposes}}

## Documents to Summarize

{{LIST_OF_LINKED_DOCUMENTS_WITH_URLS}}

## Instructions

1. Process ONLY the documents listed above - do NOT follow links within those documents
2. **ATTEMPT ALL DOCUMENT TYPES**: Try to access every document regardless of type (Google Docs, Slack, Jira, etc.). Use the appropriate tool for each:
   - Google Docs/Sheets/Slides: Use Google Drive MCP tools
   - Slack threads: Use `internal_search` with data_source="slack" (search for key terms/context from the thread)
   - Jira tickets: Use `list_tickets` or `search_issues_advanced` with the ticket key
   - Web URLs: Use WebFetch
3. **SIZE CHECK (MANDATORY for Google Drive docs)**: Before reading ANY Google Doc/Sheet/Slides:
   - Use `mcp__google-drive-mcp__get_drive_file_metadata` to get the document size
   - Under 50KB: Read fully | 50-200KB: Section-based | 200-500KB: Key sections only | Over 500KB: Skip
   - Report your size decision for each document
4. **RETRY ON ERRORS**: If a tool call fails, retry at least once before marking as failed (errors may be transient)
5. **CONTINUE ON FAILURE**: If you cannot access a document after retrying, log the error and continue with other documents - do NOT stop entirely
6. **REPORT ALL STATUSES**: In your final output, clearly report the status of EVERY document requested:
   - Successfully processed: Include summary
   - Failed to access: Include error type and what context might be missing
   - Skipped (too large): Include size and reason
7. Provide more detailed summaries for documents that appear more relevant to the RFC
8. Focus on decisions, trade-offs, constraints, and technical specifications

This is READ-ONLY research - do not create or modify any files.
```

**Handle errors**:

- The subagent will continue processing all documents even if some fail, and report failures at the end
- If the subagent reports failed documents in its output:
  - Review the "Failed Documents" section to understand what context may be missing
  - Display a summary to the user:

    ```
    ## Linked Document Summary Complete

    **Successfully processed**: [N] documents
    **Failed to access**: [N] documents (see details below)
    **Skipped (too large)**: [N] documents

    ### Failed Documents:
    - [Document 1]: [Error type] - [Brief impact on review]
    ...

    These failures are noted in the review report. Proceed with available context? (y/n)
    ```

  - If user wants to retry specific documents, re-run the subagent with just those documents

- Only prompt user to intervene if ALL documents failed to process

**CHECKPOINT: Before proceeding to Step 3, verify:**

- [ ] linked-document-summarizer has completed successfully (or user chose to skip)
- [ ] Summary has been captured for inclusion in review agent prompts
- [ ] Any errors have been resolved or acknowledged by user

**Pass summaries to downstream agents**:

- Include the linked document summaries in the context for:
  - Step 4: spotify-tool-researcher, web-search-researcher, repo-discovery
  - Step 5: codebase-locator, external-repo-explorer
  - Step 6: rfc-reviewer, gemini-rfc-reviewer
- Add to each agent's prompt:

  ```
  ## Context from Linked Documents

  The following context was gathered from documents linked in the RFC:

  {{LINKED_DOCUMENT_SUMMARY}}
  ```

---

### 3. Extract Terms/Systems for Research

After reading the RFC, analyze its content to identify:

**a. Spotify-specific terms** that need research:

- Look for Spotify tools/systems mentioned (e.g., Gabito, Decibel, Apollo, Scio, BigTable, MMA, Hermes, etc.)
- Look for Spotify product names (e.g., iDJ, Promptable Playlists, GenRecs, etc.)
- Look for internal services or frameworks

**b. External concepts** that may need research:

- Third-party APIs or services mentioned
- Industry standards or protocols
- Technical concepts that require external documentation

**c. Systems/services** mentioned that may need codebase exploration:

- Existing systems/services the RFC mentions or depends on
- Services the proposed solution will interact with or extend
- Systems whose architecture or patterns need to be understood

> **NOTE**: Do NOT try to find repositories yourself in the main agent. Just identify system NAMES and brief descriptions. The `repo-discovery` agent will find the actual repository locations.

**d. Output the extraction** for the user to see:

```
## Terms and Systems Identified for Research

### Spotify-Specific Terms
- [Term 1]: [Brief description of why it needs research]
- [Term 2]: [Brief description of why it needs research]
...

### External Concepts
- [Concept 1]: [Why it needs research]
...

### Systems to Explore (repo-discovery will find locations)
- [System 1]: [Brief description of what it does] - [What we need to understand about it]
- [System 2]: [Brief description of what it does] - [What we need to understand about it]
...

### Linked Documents Noted (Not Read)
- [Document 1]: [Google Doc URL or file path] - [Brief description of what it appears to contain]
...
*Note: These documents were not read. Context completeness will be assessed in the review.*
```

**e. Detect technical domains for specialized review:**

Scan the RFC content for domain-specific patterns:

@commands/shared/domain-agent-registry.md

Store detected domains for use in Step 6.

**Required: Agent Type Verification**

@commands/shared/agent-verification-pattern.md

Create the agent contract listing all standard review agents (rfc-reviewer, gemini-rfc-reviewer, visual-aid-recommender) plus any domain-based agents detected above. This contract governs Step 6.

---

### 4. Spawn Context-Gathering Agents

⚠️ **BLOCKING STEP - DO NOT PROCEED TO STEP 5 UNTIL THIS IS COMPLETE**

Launch the following agents **IN PARALLEL** using a single message with multiple Task tool calls:

#### 4a. Spotify-Tool-Researcher (ALWAYS spawn if Spotify terms found)

Prompt template:

```
Research the following Spotify-specific tools, systems, and concepts that appear in an RFC. For each term, provide:
- What it is / what it does
- How it's used at Spotify
- Key features and capabilities
- Any relevant documentation links
- Relevant Slack channels for support

Terms to research:
{{LIST_OF_SPOTIFY_TERMS}}

## Context from Linked Documents
{{LINKED_DOCUMENT_SUMMARY}}

This research will be used to build a Glossary section in an RFC review report. Include links/citations for each term found.

This is READ-ONLY research - do not create or modify any files.
```

#### 4b. Web-Search-Researcher (if external concepts found)

Prompt template:

```
Research the following external concepts, technologies, or standards mentioned in an RFC. For each, provide:
- What it is and how it works
- Industry best practices
- Relevant documentation links
- Any known limitations or considerations

Concepts to research:
{{LIST_OF_EXTERNAL_CONCEPTS}}

## Context from Linked Documents
{{LINKED_DOCUMENT_SUMMARY}}

This research will be used to build a Glossary section in an RFC review report. Include links/citations for each concept found.

This is READ-ONLY research - do not create or modify any files.
```

#### 4c. Repo-Discovery (ALWAYS spawn if systems/services mentioned)

**Purpose**: Find repository locations for systems mentioned in the RFC. This agent handles the token-heavy work of searching local directories and code search, returning a structured mapping of systems to repositories.

**When to spawn**: Whenever the RFC mentions existing systems, services, or codebases that:

- The proposal will interact with
- The proposal extends or modifies
- Are dependencies of the proposed solution
- Need to be understood to evaluate the RFC

Prompt template:

```
Discover repositories for the following systems mentioned in an RFC.

## RFC Context
Title: {{RFC_TITLE}}
Summary: {{BRIEF_RFC_DESCRIPTION}}

## Systems to Find

{{FOR_EACH_SYSTEM}}
- **{{SYSTEM_NAME}}**: {{BRIEF_DESCRIPTION}} - Need to understand: {{WHAT_TO_UNDERSTAND}}
{{END_FOR}}

## Local Repository Root
Repositories may be located anywhere under `~/spotify/`. The directory structure is typically:
`~/spotify/<team-or-domain>/<repo-name>/`

Examples:
- "Search Brain" is at `~/spotify/search-platform/search-brain`
- "Stormlight" might be at `~/spotify/user-data/stormlight`

## Instructions
1. For each system, search for its repository location
2. Try local discovery first (under ~/spotify/)
3. If not found locally, use code-search to find the repo
4. Return structured results with confidence levels
5. Recommend which exploration agent to use for each repo (codebase-locator for local, external-repo-explorer for external)

This is READ-ONLY research - do not create or modify any files.
```

---

**📋 CHECKPOINT: Before proceeding to Step 5 (Exploration), verify:**

- [ ] spotify-tool-researcher has completed (if spawned)
- [ ] web-search-researcher has completed (if spawned)
- [ ] repo-discovery has completed (if spawned)
- [ ] All findings have been captured

---

### 5. Spawn Codebase Exploration Agents (if repos discovered)

**This step only runs if repo-discovery found repositories to explore.**

**Check repository count**: If repo-discovery found more than 5 repositories, you MUST stop and ask the user to prioritize:

```
## Many Repositories Identified

Found [N] repositories to explore, which exceeds the limit of 5.

Repositories found:
1. [System 1] - [Repo path] (Local/External) - [What to understand]
2. [System 2] - [Repo path] (Local/External) - [What to understand]
3. [System 3] - [Repo path] (Local/External) - [What to understand]
4. [System 4] - [Repo path] (Local/External) - [What to understand]
5. [System 5] - [Repo path] (Local/External) - [What to understand]
6. [System 6] - [Repo path] (Local/External) - [What to understand]
...

Please select up to 5 repositories to explore (comma-separated numbers), or type 'all' to explore all [N] repositories, or type 'skip' to proceed without codebase exploration:
```

**IMPORTANT**: You MUST wait for user response before proceeding. Do NOT silently select a subset of repositories.

**For each repository to explore, spawn the appropriate agent IN PARALLEL:**

#### For LOCAL repositories (path starts with `~/spotify/`):

Spawn **codebase-locator**:

```
Locate files and components in {{REPO_PATH}} that are relevant to understanding:
{{WHAT_TO_UNDERSTAND_ABOUT_THE_SYSTEM}}

Focus on:
- Main entry points and service definitions
- Key data models and schemas
- Integration points with other services
- Configuration patterns
- How {{SPECIFIC_FUNCTIONALITY_FROM_RFC}} is implemented

This is READ-ONLY research - do not create or modify any files.
```

#### For EXTERNAL repositories (found via code-search, not local):

Spawn **external-repo-explorer**:

```
Clone and explore the repository {{REPO_URL}} to understand:
{{WHAT_TO_UNDERSTAND_ABOUT_THE_SYSTEM}}

Focus on:
- Architecture and main components
- How the system handles {{RELEVANT_FUNCTIONALITY}}
- Integration patterns
- Configuration and deployment approach
- Key APIs or interfaces that the RFC's proposal would use

This is READ-ONLY research - do not create or modify any files.
```

---

**📋 CHECKPOINT: Before proceeding to Step 6, verify:**

- [ ] All selected repositories have been explored (or user skipped exploration)
- [ ] Exploration findings have been captured for use in Step 6 prompts
- [ ] Any repos not explored are documented with reason (user skipped, not found, etc.)

**If codebase-locator found relevant files and deeper analysis is needed, optionally spawn codebase-analyzer:**

```
Analyze the following files/components in {{REPO_PATH}} to understand:
{{WHAT_TO_UNDERSTAND}}

Files to analyze:
{{LIST_OF_FILES_FROM_LOCATOR}}

Explain:
- How the code works (architecture, data flow, patterns)
- How it relates to the RFC's proposed changes
- Any patterns that should be followed or avoided

This is READ-ONLY research - do not create or modify any files.
```

Wait for all exploration agents to complete before proceeding to Step 6.

---

### 6. Spawn Review Agents

⚠️ **BLOCKING STEP - DO NOT PROCEED TO STEP 7 UNTIL THIS IS COMPLETE**

**REQUIRED: Pre-Spawn Verification**

Before spawning, output verification table matching contract from Step 3. If skipping any agent, provide reason and inform user.

@commands/shared/pre-spawn-verification.md

Launch the following agents **IN PARALLEL** using a single message with multiple Task tool calls:

#### 6a. RFC-Reviewer

Prompt template:

```
Review the following RFC for technical merit, problem-solution fit, assumptions, and evidence.

## RFC Content
{{RFC_CONTENT_OR_SUMMARY}}

## Context from Research
The following context was gathered to help understand the RFC:

### Spotify Systems/Tools Context
{{SPOTIFY_TOOL_RESEARCH_FINDINGS}}

### External Concepts Context
{{EXTERNAL_RESEARCH_FINDINGS}}

### Codebase Context
{{CODEBASE_ANALYSIS_FINDINGS}}

### Linked Documents Context
{{LINKED_DOCUMENT_SUMMARY}}

## Review Focus
Focus SOLELY on technical soundness, NOT on presentation or formatting:
1. Problem-Solution Fit: Does the solution address the stated problem?
2. Technical Soundness: Is the proposed approach technically feasible?
3. Implicit Assumptions: What assumptions are being made? Are they valid?
4. Evidence: Is the proposal backed by sufficient evidence?
5. Risks: Are risks adequately identified and mitigated?
6. Alternatives: Were reasonable alternatives considered?
7. Impact: What is the impact on existing systems?

Provide specific, actionable feedback with references to specific sections of the RFC.
```

#### 6b. Gemini-RFC-Reviewer

Prompt template:

```
Use the gemini-rfc-reviewer agent to analyze the RFC and provide a technical review using Google's Gemini model.

## RFC Content
{{RFC_CONTENT_OR_SUMMARY}}

## Context from Research
### Spotify Systems/Tools Context
{{SPOTIFY_TOOL_RESEARCH_FINDINGS}}

### External Concepts Context
{{EXTERNAL_RESEARCH_FINDINGS}}

### Codebase Context
{{CODEBASE_ANALYSIS_FINDINGS}}

### Linked Documents Context
{{LINKED_DOCUMENT_SUMMARY}}

## Review Focus
Evaluate technical soundness, problem-solution fit, assumptions, evidence, and logic.
Focus on what could go wrong and what's missing from the proposal.
```

#### 6c. Visual-Aid-Recommender

Prompt template:

```
Analyze the RFC and create visual aids that would help readers understand the core concepts.

## RFC Content
{{RFC_CONTENT_OR_SUMMARY}}

## Instructions
For this RFC, identify 2-4 key concepts that would benefit from visualization, then CREATE the actual diagrams.

Focus on:
1. Complex flows or processes (use sequence diagrams or flowcharts)
2. System architectures (use architecture diagrams)
3. Data flows or state transitions (use state diagrams or data flow diagrams)
4. Decision logic or caching strategies (use flowcharts)

For EACH diagram you create:
1. **Title**: A descriptive name for the diagram
2. **Purpose**: What concept this helps explain (1 sentence)
3. **Diagram Type**: flowchart, sequence, architecture, state, etc.
4. **Tool**: Use Mermaid (preferred) or PlantUML
5. **Code**: The COMPLETE, VALID diagram code that can be rendered

## Output Format
Return your diagrams in this exact format:

### Diagram 1: [Title]
**Purpose**: [What this diagram explains]
**Type**: [Diagram type]
**Tool**: Mermaid

\`\`\`mermaid
[Complete Mermaid code here]
\`\`\`

### Diagram 2: [Title]
...

## Diagram Best Practices
- Keep diagrams simple and focused (max 10-15 nodes)
- Use clear, descriptive labels
- Show the happy path prominently
- Include error/edge cases where important
- Use consistent styling within each diagram
- Make diagrams self-explanatory (reader shouldn't need to read surrounding text)
```

#### 6d. Domain Expert Reviewers (spawn if detected in Step 3)

For each domain detected in Step 3, spawn the corresponding expert agent **IN PARALLEL** with the standard reviewers:

**Prompt template for domain experts:**

```
Review the [DOMAIN] aspects of this RFC.

## RFC Content
{{RFC_CONTENT_OR_SUMMARY}}

## Context from Research
{{RESEARCH_FINDINGS}}

## Review Focus
- Evaluate alignment with Spotify [DOMAIN] best practices
- Identify potential issues or anti-patterns specific to [DOMAIN]
- Suggest improvements based on [DOMAIN] expertise
- Check for missing considerations typical in [DOMAIN] proposals
- Verify proposed approach against known [DOMAIN] constraints

Provide specific, actionable feedback with references to RFC sections.
```

**Domain-to-agent mapping:** See `commands/shared/domain-agent-registry.md` for the full registry.

Include domain expert findings in Step 7 synthesis.

---

**📋 CHECKPOINT: Before proceeding to Step 7, verify:**

- [ ] rfc-reviewer has completed
- [ ] gemini-rfc-reviewer has completed
- [ ] visual-aid-recommender has completed
- [ ] Domain expert reviewers have completed (if spawned)
- [ ] All findings have been captured for synthesis

---

### 7. Synthesize All Findings

**REQUIRED: Pre-Synthesis Agent Verification**

Run Phase 3 from `commands/shared/agent-verification-pattern.md` to verify all contracted agents were spawned before proceeding.

Once all review agents have completed:

**7a. Consolidate review findings:**

- Combine findings from rfc-reviewer and gemini-rfc-reviewer
- **Include findings from domain expert reviewers (if spawned)**
- Identify common themes and issues flagged by multiple reviewers
- Note areas where reviewers disagree (valuable for discussion)
- **Highlight domain-specific insights that general reviewers may have missed**

**7b. Deduplicate and prioritize issues:**

- **Critical**: Must address before approval (technical flaws, security issues, missing critical information)
- **Major**: Should address before approval (gaps in reasoning, missing alternatives, unclear risks)
- **Minor**: Nice to have (clarifications, additional examples, minor improvements)
- **Enhancement**: Future considerations (optimizations, extensions, related work)

**7c. Build the Glossary:**

- Compile all terms researched from spotify-tool-researcher and web-search-researcher
- Include definitions, usage context, and documentation links
- Format with citations to source documentation

**7d. Process visual aids from visual-aid-recommender:**

- Extract the diagram code from the visual-aid-recommender output
- Validate that the diagram code is syntactically correct
- Prepare diagram code for inclusion in the report

---

### 8. Generate Review Report

**Ensure the output directory exists**:

```bash
mkdir -p ~/.claude/thoughts/shared/reviews/
```

**Create a unique filename**:

- Format: `rfc-review_{{RFC_TITLE_KEBAB_CASE}}_{{TIMESTAMP}}.md`
- Example: `rfc-review_cultural-context-service_2025-12-09.md`

**Write the review document** to `~/.claude/thoughts/shared/reviews/{{FILENAME}}` using the review report template:

@commands/shared/rfc-review-template.md

---

### 9. Present Review to User

After generating the report:

1. **Display a summary** of the review findings:

   ```
   ## Review Complete

   **RFC**: {{RFC_TITLE}}
   **Overall Recommendation**: {{RECOMMENDATION}}

   **Issues Found**:
   - Critical: {{COUNT}}
   - Major: {{COUNT}}
   - Minor: {{COUNT}}

   **Key Concerns**:
   - [Top 2-3 concerns]

   **Strengths**:
   - [Top 2-3 strengths]

   **Report saved to**: ~/.claude/thoughts/shared/reviews/{{FILENAME}}
   ```

2. **List the visual aids generated**:

   ```
   **Visual Aids Generated**:
   - [Diagram 1 title]: images/{{FILENAME}}.png
   - [Diagram 2 title]: images/{{FILENAME}}.png
   ...
   ```

3. **Ask for follow-up**:
   ```
   Would you like me to:
   1. Elaborate on any specific finding?
   2. Research additional context for any issue?
   3. Regenerate any diagrams with different focus or detail?
   ```

---

## Important Notes

- **No RFC modifications**: This command only reviews and generates a report. Never modify the RFC.
- **NEVER read linked documents in main context**: The main agent must NEVER read linked document content directly. Only identify linked documents (note URLs/titles) and delegate ALL reading to the linked-document-summarizer subagent. This prevents context bloat and ensures efficient processing. The only exception is if the user explicitly provides document content in their prompt.
- **NEVER pre-filter documents by type**: Send ALL identified linked documents to the subagent regardless of document type (Google Docs, Slack, Jira, GitHub, etc.). Let the subagent attempt to access each one and report success/failure. Do not assume any document type is inaccessible.
- **Document count consistency**: The number of linked documents identified MUST match the total in the final report (processed + failed + skipped = total identified). Any discrepancy indicates documents were incorrectly filtered out.
- **Linked document handling**: Linked documents are automatically summarized unless `--skip-linked-docs` is specified. Recursive links (links within linked documents) are NOT followed.
- **Linked document summarization**: By default, linked documents are summarized via the linked-document-summarizer subagent. Use `--skip-linked-docs` to disable this. If document access errors occur, the user is prompted to resolve or skip.
- **Context completeness assessment**: The review report must assess whether the RFC is self-contained. Identify linked documents and evaluate whether the RFC provides sufficient context without requiring readers to access external documents.
- **Sequential phase execution**: Complete all context-gathering before review agents, complete all reviews before synthesis.
- **Parallel execution within phases**: Launch all agents in each phase in parallel for efficiency.
- **Include context in prompts**: Review agent prompts MUST include the findings from context-gathering agents.
- **Constructive feedback**: Ensure all feedback is actionable, specific, and constructive.
- **Deduplication**: Consolidate duplicate findings from multiple reviewers.
- **Section references**: Always include specific references to RFC sections in issue descriptions.
- **Glossary citations**: Every glossary term must include a source/documentation link.
- **Diagram code**: All diagrams are included as Mermaid/PlantUML code blocks in the report. No external rendering service is used.
- **Repository discovery delegation**: NEVER search for repositories in the main agent context. Always delegate repository discovery to the `repo-discovery` subagent to avoid context bloat from directory listings and code search results.
- **Repository exploration limits**: If more than 5 repositories are identified for exploration, you MUST stop and ask the user to prioritize which ones to explore. Do NOT silently select a subset - always get explicit user confirmation. This prevents excessive agent spawning and context usage while ensuring the user controls which repos are explored.
- **Codebase exploration is optional but recommended**: If the RFC mentions systems/services, spawn repo-discovery. If repos are found, spawn exploration agents. If no repos are found or user skips, document this in the review.

## Review Dimensions Checklist

Before finalizing the review, ensure these dimensions are assessed:

- [ ] **Problem-Solution Fit**: Does the solution address the stated problem?
- [ ] **Technical Soundness**: Is the approach technically feasible?
- [ ] **Assumptions**: Are implicit assumptions identified and valid?
- [ ] **Evidence**: Is the proposal backed by sufficient evidence/data?
- [ ] **Alternatives**: Were reasonable alternatives considered?
- [ ] **Risks**: Are risks adequately identified with mitigations?
- [ ] **Impact Analysis**: What's the impact on existing systems?
- [ ] **Scope**: Are in-scope and out-of-scope clearly defined?
- [ ] **Implementation Path**: Is there a clear path to implementation?
- [ ] **Backwards Compatibility**: Are breaking changes addressed?
- [ ] **Security Implications**: Are security considerations covered?
- [ ] **Operational Concerns**: Are monitoring, alerting, and on-call covered?
- [ ] **Context Completeness**: Is the RFC self-contained with sufficient background? Are linked documents essential to understanding?
