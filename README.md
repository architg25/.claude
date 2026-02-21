# .claude Configuration

Personal Claude Code configuration optimized for efficient token usage and workflow automation.

## Philosophy

This setup prioritizes:
- **Minimal context pollution** - Core guidelines load globally; specialized workflows load on-demand via skills
- **Learn from mistakes** - Track corrections in `tasks/lessons.md` to prevent repeat errors
- **Autonomous execution** - Sub-agents handle research/exploration without bloating main context
- **No cheerleading** - Direct, honest technical feedback over platitudes

## Structure

```
.claude/
├── CLAUDE.md              # Core philosophy & decision framework (52 lines)
├── skills/                # On-demand workflow documentation
│   ├── planning-workflow/
│   ├── implementation-standards/
│   ├── debugging-protocol/
│   ├── mcp-tools-guide/
│   └── spotify-workflows/
├── plugins/               # Installed Claude Code plugins
└── settings.local.json    # Local settings and MCP configs
```

## Core Guidelines (CLAUDE.md)

The global `CLAUDE.md` contains only:
- Philosophy (grumpy but helpful senior dev)
- Core beliefs (incremental, pragmatic, simple)
- Critical rules (3 attempts max, use subagents, prove it works)
- Decision framework (testability → readability → consistency → simplicity → reversibility)

**Token savings**: ~75% reduction vs monolithic instructions. Only pay for what's relevant.

## Skills System

Skills are loaded on-demand when needed, not upfront. Each skill documents a specific workflow:

### planning-workflow
- When to enter plan mode vs just coding
- TodoWrite usage and task management
- Autonomous bug fixing approach

**Load when**: Starting complex features, multi-file refactors

### implementation-standards
- 5-step implementation flow (Understand → Test → Implement → Refactor → Commit)
- Architecture principles (composition, DI, explicit dependencies)
- Quality gates and test guidelines

**Load when**: Implementing features, reviewing code quality

### debugging-protocol
- 4-step stuck protocol (Document → Research → Question → Try Different Angle)
- When to stop and reassess vs keep pushing

**Load when**: Hitting repeated failures on same issue

### mcp-tools-guide
- When to use aika-search vs code-search vs sequential-thinking
- Context7 external library documentation workflow
- Skills vs MCP tools decision matrix

**Load when**: Using MCP tools for research/exploration

### spotify-workflows
- Statements MCP (entity debugging only)
- Atlassian/JIRA conventions
- Backstage techdocs URL handling

**Load when**: Working with Spotify-internal systems

## Plugins

Active plugins for specialized workflows:

```shell
# Feature development with codebase understanding
/plugin install feature-dev

# PR review with specialized sub-agents
/plugin install pr-review-toolkit

# Git commit helpers
/plugin install commit-commands

# Agent SDK verification
/plugin install agent-sdk-dev

# Memory bank for long-term context
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

## MCP Servers

Configured in `settings.local.json`:

- **code-search** - Search across Spotify repos (Zoekt)
- **aika-search** - Semantic search (techdocs, Slack, Confluence, etc.)
- **atlassian-mcp** - JIRA integration (project: CONACCESS)
- **context7** - External library documentation
- **sequential-thinking** - Multi-step reasoning for complex tasks
- **statements-mcp** - Entity debugging (episodes, shows, audiobooks)

## Usage Patterns

### Starting a feature
1. Claude loads slim CLAUDE.md (52 lines)
2. Reads `planning-workflow` skill to understand your task management preferences
3. Creates todos, enters plan mode if >50 lines
4. Loads `implementation-standards` when ready to code

### Debugging an issue
1. Attempts fix (max 3 tries)
2. If stuck, loads `debugging-protocol` skill
3. Uses sub-agent for research to avoid context pollution
4. Documents lesson learned in `tasks/lessons.md`

### Using MCP tools
1. Loads `mcp-tools-guide` skill
2. Checks if existing skill covers the use case
3. Uses appropriate MCP tool (aika/code-search/sequential-thinking)
4. Sub-agent handles exploration if multi-step

## Token Budget

| Approach                  | Tokens per conversation                   |
|---------------------------|-------------------------------------------|
| Old monolithic CLAUDE.md  | ~8000 tokens                              |
| New skill-based system    | ~1000 tokens (core) + skills as needed    |
| **Savings**               | **~75% reduction in base context**        |

## Development Workflow

1. **All changes compile and pass tests** - Never commit broken code
2. **Max 3 attempts per issue** - Stop and reassess if stuck
3. **Learn from corrections** - Update `tasks/lessons.md` after user feedback
4. **Use sub-agents liberally** - Keep main context clean

## Quick Reference

### Critical Rules
- Stop after 3 failed attempts
- Use sub-agents for research/exploration
- Update lessons after corrections
- Prove it works before marking done

### Decision Framework
When choosing approaches, prioritize:
1. Testability
2. Readability
3. Consistency with existing code
4. Simplicity
5. Reversibility

### Never
- Bypass commit hooks or disable tests
- Make assumptions without verifying against existing code

### Always
- Learn from existing implementations first
- Write code as if maintained by a violent psychopath who knows where you live

---

*"Write code as if the person maintaining it is a violent psychopath who knows where you live. Make it that clear."*
