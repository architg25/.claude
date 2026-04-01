# Codex Dispatch Pattern

A standardized pattern for dispatching work to Codex CLI as a background agent. Use this whenever a skill needs to run Codex in parallel with other agents.

## Launching Codex

```bash
codex exec --full-auto -m <model> -o <output-file> "<prompt>"
```

### Required flags

- `-m <model>` -- the model to use (see Model Selection below)
- `-o <output-file>` -- where Codex writes its result
- `--full-auto` -- non-interactive mode, no user prompts

### Conditional flags

- `-C /path/to/repo` -- set working directory. Use when the target repo is not the current directory.
- `--skip-git-repo-check` -- required when running outside a git repository. Omit when inside one.

## Output directory

Always create a timestamped subdirectory under `/tmp` to avoid collisions between concurrent runs:

```
/tmp/<skill-name>-$(date +%s)/
```

Each agent within the run should write to a distinct file inside this directory (e.g., `codex-review.md`, `codex-tests.md`). Never reuse output paths across agents.

## Background execution

Always set `run_in_background: true` on the Bash tool call. Codex runs are long-lived and should not block the main thread.

```
Bash tool call:
  command: mkdir -p /tmp/my-skill-$(date +%s) && codex exec --full-auto -m <model> -o /tmp/my-skill-<ts>/output.md "<prompt>"
  run_in_background: true
```

## Output validation

After Codex completes, verify results before consuming them:

1. Check that the output file exists.
2. Check that it is non-empty.
3. If missing or empty, note the failure and proceed with results from other agents. Do not block the entire workflow on a single Codex failure.

## Model selection

Reference `shared:complexity-assessment` for the complexity tier and model IDs. Use the Codex model column:

- **Simple tasks** → lighter Codex model from the table (currently `gpt-5.4-mini`)
- **Complex tasks** → stronger Codex model from the table (currently `gpt-5.4`)

When in doubt, default to Complex. The model IDs here are just for quick reference — `shared:complexity-assessment` is the source of truth.

## Fallback: Codex unavailable

If Codex is not installed (`command not found`) or errors on launch:

1. Copy the same prompt you would have sent to Codex.
2. Dispatch via the **Agent tool** instead, with `run_in_background: true`.
3. The Agent subagent should write its output to the same output file path so downstream steps work unchanged.

This keeps the workflow running even when Codex is not available on the machine.
