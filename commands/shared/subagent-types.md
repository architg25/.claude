# Subagent Type Definitions

Descriptions of the specialized subagent types available for research, analysis, and review workflows. Each agent has a specific role -- use the right agent for the task.

## Codebase Research Agents

### codebase-locator

**Purpose**: Find WHERE files and components are in a repository.

- Finds relevant source files, configs, and tests
- Identifies specific directories to focus on
- Returns file paths and brief descriptions of what each file contains
- Use this FIRST before codebase-analyzer

### codebase-analyzer

**Purpose**: Understand HOW code works.

- Analyzes implementation details of specific files
- Traces data flow and key functions
- Explains architecture, patterns, and design decisions
- Returns detailed explanations with file:line references
- **Requires codebase-locator to run first** to identify which files to analyze

### codebase-pattern-finder

**Purpose**: Find existing abstractions, patterns, and similar implementations.

- Searches for abstract classes, interfaces, base classes
- Finds existing implementations that can be modeled after
- Identifies factory patterns, builder patterns, and other design patterns in use
- Returns usage counts and pattern locations

## Knowledge Research Agents

### spotify-tool-researcher

**Purpose**: Research Spotify-specific tools, systems, and internal context.

- Searches Spotify internal documentation (TechDocs)
- Finds relevant Slack discussions and channels
- Reads Google Docs, Sheets, and Slides content
- Searches code across Spotify repositories via code search
- Returns findings with links and citations

### web-search-researcher

**Purpose**: Research external concepts, technologies, and standards.

- Searches web for documentation and best practices
- Finds industry standards and protocol documentation
- Returns findings with links to external documentation
- Use when spotify-tool-researcher does not cover the topic, or to complement its findings

## Thoughts Directory Agents

### thoughts-locator

**Purpose**: Discover what documents exist in the `~/.claude/thoughts/` directory about a topic.

- Searches across research documents, plans, tickets, and notes
- Returns document paths and brief summaries
- Use this FIRST before thoughts-analyzer

### thoughts-analyzer

**Purpose**: Extract key insights from specific thoughts documents.

- Deep-reads the most relevant documents found by thoughts-locator
- Extracts decisions, findings, and historical context
- Returns structured insights with document references

## Repository Discovery Agents

### repo-discovery

**Purpose**: Find repository locations for systems mentioned in documents.

- Searches local directories (under `~/spotify/`) for repositories
- Falls back to code search if not found locally
- Returns structured results with confidence levels
- Recommends which exploration agent to use (codebase-locator for local, external-repo-explorer for external)

### external-repo-explorer

**Purpose**: Clone and explore repositories that are not available locally.

- Clones external repositories for analysis
- Explores architecture and main components
- Returns findings about integration patterns and key APIs

## Sequential Usage Pattern

For codebase research, agents should be used sequentially, not in parallel:

```
Batch 1 (parallel): codebase-locator + spotify-tool-researcher + web-search-researcher + thoughts-locator
   |
   v (wait for completion)
Batch 2 (parallel): codebase-analyzer + codebase-pattern-finder + thoughts-analyzer
```

**Reasoning**: Locator agents must find files before analyzer agents can explain them. This is a sequential dependency, not parallel work.
