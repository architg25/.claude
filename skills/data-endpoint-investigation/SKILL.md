---
name: Data Endpoint Investigation
description: Investigates data endpoint incidents including lateness/SLO breaches, missing dependencies, schema failures, and workflow errors. Use this skill when the user wants to (1) investigate a PagerDuty incident, (2) trace upstream dependencies for a failing endpoint, (3) understand why a workflow failed, (4) find the root cause of data lateness, or (5) generate backfill commands. Follows a phased investigation pattern.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - mcp__dataplatform__greg_get_dataset
  - mcp__dataplatform__lineage_get_upstreams
  - mcp__dataplatform__lineage_get_downstreams
  - mcp__dataplatform__styx_get_workflows
  - mcp__dataplatform__styx_get_workflow
  - mcp__dataplatform__styx_get_workflow_instances
  - mcp__dataplatform__gcp_logs_get_flyte_logs
  - mcp__dataplatform__gcp_logs_get_styx_logs
  - mcp__component-metadata-mcp__get_component_id_context
  - mcp__o11y-agg-mcp__list_incidents
  - mcp__o11y-agg-mcp__get_incident
  - mcp__o11y-agg-mcp__list_alerts
  - mcp__cloud-logging-mcp__diagnose_service_errors
  - mcp__code-search-mcp__search_code
  - mcp__code-search-mcp__read_file
---

# Data Endpoint Investigation

Systematic investigation of data endpoint incidents using MCP tools.

## Quick Start

For a quick investigation, use these MCP tools in order:

### 1. Get Endpoint Metadata
```
mcp__dataplatform__greg_get_dataset(dataset_id="<endpoint_id>")
```
Returns: owner, SLO, component_id, workflow mappings.

### 2. Check Workflow Status

```
mcp__dataplatform__styx_get_workflow_instances(
  component_id="<component>",
  workflow_id="<workflow>",
  start="YYYY-MM-DD",
  end="YYYY-MM-DD",
  limit=10
)
```
Returns: execution history with triggers, statuses, and **exit codes**.

### 3. Trace Upstream Dependencies
```
mcp__dataplatform__lineage_get_upstreams(dataset_id="<endpoint_id>")
```
For each upstream, repeat step 2 to find the root failing workflow.

### 4. Get Logs for Root Cause
```
mcp__dataplatform__gcp_logs_get_styx_logs(
  styx_pod_name="<pod_name>",
  execution_date="YYYY-MM-DD"
)
```
Or for Flyte workflows:
```
mcp__dataplatform__gcp_logs_get_flyte_logs(
  flyte_namespace="<namespace>",
  flyte_execution_id="<exec_id>",
  execution_date="YYYY-MM-DD"
)
```

## Investigation Workflow

### Phase 1: Parse Incident Context

**Input**: PagerDuty incident URL, endpoint name, or partition date

**Extract**:
- Endpoint ID (e.g., `search-semantic-episode.genre-vectors.bq`)
- Affected partition (e.g., `2026-02-04T00:00`)
- Alert type (lateness, failure, SLO breach)

### Phase 2: Get Endpoint Metadata

Use `mcp__dataplatform__greg_get_dataset` to get:
- Owner (for escalation)
- SLO configuration
- Component ID (for workflow lookup)
- Storage URI pattern

### Phase 3: Check Workflow Status

Use `mcp__dataplatform__styx_get_workflow_instances` to get execution history.

Check:
- Did the workflow trigger? (Look for `trigger` field)
- What was the exit code / final status?
- How many retries occurred?

**Key fields to examine**:
- `state`: DONE, FAILED, RUNNING, QUEUED
- `executionInfo.exitCode`: See [Exit Codes](exit-codes.md)
- `trigger`: NATURAL (scheduled) vs AD_HOC (manual)

### Phase 4: Interpret Exit Code

See [Exit Codes](exit-codes.md) for full interpretation.

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | No action needed |
| 20 | Missing dependencies | Trace upstream lineage |
| 30 | Schema mismatch / Luigi failure | Check recent schema changes |
| 50 | Unrecoverable failure | Check logs, escalate to owner |
| 137 | OOM (SIGKILL) | Recommend memory increase |

### Phase 5: Trace Upstream (if Exit 20)

Use `mcp__dataplatform__lineage_get_upstreams` to get dependencies.

**CRITICAL — Lineage API is incomplete**: The lineage API only tracks registered
data endpoints. It does NOT capture internal Luigi task dependencies (e.g., a
`FeatureStore` task required by a `VectorJob`). You MUST also:

1. **Read the workflow source code** to find ALL dependencies:
   - Get the workflow config via `styx_get_workflow` — look at `docker_args` for `--module` and the task class
   - Search for the task class in code: `mcp__code-search-mcp__search_code(query="class <TaskName>")`
   - Read the `requires()` method to find every dependency
   - For WrapperTasks that require multiple sub-tasks, check ALL sub-tasks' dependencies

2. For each upstream (from BOTH lineage AND source code):
   - Get its workflow instances (Phase 3)
   - Verify `trigger_complete: true` — not just that one execution succeeded
   - If failed, check its exit code
   - Recurse until finding the root cause

3. **Check ALL branches, not just one**: A workflow often has multiple independent
   upstream dependencies. Do NOT stop investigating after finding one failing
   upstream — there may be others. The actual blocker might be a different
   dependency than the one that appears first in the lineage API.

**Root cause** = First workflow in the chain that:
- Has `trigger_complete: false` with extended retrying, OR
- Failed with exit code != 20, OR
- Was never triggered (no natural trigger)

### Phase 6: Get Logs for Root Cause

For Luigi/Styx workflows:
```
mcp__dataplatform__gcp_logs_get_styx_logs(
  styx_pod_name="<workflow>-<partition>",
  execution_date="YYYY-MM-DD"
)
```

For Flyte/Liftoff workflows:
```
mcp__dataplatform__gcp_logs_get_flyte_logs(
  flyte_namespace="<component>",
  flyte_execution_id="<id>",
  execution_date="YYYY-MM-DD"
)
```

### Phase 7: Check if the Problem is Self-Resolving

Before recommending remediation, check if the workflow is **already recovering**:

1. Look at the **current/latest execution** — is it still running?
2. Compare its runtime to the **typical failure time** for the error type.
   - MISSING_DEPS failures typically occur within ~20 seconds of STARTED.
   - OOM/SIGKILL (exit 137) typically occurs within minutes.
3. If the current execution has been running **significantly longer** than the
   typical failure time, the error is likely resolved and no action is needed.

**Example**: If 220 prior executions all failed with MISSING_DEPS within 20s of
starting, but the current execution has been running for 24 minutes, the
dependency has likely become available and the job is doing real work. Just
monitor — don't trigger a manual backfill.

4. **Verify actual output existence** — even if the workflow status looks like
   it's recovering, confirm the output exists:
   ```bash
   bq ls "<project>:<dataset>" 2>&1 | grep <table_prefix> | sort | tail -5
   ```
   A workflow can show SUCCESS status but the output may not have propagated,
   or a DIFFERENT dependency in the chain may still be missing.

5. **Check ALL workflows in the chain** — do not conclude the issue is
   self-resolving based on only the deepest upstream. Verify `trigger_complete`
   for every intermediate workflow between the root cause and the alerted endpoint.

### Phase 8: Generate Remediation

**Output includes**:
1. Root cause summary
2. Failure chain visualization
3. Owner contact info (if external)
4. Backfill commands (user must execute manually)
5. Escalation message template (if needed)

## Backfill Commands

**IMPORTANT**: Do NOT execute these automatically. Provide for user to run.

### Styx Backfill
```bash
styx trigger <component> <workflow_id> <partition> --reason "Backfill after incident"
```

### Flyte Backfill
```bash
flyte launch --project <project> --domain production --name <workflow> --inputs partition=<date>
```

## Related Skills

- [data-endpoints](../data-endpoints/SKILL.md) - View data, schema, status
- [luigi-workflows](../luigi-workflows/SKILL.md) - Luigi task patterns
- [flyte-liftoff-workflows](../flyte-liftoff-workflows/SKILL.md) - Flyte workflow patterns

## Troubleshooting

### BQ Table Existence Checks

When checking if output tables exist (e.g., for `HourlyBQTask` dependencies):
```bash
bq ls --max_results=2000 "<project>:<dataset>" 2>&1 | grep <table_prefix> | sort -t_ -k3 -r | head -10
```

See also [Troubleshooting Guide](troubleshooting.md) for other common issues.
