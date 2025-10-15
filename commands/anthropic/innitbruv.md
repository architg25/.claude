---
allowed-tools: Write, Read, Edit, Glob, Grep, LS, Bash(mkdir:*), Bash(mvn:*), Bash(echo:*), Task, TodoWrite
description: Initialize project with CLAUDE.md and create comprehensive feature documentation using parallel task delegation
---

## Project Initialization & Feature Documentation (TodoWrite Method)

This command initializes a project by creating CLAUDE.md and systematically documenting all major features using parallel task delegation to optimize speed and context efficiency.

---

## EXECUTION WORKFLOW

### TodoWrite Task Structure

```json
[
  {"id": "setup_timestamp", "content": "Record initialization start time", "status": "pending", "activeForm": "Recording initialization start time", "priority": "high"},
  {"id": "analyze_codebase", "content": "Analyze codebase structure to identify features (Task-based)", "status": "pending", "activeForm": "Analyzing codebase structure to identify features", "priority": "high"},
  {"id": "create_claude_md", "content": "Create initial CLAUDE.md with project context", "status": "pending", "activeForm": "Creating initial CLAUDE.md with project context", "priority": "high"},
  {"id": "doc_feature_group_1", "content": "Document feature group 1 (Subagent A - parallel)", "status": "pending", "activeForm": "Documenting feature group 1", "priority": "high", "parallel_group": "feature_docs"},
  {"id": "doc_feature_group_2", "content": "Document feature group 2 (Subagent B - parallel)", "status": "pending", "activeForm": "Documenting feature group 2", "priority": "high", "parallel_group": "feature_docs"},
  {"id": "doc_feature_group_3", "content": "Document feature group 3 (Subagent C - parallel)", "status": "pending", "activeForm": "Documenting feature group 3", "priority": "high", "parallel_group": "feature_docs"},
  {"id": "doc_feature_group_4", "content": "Document feature group 4 (Subagent D - parallel)", "status": "pending", "activeForm": "Documenting feature group 4", "priority": "high", "parallel_group": "feature_docs"},
  {"id": "consolidate_features", "content": "Consolidate parallel feature documentation", "status": "pending", "activeForm": "Consolidating parallel feature documentation", "priority": "high", "depends_on": ["feature_docs"]},
  {"id": "update_claude_md", "content": "Update CLAUDE.md with feature index", "status": "pending", "activeForm": "Updating CLAUDE.md with feature index", "priority": "high"},
  {"id": "final_timestamp", "content": "Record completion time and summary", "status": "pending", "activeForm": "Recording completion time and summary", "priority": "high"}
]
```

---

## PHASE 1: SETUP & INITIALIZATION

### Task: Record Start Time
**TodoWrite**: Mark "setup_timestamp" as in_progress

```bash
echo "Project initialization started: $(date '+%Y-%m-%d %H:%M:%S')"
```

**TodoWrite**: Mark "setup_timestamp" completed, "analyze_codebase" as in_progress

---

## PHASE 2: CODEBASE ANALYSIS (TASK-BASED)

### Task: Feature Identification
**TodoWrite**: Mark "analyze_codebase" as in_progress

**CRITICAL**: Use Task tool delegation to prevent context overflow during initial codebase analysis.

**Task Delegation**:
```
Task Description: "Analyze Codebase for Feature Identification"

Task Prompt: "Analyze the project structure to identify all major features and functionality areas.

**ANALYSIS APPROACH**:
1. Examine project directory structure for functional modules
2. Identify main entry points and core components
3. Review configuration files for feature flags or module definitions
4. Analyze package/module organization patterns
5. Identify distinct functionality domains

**CONTEXT MANAGEMENT**:
- Start with high-level structure (directory tree, README, package.json/setup.py/pom.xml)
- Progressively examine 3-5 key files per functional area
- Use Glob for pattern discovery, Read for strategic file inspection
- Avoid loading entire codebase simultaneously

**OUTPUT REQUIREMENTS**:
Provide a structured list of features with:
- Feature name (kebab-case for filenames)
- Brief description (1-2 sentences)
- Primary files/directories involved (3-5 key files max)
- Estimated complexity (simple/moderate/complex)

Format as JSON array for programmatic processing:
[
  {
    \"feature_name\": \"user-authentication\",
    \"description\": \"Handles user login, registration, and session management\",
    \"key_files\": [\"src/auth/login.py\", \"src/auth/session.py\", \"src/models/user.py\"],
    \"complexity\": \"moderate\"
  },
  ...
]
"
```

**TodoWrite**: Mark "analyze_codebase" completed, "create_claude_md" as in_progress

---

## PHASE 3: INITIAL CLAUDE.MD CREATION

### Task: Create Base Documentation
**TodoWrite**: Mark "create_claude_md" as in_progress

Create the initial CLAUDE.md file with project context:

```markdown
# [Project Name]

## Overview
[Auto-detected project description from README/package metadata]

## Architecture
[High-level architecture summary from codebase analysis]

## Build & Test
[Commands detected from package.json/Makefile/build scripts]

## Features
[Will be populated after feature documentation completes]

---
```

Create directory structure for feature documentation:
```bash
mkdir -p docs/development/features
```

**TodoWrite**: Mark "create_claude_md" completed, prepare for parallel feature documentation

---

## PHASE 4: PARALLEL FEATURE DOCUMENTATION

**CRITICAL**: Distribute features evenly across 4 parallel subagents based on feature count from Phase 2 analysis.

**Feature Distribution Logic**:
```
Total Features: N
Subagent A: Features 1 to ⌈N/4⌉
Subagent B: Features ⌈N/4⌉+1 to ⌈N/2⌉
Subagent C: Features ⌈N/2⌉+1 to ⌈3N/4⌉
Subagent D: Features ⌈3N/4⌉+1 to N
```

### Subagent A: Feature Group 1 Documentation
**TodoWrite**: Mark "doc_feature_group_1" as in_progress

**Task Delegation**:
```
Task Description: "Document Feature Group 1 (Features 1-⌈N/4⌉)"

Task Prompt: "Create detailed feature documentation for assigned features in `docs/development/features/`.

**ASSIGNED FEATURES**: [Features 1 through ⌈N/4⌉ from Phase 2 analysis]

**DOCUMENTATION REQUIREMENTS** (per feature):

1. **Feature Overview** (2-3 sentences)
   - What the feature does
   - Why it exists / business value
   - Key user-facing or system capabilities

2. **Technical Architecture** (information-dense, brief)
   - Core components and their responsibilities
   - Data flow and key interactions
   - Integration points with other features
   - Important design patterns used

3. **Key Files** (file:line references where applicable)
   - Primary implementation files (3-5 max per feature)
   - Configuration files
   - Test files
   - Related documentation

4. **Dependencies**
   - External libraries used
   - Internal feature dependencies
   - Database/storage requirements
   - API integrations

5. **Development Guidelines**
   - How to extend this feature
   - Common modification patterns
   - Testing approach
   - Known limitations or gotchas

**CONTEXT MANAGEMENT**:
- Analyze maximum 5 files per feature
- Use strategic Read operations for key files
- Use Grep for pattern discovery across feature domain
- Avoid loading all feature files simultaneously

**OUTPUT FORMAT**:
- Create `docs/development/features/[feature-name].md` for each feature
- Return JSON metadata for CLAUDE.md index:
[
  {
    \"feature_name\": \"user-authentication\",
    \"file_path\": \"docs/development/features/user-authentication.md\",
    \"summary\": \"User login, registration, and session management\"
  },
  ...
]
"
```

### Subagent B: Feature Group 2 Documentation
**TodoWrite**: Mark "doc_feature_group_2" as in_progress (parallel with A)

**Task Delegation**: [Same prompt structure as Subagent A, with features ⌈N/4⌉+1 to ⌈N/2⌉]

### Subagent C: Feature Group 3 Documentation
**TodoWrite**: Mark "doc_feature_group_3" as in_progress (parallel with A, B)

**Task Delegation**: [Same prompt structure as Subagent A, with features ⌈N/2⌉+1 to ⌈3N/4⌉]

### Subagent D: Feature Group 4 Documentation
**TodoWrite**: Mark "doc_feature_group_4" as in_progress (parallel with A, B, C)

**Task Delegation**: [Same prompt structure as Subagent A, with features ⌈3N/4⌉+1 to N]

---

## PHASE 5: CONSOLIDATION & INTEGRATION

### Task: Consolidate Parallel Findings
**TodoWrite**: Mark all parallel groups completed, "consolidate_features" as in_progress

**Consolidation Process**:
1. **Collect Metadata**: Gather JSON metadata from all 4 subagents
2. **Validate Completeness**: Ensure all features have documentation files created
3. **Check for Overlaps**: Identify any cross-feature dependencies or documentation gaps
4. **Verify File Creation**: Confirm all `docs/development/features/*.md` files exist
5. **Prepare Index Data**: Merge JSON metadata arrays for CLAUDE.md update

**Quality Gates**:
- [ ] All assigned features documented
- [ ] All feature files exist in `docs/development/features/`
- [ ] No duplicate feature names
- [ ] All metadata includes feature_name, file_path, summary
- [ ] Cross-feature dependencies identified

**TodoWrite**: Mark "consolidate_features" completed, "update_claude_md" as in_progress

---

## PHASE 6: CLAUDE.MD UPDATE

### Task: Update with Feature Index
**TodoWrite**: Mark "update_claude_md" as in_progress

Update the CLAUDE.md file with the comprehensive feature index:

```markdown
## Features

### Feature Index
| Feature | Summary | Documentation |
|---------|---------|---------------|
| [feature-name-1] | [Brief 1-line summary] | [docs/development/features/feature-name-1.md] |
| [feature-name-2] | [Brief 1-line summary] | [docs/development/features/feature-name-2.md] |
| ... | ... | ... |

### Feature Categories
[Optional: Group features by domain/category if applicable]

**For detailed information** on any feature, see the corresponding documentation file in `docs/development/features/`.
```

**TodoWrite**: Mark "update_claude_md" completed, "final_timestamp" as in_progress

---

## PHASE 7: COMPLETION

### Task: Final Summary
**TodoWrite**: Mark "final_timestamp" as in_progress

```bash
echo "Project initialization completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Total features documented: [N]"
echo "Documentation location: docs/development/features/"
echo "Project documentation: CLAUDE.md"
```

**TodoWrite**: Mark "final_timestamp" completed

**Completion Message**:
```
✅ Project initialization complete!

Created:
- CLAUDE.md (project documentation with feature index)
- docs/development/features/ ([N] feature documentation files)

Next steps:
- Review CLAUDE.md for project overview
- Explore individual feature docs for development context
- Use feature documentation to guide implementation work
```

---

## CONTEXT MANAGEMENT RULES

**CRITICAL SUCCESS PATTERNS**:
1. **Task Delegation**: Use Task tool for codebase analysis and all feature documentation phases
2. **File Limits**: Maximum 5 files per feature analysis
3. **Parallel Execution**: 4 subagents running simultaneously for feature documentation (60-70% speed improvement)
4. **Progressive Analysis**: Never load entire codebase; use strategic file selection
5. **Fresh Context**: Each Task operation gets clean context to prevent overflow

**AVOID PATTERNS**:
- ❌ `@file1 @file2 @file3...` bulk file loading
- ❌ Loading all features simultaneously in main context
- ❌ Sequential feature documentation (use parallel subagents instead)
- ❌ Reading entire codebase before feature identification

**USE PATTERNS**:
- ✅ Task delegation for codebase analysis with progressive file examination
- ✅ Parallel subagents for feature documentation (4 concurrent)
- ✅ Strategic file selection (3-5 files per feature max)
- ✅ TodoWrite tracking for transparent progress visibility

---

## OPTIMIZATION NOTES

**Parallel Execution Benefits**:
- **Speed**: 60-70% faster than sequential documentation
- **Coverage**: Each subagent maintains deep focus on assigned features
- **Context Efficiency**: Fresh context per subagent prevents overflow
- **Scalability**: Handles projects with 20+ features efficiently

**Estimated Timeline**:
- Small projects (1-5 features): ~3-5 minutes total
- Medium projects (6-15 features): ~5-10 minutes total
- Large projects (16+ features): ~10-15 minutes total

Parallel subagent execution provides near-linear scaling compared to sequential approach.