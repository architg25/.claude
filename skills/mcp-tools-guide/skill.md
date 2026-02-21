# MCP Tools Guide

Use MCP tools when they're actually needed, not speculatively.

## Skills vs MCP Tools

- **IMPORTANT**: When a user request could be handled by either a skill (in `~/.claude/skills/`) or an MCP tool, ALWAYS check for and prefer using skills first
- Skills are custom, well-documented approaches specifically designed for common tasks
- Before using MCP tools for complex tasks, check if there's a relevant skill file
- Skills are documentation/instructions to read and follow, not commands to invoke

## Aika Search

**Use aika-search when:**
- Debugging Spotify internals without clear codebase pointers
- Finding documentation or Slack discussions about systems/decisions
- Understanding context for legacy code or design choices

## Code Search

**Use code-search when:**
- Finding usage patterns across multiple repos at ghe.spotify.net
- Understanding how others solved similar problems
- Verifying API usage before implementing

## GitHub CLI

**Use gh when:**
- Examining specific PRs or commit history
- Understanding recent changes affecting your work

## Sequential Thinking (FOR GENUINELY COMPLEX TASKS)

Use `mcp__sequential-thinking__sequentialthinking` when:
- Multi-file features or refactors (not simple edits)
- Non-obvious bugs requiring systematic analysis (not typos/simple fixes)
- Architecture decisions with multiple trade-offs
- Performance optimizations requiring measurement and analysis
- Security-sensitive implementations (threat modeling needed)
- API integrations (error handling, rate limits, edge cases)
- State management changes (race conditions, cleanup, side effects)

**DO NOT use for:**
- Typo fixes, simple bug fixes, or single-file changes
- Well-understood patterns you're just copying
- Trivial feature additions

## Context7 (FOR WORKING WITH EXTERNAL LIBRARIES)

Use the below tools if we need to utilize an external library to work on a feature.

**Use `mcp__context7__resolve-library-id` for:**
- Resolving a package/product name to a Context7-compatible library ID and returns a list of matching libraries
- You MUST call this function before 'get-library-docs' to obtain a valid Context7-compatible library ID UNLESS the user explicitly provides a library ID in the format '/org/project' or '/org/project/version'

**Use `mcp__context7__get-library-docs` for:**
- Fetching up-to-date documentation for a library
