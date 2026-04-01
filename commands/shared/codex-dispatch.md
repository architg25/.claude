# Codex CLI Reference

How to invoke the Codex CLI. For the full dual-agent dispatch pattern (when to use Codex, fallback, synthesis), see `shared:dual-agent-dispatch`.

## Command

```bash
codex exec --full-auto -m <model> -o <output-file> "<prompt>"
```

### Required flags

- `--full-auto` — non-interactive, no user prompts
- `-m <model>` — model ID (see `shared:complexity-assessment` for model table)
- `-o <output-file>` — where Codex writes its result

### Conditional flags

- `-C /path/to/repo` — set working directory (when target repo isn't cwd)
- `--skip-git-repo-check` — required when running outside a git repository

## Output conventions

- Create a timestamped directory: `/tmp/<skill-name>-$(date +%s)/`
- Each agent writes to a distinct file (e.g., `codex-review.md`, `codex-research.md`)
- Never reuse output paths across concurrent agents

## Background execution

Always use `run_in_background: true` on the Bash tool call. Codex runs are long-lived.
