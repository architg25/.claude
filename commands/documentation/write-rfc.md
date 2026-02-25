---
description: Write a high-quality RFC following Spotify Search best practices
argument-hint: [brief RFC topic description]
---

# Write RFC

You are tasked with writing a high-quality RFC (Request for Comments) document following Spotify Search team best practices, based on the quality dimensions research in `~/.claude/thoughts/shared/research/2025-11-13-rfc-quality-dimensions.md`.

## Initial Setup:

When this command is invoked, respond with:

```
I'm ready to write an RFC. Please provide:
1. The problem you're trying to solve
2. Any relevant context (tickets, docs, existing code, related RFCs)
3. Any constraints or requirements

I'll guide you through creating a high-quality RFC that follows Spotify Search best practices.
```

Then wait for the user's input.

## Steps to follow after receiving the RFC context:

### 1. **Read all referenced materials first:**

- **CRITICAL**: Read the RFC quality dimensions guide first:
  ```
  @~/.claude/thoughts/shared/research/2025-11-13-rfc-quality-dimensions.md
  ```
- If the user mentions specific files (tickets, docs, code files, related RFCs, Google Docs), read them FULLY first
- **CRITICAL**: Google docs should be read using the google-drive mcp tool
- **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
- **CRITICAL**: Read these files yourself in the main context before starting the RFC
- This ensures you have full context before writing

### 2. **Synthesize the information:**

- **ULTRATHINK deeply about how to synthesize all the provided information into a coherent and comprehensive RFC**
- Analyze the materials you've read to identify:
  - The core problem and why it matters (with concrete examples)
  - Current pain points and their business/user impact
  - Existing architectural patterns and how they relate
  - Alternative approaches (from provided context or general knowledge)
  - Key stakeholders and affected systems
  - Potential risks and tradeoffs
  - **Unknowns and gaps** - what don't we know yet? What needs stakeholder input?
  - Implementation considerations
- Create a mental outline of how the RFC should flow:
  - Problem statement (why this matters)
  - High-level solution (accessible to all)
  - Technical details (for implementers)
  - Migration path (how to get there)
- **CRITICAL: Plan the main text vs appendix division**:
  - For each piece of information, ask: "Is this needed to approve the proposal or just to implement it?"
  - Main text (5-10 pages): Decision-critical information
  - Appendix (unlimited): Implementation details and supporting information
- Ensure you understand:
  - What's in scope vs out of scope
  - Who the audience is (engineers, PMs, architects)
  - What decision needs to be made
  - **What's unknown or needs discussion** (use Open Questions section if needed)
  - What the timeline is

### 3. **Draft RFC structure with user:**

- Based on the template from the quality dimensions guide
- Confirm with user:
  - Problem statement accuracy
  - Scope (what's in/out)
  - Key stakeholders (DACI model)
  - Timeline for feedback
- Ask: "Does this structure capture what you need? Any adjustments before I write the full RFC?"

### 4. **Write the RFC markdown file:**

- **CRITICAL: Distinguish main text from appendix**
  - **Main text**: Maximum 5 pages (up to 10 if heavy on diagrams) but the shorter the better
  - **Main text word count**: 2,000-3,000 words maximum
  - **Appendix**: NO PAGE LIMIT - include as much detail as needed for completeness

- **What belongs in main text vs appendix?**
  - **ULTRATHINK about each piece of information**: Is this needed to understand and critique the proposal, or is this implementation detail?
  - **Main text should contain**:
    - Problem understanding and business impact
    - Proposed solution at a high level PMs and architects can grasp
    - Key alternatives and why they were rejected
    - Major risks and mitigation strategies
    - High-level implementation approach and timeline (phases, milestones)
    - Enough detail for stakeholders to make an informed decision
    - Related RFCs and strategy documents (decision context)
  - **Appendix should contain**:
    - **Detailed Design** - code changes, API signatures, class structures
    - **Configuration Examples** - concrete code snippets, example requests/responses
    - Detailed current state architecture (if not essential to understanding the problem)
    - Deep implementation specifics (data models, API contracts, proto definitions)
    - Extended technical background
    - Additional case studies beyond the 3-5 in main text
    - Detailed benchmarks or performance analysis
    - Historical context that's interesting but not decision-critical
    - Research documents, external service docs, specific code references
  - **Litmus test**: If removing this section would prevent someone from understanding whether the proposal is sound → MAIN TEXT. If it's needed for implementation but not for approval → APPENDIX.

- Follow the template structure:

  ```markdown
  # RFC: [Descriptive Title]

  **Published**: YYYY-MM-DD
  **Authors**: [Names]
  **Decision by**: [Decision maker]
  **Consulted**: [Key reviewers]
  **Informed**: [Slack channels, teams]
  **Status**: Open until [YYYY-MM-DD + 2 weeks]

  ## Executive Summary

  [1-2 paragraphs: problem → solution → impact → key risks]

  ## Need

  [Problem statement with concrete examples from research]
  [Why it matters - business/user impact]
  [What happens if we do nothing]

  ## Guiding Principles

  [3-5 key principles that constrain the solution]

  ## Proposed Solution

  [High-level approach - accessible to PMs and architects]
  [Include "As-Is → To-Be" if applicable]
  [Keep implementation overview at high level - move details to Appendix]

  ## Case Studies (if applicable)

  [3-5 scenarios demonstrating how the design applies]

  ## Alternatives Considered

  [At least 2 alternatives with pros/cons]
  [Why they weren't chosen]

  ## Risks and Tradeoffs

  [Known risks with mitigation strategies]
  [Honest assessment of limitations]

  ## Out of Scope

  [Explicitly list what this RFC is NOT addressing]
  [Brief rationale for deferral]

  ## Open Questions / Unknowns (Optional)

  [Use this section when there are explicit gaps or decisions still to be made]
  [Be transparent about what you don't know or what needs stakeholder input]

  Format each unknown as:

  1. **[Question or Unknown Area]**
     - Current understanding: [What we know so far]
     - Gap/Uncertainty: [What we don't know or need to decide]
     - Options under consideration:
       - [ ] **Option A**: [Description]
         - Pros: [Benefits]
         - Cons: [Drawbacks]
       - [ ] **Option B**: [Description]
         - Pros: [Benefits]
         - Cons: [Drawbacks]
       - [ ] **Option C**: [Description or "Other - please suggest"]
     - Impact on proposal: [How this unknown affects the overall design]
     - Decision needed by: [Date, milestone, or "Before implementation"]
     - Owner: [Who will resolve this]

  Example unknowns:

  - Technical decisions still being evaluated
  - Tradeoffs where stakeholder input is needed
  - Integration points that need clarification from other teams
  - Performance characteristics that need benchmarking
  - Rollout strategy details pending further discussion

  ## Resources

  ### Related RFCs

  [Links to related RFCs - include Google Docs links. Hyperlinked text should be underlined]

  ### Strategy Documents

  [Links to strategy docs, company bets, product plans]

  ---

  ## Appendix

  ### Detailed Design

  [Technical implementation details]
  [Configuration structures with examples]
  [API definitions]
  [Code changes with file paths and line numbers]

  ### Configuration Examples

  [Concrete, copy-pastable examples from the codebase patterns]
  [Example requests/responses]
  [Test fixtures]

  ### Implementation Plan

  [Migration path from current state]
  [Phased rollout strategy]
  [Feature flags / RCS properties]
  [Rollback strategy]

  ### Additional Context (Optional)

  [Current state diagrams if not in main text]
  [Background information]
  [Future ideas]

  ### Additional Resources

  #### Research Documents

  [Links to research docs, investigations, analysis]

  #### External Services

  [Links to external service docs, APIs, architecture]

  #### Code References

  [Specific code references with file:line format]
  [Link to relevant source code]
  ```

- **PM-Friendly Writing Guidelines**:
  - Lead with user/business outcomes, not mechanisms
  - Use concrete examples before abstractions
  - Replace passive voice with ownership ("Service X will...")
  - Keep paragraphs short (≤5 lines)
  - Call out unknowns explicitly and assign owners

- **Apply the 15 Quality Dimensions**:
  1.  Brevity - respect reader time
  2.  Visual Communication - use diagrams for complex concepts
  3.  Explicit Scope Boundaries - clear in/out of scope
  4.  Concrete Examples - real configs and code
  5.  Case Studies - demonstrate applicability
  6.  Alternatives Considered - show your homework
  7.  Risk Assessment - honest about challenges
  8.  Resources and Citations - link everything
  9.  Appendices - move details out of main flow
  10. Accessibility - core ideas before technical details
  11. Clear Problem Statement - start with why
  12. Guiding Principles - design constraints
  13. Implementation Path - migration and rollout
  14. Metadata and Context - DACI model
  15. Configuration Examples - show real snippets

- Save to: `rfcs/YYYY-MM-DD-rfc-topic-name.md`

### 5. **Identify opportunities for visual aids using visual-aid-recommender agent:**

- **CRITICAL: Use the visual-aid-recommender agent to analyze the RFC**
- Launch the agent with the Task tool:
  ```
  Use the visual-aid-recommender agent to analyze the RFC at [path to RFC file]
  and recommend visual aids that would enhance understanding of the technical concepts.
  ```
- The agent will:
  - Read the RFC document
  - Identify concepts that would benefit from visualization
  - Recommend appropriate diagram types
  - Suggest specific content for each diagram
- Present the agent's recommendations to the user
- Ask user: "Would you like me to create these recommended diagrams?"

### 6. **Add visual aids (if requested):**

- If user wants diagrams added, create them using Mermaid or PlantUML syntax
- Insert diagrams inline in the appropriate sections
- Follow visual aid best practices:
  - Simplify - remove unnecessary details
  - Label clearly - every box, arrow, connection
  - Make self-contained - PM can interpret without text
  - Ensure accessibility - high contrast, 12pt+ text
  - Include scale & units where applicable
  - Add captions explaining what the diagram shows

### 7. **Review and reference visual aids in text:**

- **Scan through the RFC** to identify where visual aids have been added
- **Amend surrounding text** to reference the diagrams appropriately:
  - Add explicit references like "as shown in the diagram below" or "see Figure X"
  - Ensure the text introduces the diagram's purpose before it appears
  - After the diagram, briefly connect it back to the main narrative
  - Remove or condense redundant text that duplicates what the diagram shows
- **Ensure diagrams are self-explanatory** but also integrated into the document flow
- Update the RFC markdown file with these text amendments
- Inform user of changes made to integrate visual aids with text

### 8. **Run document editorial review:**

- **CRITICAL: Use the document-editor-reviewer agent**
- Launch the agent with the Task tool:

  ```
  Use the document-editor-reviewer agent to analyze the RFC at [path to RFC file]
  and provide editorial recommendations for grammar, readability, structure, and
  technical writing best practices.

  IMPORTANT: Pay special attention to opportunities where visual diagrams have been
  added - identify any text that is now redundant or could be removed/condensed
  because the diagram already explains the concept. The goal is to let diagrams
  do the heavy lifting for complex flows and processes, while keeping text concise.
  ```

- The agent will identify:
  - Grammatical errors and readability issues
  - Structural problems
  - Redundancy and spelling errors
  - Technical writing improvements
  - **Text that can be removed or condensed due to visual diagrams**
- Present the editorial findings to the user
- **Ask user: "Would you like me to apply these editorial recommendations before proceeding to technical review?"**

### 9. **Apply editorial improvements (if approved):**

- If user approves, apply the recommended editorial changes:
  - Grammar and sentence structure
  - Readability and paragraph flow
  - Clarity of technical explanations
  - Active voice and ownership clarity
  - Remove or condense text where diagrams make it redundant
- Update the RFC markdown file
- Inform user of changes made

### 10. **Add emojis to headers (optional):**

- **Ask user: "Would you like me to add emojis to section headers to help with visual navigation?"**
- If user approves:
  - **Scan through all headers** in the RFC (##, ###, etc.)
  - **For each header, determine if an emoji would help** with navigation and comprehension
  - **Add a single relevant emoji** at the start of appropriate headers:
    - Choose emojis that provide visual context for the section content
    - Examples:
      - "## 🎯 Need" or "## 📋 Executive Summary"
      - "## 💡 Proposed Solution" or "## ⚖️ Alternatives Considered"
      - "## ⚠️ Risks and Tradeoffs" or "## 🚫 Out of Scope"
      - "## ❓ Open Questions" or "## 🔗 Resources"
      - "## 📚 Appendix" or "## 🛠️ Implementation Plan"
    - **Only use one emoji per header** - avoid emoji overload
    - **Not all headers need emojis** - use sparingly where they add value
    - Prioritize top-level sections (##) over subsections (###)
  - Update the RFC markdown file with emoji additions
  - Inform user of emoji additions made
- If user declines, skip this step and proceed to the next step

### 11. **Run comprehensive RFC technical review:**

- **Delegate the full review to the `rfc-review` command**, which handles domain detection, parallel review agent spawning (rfc-reviewer, gemini-rfc-reviewer, domain experts), context gathering, and synthesis.
- Use the Skill tool to run `documentation:rfc-review` on the draft RFC file path (e.g., `rfcs/YYYY-MM-DD-rfc-topic-name.md`).
- Wait for the review to complete. The review report will be saved to `~/.claude/thoughts/shared/reviews/`.

### 12. **Present review findings and ask to apply:**

- Read the review report generated by `rfc-review`.
- Present a consolidated summary to the user:

  ```
  ## Technical Review Summary

  **Overall Recommendation:** [From review report]

  **Critical Issues:** [Count and summary]
  **Major Issues:** [Count and summary]
  **Minor Issues:** [Count and summary]

  **Key Strengths:**
  - [From review report]

  **Recommended Actions:**
  1. [Prioritized actions from review]
  2. [Prioritized actions from review]
  ...

  Full review report: ~/.claude/thoughts/shared/reviews/[filename]
  ```

- Ask user: "Would you like me to apply these technical improvements?"

### 13. **Apply technical improvements (if approved):**

- If user approves, apply the recommended changes:
  - Address logical gaps or technical soundness issues
  - Add missing evidence or concrete examples
  - Clarify assumptions or alternatives
  - Strengthen risk assessments
- Update the RFC markdown file
- Inform user of changes made

### 14. **Present RFC for user review:**

- Show the complete RFC structure and key sections
- Highlight:
  - Problem statement and impact
  - Proposed solution overview
  - Key risks and mitigations
  - Implementation approach
- **MANDATORY: Ask the user:**

  ```
  I've completed the RFC draft. Please review:

  1. Does the problem statement accurately reflect your needs?
  2. Is the proposed solution clear and complete?
  3. Are there any missing sections or areas that need expansion?
  4. Should I adjust anything before converting to Google Docs?
  ```

### 15. **Iterate based on feedback:**

- If user has feedback, update the RFC accordingly
- Update visual aids if the design changes
- Re-run editorial or technical review if major sections change
- Continue iteration until user approves

### 16. **Convert to Google Docs:**

- **CRITICAL: Only proceed after user approval**
- Use the `google-docs` skill to convert the RFC
- Follow the skill instructions in `~/.claude/skills/google-docs/`
- The skill will:
  - Render any diagrams (Mermaid, Graphviz, PlantUML) as images
  - Apply Spotify-friendly formatting (Proxima Nova text, Consolas code)
  - Upload to Google Drive
  - Return a shareable link
- Present the Google Docs link to the user
- Remind user to:
  - Set appropriate sharing permissions
  - Share in #search-rfcs Slack channel
  - Update stakeholder lists (Decision by, Consulted, Informed)

### 17. **Validate Google Doc Formatting Visually:**

- Follow the visual formatting validation sub-workflow documented in the `google-docs` skill
- See `@skills/google-docs/visual-formatting.md` for the full process (screenshot capture, pixel comparison, SSIM validation)
- Pass the markdown file path and Google Doc URL from step 16

### 18. **Final steps:**

- Keep the markdown version in the `rfcs/` directory
- Ask: "Would you like me to:
  1.  Create a Jira ticket for this RFC?
  2.  Draft a Slack message for #search-rfcs?
  3.  Link this RFC from relevant code files (TechDocs, Javadoc)?"

## Important Notes:

- **Brevity is critical for MAIN TEXT ONLY**:
  - Maximum 5-10 pages for main text but nicer if it's shorter (the decision-making content)
  - NO PAGE LIMIT for appendix - make it as detailed as needed
  - ULTRATHINK about each section: "Is this needed to approve the proposal or just to implement it?"
  - Main text = enough to critique and approve; Appendix = implementation details
- **PM accessibility**: Core ideas must be understandable without deep technical knowledge
- **Visual aids matter**: Use specialized agents to identify what needs diagrams
- **Concrete over abstract**: Show real configs, real code, real examples
- **Honest about risks AND unknowns**: Don't hide limitations, tradeoffs, or gaps in knowledge
- **Use Open Questions section**: When you have unknowns, make them explicit with options for reviewers
- **Actionable**: Include clear implementation and migration paths
- **Well-researched**: Show alternatives considered with reasoning
- **Properly scoped**: Explicit in-scope and out-of-scope sections
- **DACI model**: Clear stakeholders and timeline
- **Follow Spotify patterns**: Reference existing RFCs and codebase patterns
- **Agent-based review workflow**: Use specialized agents for visual aids, editorial review, and technical review to ensure comprehensive quality assessment

## Quality Checklist (from research):

Before presenting for user review, verify:

- [ ] **Brevity (Main Text Only)**: Maximum of 2,000-3,000 words, 5-10 pages but keep as short as possible (Appendix can be unlimited)
- [ ] **Main Text vs Appendix**: Each section is in the right place (decision-critical vs implementation detail)
- [ ] **Visual Communication**: Diagrams for complex concepts (≥3 entities or >2 paragraphs)
- [ ] **Explicit Scope**: Clear in-scope and out-of-scope sections
- [ ] **Concrete Examples**: Real configs, code snippets, data
- [ ] **Case Studies**: 3-5 scenarios demonstrating design (if applicable)
- [ ] **Alternatives**: At least 2 alternatives with pros/cons
- [ ] **Risk Assessment**: Honest risks with mitigations
- [ ] **Open Questions/Unknowns**: Gaps explicitly called out with options (if applicable)
- [ ] **Resources**: Links to related RFCs, docs, code
- [ ] **Appendices**: Implementation details moved out of main flow
- [ ] **Accessibility**: Core ideas before technical details
- [ ] **Problem Statement**: Clear why with concrete examples
- [ ] **Guiding Principles**: 3-5 design constraints
- [ ] **Implementation Path**: Migration, rollout, rollback
- [ ] **Metadata**: DACI model with deadline
- [ ] **Configuration Examples**: Copy-pastable snippets
- [ ] **Editorial Quality**: Reviewed by document-editor-reviewer agent
- [ ] **Technical Merit**: Reviewed by both rfc-reviewer and gemini-rfc-reviewer agents

## Anti-Patterns to Avoid:

1. **The Encyclopedia** - Overwhelming detail in MAIN TEXT (keep main text 5-10 pages max; move details to appendix!)
2. **The Mystery** - Not explaining the problem or why it matters
3. **The Fait Accompli** - Only one solution without alternatives
4. **The Technical Deep Dive** - Leading with implementation before problem
5. **The Optimist** - Ignoring risks or pretending no tradeoffs
6. **The Hand-Waver** - Hiding unknowns instead of calling them out explicitly
7. **The Orphan** - No clear owners or timeline
8. **The Scope Creep** - Trying to solve too many problems
9. **The Text Wall** - No visual aids for complex flows
10. **The Abstract** - No concrete examples or case studies
11. **The Stale Doc** - Plan to update as implementation progresses
