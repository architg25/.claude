# Exit Code Interpretation

Styx workflows exit with specific codes indicating the type of failure.

## Exit Code Reference

### Exit 0 - Success

**Meaning**: Workflow completed successfully.

**Action**: No action needed.

---

### Exit 20 - Missing Dependencies

**Meaning**: One or more upstream dependencies are missing or incomplete.

**Common in**: Luigi tasks with `requires()` dependencies

**Investigation Steps**:
1. Get upstream dependencies:
   ```
   mcp__dataplatform__lineage_get_upstreams(dataset_id="<endpoint>")
   ```
2. For each upstream, check workflow status:
   ```
   mcp__dataplatform__styx_get_workflow_instances(...)
   ```
3. Find the first upstream that failed or was not triggered
4. Recurse until finding root cause

**Root Cause Examples**:
- Upstream workflow never triggered (Styx scheduler issue)
- Upstream workflow failed with different exit code
- External data source unavailable

---

### Exit 30 - Schema Mismatch / Task Failure

**Meaning**: Either:
- BigQuery schema mismatch (field type/name change)
- Luigi task assertion failure
- General task logic error

**Investigation Steps**:
1. Check recent commits to the workflow repository:
   ```
   mcp__code-search-mcp__search_code(
     query="<workflow_name> f:*.py",
     repo="<component>"
   )
   ```
2. Check BigQuery table schema for changes
3. Review Styx logs for specific error messages:
   ```
   mcp__dataplatform__gcp_logs_get_styx_logs(...)
   ```

**Common Fixes**:
- Revert schema change
- Update workflow code to match new schema
- Fix Luigi task logic

---

### Exit 50 - Unrecoverable Failure

**Meaning**: The workflow encountered an error that cannot be retried.

**Common Causes**:
- Dataflow job failure
- Service account permissions issue
- Code bug in pipeline logic

**Investigation Steps**:
1. Get detailed logs:
   ```
   mcp__dataplatform__gcp_logs_get_styx_logs(...)
   ```
2. Check for stack traces:
   ```
   mcp__cloud-logging-mcp__diagnose_service_errors(
     container="<container>",
     namespace="<namespace>",
     projectId="<project>"
   )
   ```
3. Escalate to workflow owner with log excerpts

**This typically requires code changes to fix.**

---

### Exit 137 - OOM (SIGKILL)

**Meaning**: The container was killed by the OOM killer (memory exhaustion).

**Investigation Steps**:
1. Check current resource limits in workflow definition
2. Review Dataflow job metrics for memory usage

**Remediation**:
1. Increase worker memory:
   ```yaml
   # In workflow YAML
   resources:
     limits:
       memory: "8Gi"  # Increase from default
   ```
2. Or use larger Dataflow machine type:
   ```python
   worker_machine_type = "n1-highmem-8"
   ```

---

### Other Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 1 | General error | Check logs |
| 2 | Misuse of shell command | Check docker args |
| 126 | Command not executable | Check file permissions |
| 127 | Command not found | Check Docker image |
| 128+ | Signal received (128+signal) | Check system issues |

## Quick Decision Tree

```
Exit Code?
├── 0 → Success, no action
├── 20 → Trace upstream dependencies
│         └── Find first failing/missing workflow
├── 30 → Check schema changes or task logic
│         └── Review recent commits
├── 50 → Check logs, escalate to owner
│         └── Likely needs code fix
└── 137 → OOM, increase memory
          └── Update resource limits
```
