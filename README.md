<p align="center">
  <img src="!/claude-jumping.svg" alt="Claude" />
</p>

# .claude

Personal Claude Code configuration. Core guidelines live in `CLAUDE.md` — everything else loads on-demand.

## Structure

```
.claude/
├── CLAUDE.md           # Global instructions (philosophy, rules, decision framework)
├── settings.json       # MCP servers, permissions, model config
├── skills/             # On-demand workflow docs (~28 skills)
├── commands/           # Slash commands (engineering/, architecture/, docs/, etc.)
├── hooks/              # Shell hooks (auto-format, notify, security-block, session-context)
├── plugins/            # Installed plugins (feature-dev, pr-review-toolkit, etc.)
├── agents/             # Custom agent configurations
├── ccline/             # Status line / powerline config
├── projects/           # Per-project memory and settings
└── tasks/              # Task tracking and lessons learned
```

## Skills

28 skills loaded on-demand via `/skill-name`. Grouped by purpose:

| Category            | Skills                                                                                                                  |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Workflow**        | planning-workflow, implementation-standards, debugging-protocol, mcp-tools-guide                                        |
| **Code quality**    | code-simplification-common, java-simplification-patterns, scala-simplification-patterns, python-simplification-patterns |
| **Spotify infra**   | apollo-configuration, kubernetes-deployments, decibel, locus-caching, rcs-patterns, mma-templates, data-endpoints       |
| **ML**              | ml-model-patterns, java-ml-serving-patterns                                                                             |
| **Experimentation** | experimentation-patterns, exposure-filtering                                                                            |
| **Java/Scala**      | migrate-to-junit5                                                                                                       |
| **Docs & tools**    | spotify-workflows, backstage-techdocs, google-docs, google-docs-visual-formatter, skill-creator, generate-completions   |
| **Team**            | vogons-epic-context                                                                                                     |

## Commands

Slash commands in `commands/`:

- `engineering/` — commit, ship, PR description, PR review, plan, implement, research
- `architecture/` — explain architecture patterns
- `documentation/` — RFC writing/review, README sections, feedback docs
- `refactor/` — tidy, refactor analysis
- `cleanup/` — context optimization
- `innitbruv` — project initialization with CLAUDE.md + feature docs

## Hooks

Shell hooks in `hooks/`:

- **auto-format.sh** — Format on save
- **notify.sh** — Desktop notifications
- **security-block.py** — Block dangerous operations
- **session-context.sh** — Inject session context on startup
