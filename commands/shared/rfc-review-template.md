# RFC Review: {{RFC_TITLE}}

**Review Date**: {{DATE}}
**Reviewer**: Claude Code (automated review)
**RFC Authors**: {{AUTHORS}}
**RFC Status**: {{STATUS}}

---

## Executive Summary

[2-3 paragraphs summarizing:

- The core problem the RFC addresses
- The proposed solution at a high level
- Overall assessment of the RFC's merit
- Key concerns or strengths identified
- High-level recommendation (Approve / Approve with changes / Request revision)]

---

## RFC At-a-Glance

This section provides a condensed summary of the RFC, allowing readers to understand the review findings without reading the full RFC.

### Problem

[2-3 sentences describing the core problem. What pain point exists? Who is affected? What are the consequences of not solving it?]

### Proposed Solution

[2-3 sentences describing the proposed solution at a high level. What is being built? How does it solve the problem?]

### Key Design Decisions

| Decision Area                      | Choice        | Rationale         |
| ---------------------------------- | ------------- | ----------------- |
| [Area 1, e.g., "Architecture"]     | [Choice made] | [Why this choice] |
| [Area 2, e.g., "Caching Strategy"] | [Choice made] | [Why this choice] |
| [Area 3, e.g., "Data Storage"]     | [Choice made] | [Why this choice] |
| [Area 4, e.g., "API Design"]       | [Choice made] | [Why this choice] |
| [Area 5, e.g., "MVP Scope"]        | [Choice made] | [Why this choice] |

### Review Findings Summary

| Severity | Count | Key Issues                                           |
| -------- | ----- | ---------------------------------------------------- |
| Critical | [N]   | [1-2 sentence summary of critical issues, or "None"] |
| Major    | [N]   | [1-2 sentence summary of major issues, or "None"]    |
| Minor    | [N]   | [1-2 sentence summary of minor issues, or "None"]    |

---

## Visual Aids

[Diagrams created to help understand the RFC's key concepts]

### Diagram 1: [Title]

**Purpose**: [What this diagram explains]

```mermaid
[Mermaid code here]
```

---

### Diagram 2: [Title]

**Purpose**: [What this diagram explains]

```mermaid
[Mermaid code here]
```

[Repeat for each diagram generated]

---

## Glossary

[Technical and domain-specific terms defined with citations]

| Term     | Definition   | Source                  |
| -------- | ------------ | ----------------------- |
| [Term 1] | [Definition] | [Link to documentation] |
| [Term 2] | [Definition] | [Link to documentation] |
| [Term 3] | [Definition] | [Link to documentation] |

---

## Technical Review Findings

### Summary

[2-3 sentence overview of the technical review findings]

### Strengths & Highlights

[What the RFC does well]

- [Strength 1]
- [Strength 2]
  ...

### Critical Issues

[If none: "None identified."]

- **Issue [N]**: [RFC Section Reference]
  - **Description**: [Detailed description of the issue]
  - **Impact**: [Why this matters]
  - **Recommendation**: [Specific, actionable fix]

### Major Issues

[If none: "None identified."]

- **Issue [N]**: [RFC Section Reference]
  - **Description**: [Detailed description]
  - **Impact**: [Why this matters]
  - **Recommendation**: [Specific fix]

### Minor Issues

[If none: "None identified."]

- **Issue [N]**: [RFC Section Reference]
  - **Description**: [Brief description]
  - **Recommendation**: [Suggestion]

---

## Risk Analysis

### Risks Identified in RFC

[List risks the RFC authors identified, with assessment of their mitigations]

| Risk     | RFC's Mitigation   | Assessment                               |
| -------- | ------------------ | ---------------------------------------- |
| [Risk 1] | [Their mitigation] | Adequate / Needs strengthening / Missing |

### Additional Risks Identified

[Risks the review identified that aren't in the RFC]

- **Risk [N]**: [Description]
  - **Likelihood**: Low / Medium / High
  - **Impact**: Low / Medium / High
  - **Suggested Mitigation**: [Recommendation]

---

## Open Questions & Concerns

[Questions raised by the review that the RFC should address]

1. **[Question/Concern 1]**
   - Context: [Why this question matters]
   - Suggested resolution: [How to address it]

2. **[Question/Concern 2]**
   - Context: [Why this question matters]
   - Suggested resolution: [How to address it]

---

## Context Completeness Assessment

**Overall Assessment**: [Self-Contained / Mostly Self-Contained / Requires External Context]

### Context Provided in RFC

[What background, definitions, and context the RFC provides]

- [Context area 1]: [Assessment - Adequate / Partial / Missing]
- [Context area 2]: [Assessment - Adequate / Partial / Missing]
  ...

### Linked Documents Summary

[Documents referenced in the RFC that were summarized during this review]

| Document     | Type   | Relevance         | Key Contribution           |
| ------------ | ------ | ----------------- | -------------------------- |
| [Document 1] | [Type] | [High/Medium/Low] | [What context it provided] |

**Documents Not Accessed** (if any):
| Document | Link | Error | Impact on Review |
|----------|------|-------|------------------|
| [Document 1] | [URL] | [Error type] | [How lack of access affected review] |

### Missing Context

[Context that appears to be missing or insufficiently explained in the RFC]

- **[Missing Context 1]**:
  - What's missing: [Description]
  - Why it matters: [Impact on understanding/evaluation]
  - Recommendation: [How to address - add to RFC or link to external doc]

### Context Recommendations

[Recommendations for improving RFC self-containedness]

1. [Recommendation 1]
2. [Recommendation 2]
   ...

---

## Overall Recommendation

**Recommendation**: [Approve / Approve with Minor Changes / Approve with Major Changes / Request Revision]

**Rationale**: [2-3 sentences explaining the recommendation]

**Required Actions Before Approval**:

1. [Action 1 - Critical/Major issue to fix]
2. [Action 2 - Critical/Major issue to fix]
   ...

**Suggested Improvements** (optional but recommended):

1. [Improvement 1 - Minor issue or enhancement]
2. [Improvement 2 - Minor issue or enhancement]
   ...

---

## Review Methodology

This review was conducted using the following specialized subagents:

- **linked-document-summarizer**: Summarization of linked documents for context gathering
- **rfc-reviewer**: Technical merit and problem-solution fit analysis
- **gemini-rfc-reviewer**: Alternative perspective using Google's Gemini model
- **visual-aid-recommender**: Diagram code generation (Mermaid/PlantUML)
- **spotify-tool-researcher**: Spotify-specific terminology research
- **web-search-researcher**: External concept research (if applicable)
- **repo-discovery**: Repository location discovery for mentioned systems (if applicable)
- **codebase-locator**: Local repository structure exploration (if applicable)
- **external-repo-explorer**: External repository cloning and exploration (if applicable)
- **codebase-analyzer**: Deep code analysis (if applicable)

**Diagrams**: Diagrams are included as Mermaid/PlantUML code blocks.
