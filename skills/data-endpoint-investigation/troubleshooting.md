# Troubleshooting Guide

Common scenarios encountered during data endpoint investigations.

## Lateness / SLO Breach

### Symptom
PagerDuty alert for data endpoint lateness or SLO breach.

### Diagnosis
1. Get endpoint metadata and SLO:
   ```
   mcp__dataplatform__greg_get_dataset(dataset_id="<endpoint>")
   ```

2. Check recent workflow instances:
   ```
   mcp__dataplatform__styx_get_workflow_instances(
     component_id="<component>",
     workflow_id="<workflow>",
     start="YYYY-MM-DD",
     end="YYYY-MM-DD",
     limit=10
   )
   ```

3. Look for:
   - Failed executions (exit code != 0)
   - Missing natural triggers (no NATURAL trigger type)
   - Long-running executions

### Common Causes
- Upstream dependency failure (Exit 20)
- Workflow never triggered (Styx scheduler issue)
- Long-running Dataflow job

---

## Missing Natural Triggers

### Symptom
Workflow instances show only AD_HOC triggers, no NATURAL triggers.

### Diagnosis
1. Check workflow configuration:
   ```
   mcp__dataplatform__styx_get_workflow(
     component_id="<component>",
     workflow_id="<workflow>"
   )
   ```

2. Check for recent deployments that may have affected the schedule

### Common Causes
- Workflow was disabled/re-enabled during deployment
- Schedule expression issue
- Styx scheduler temporary outage

### Remediation
Manually trigger backfill for missing dates:
```bash
styx trigger <component> <workflow_id> <partition>
```

---

## Cascading Dependency Failure

### Symptom
Multiple downstream endpoints failing with Exit 20.

### Diagnosis
1. Start from the alerted endpoint
2. Trace upstream via lineage:
   ```
   mcp__dataplatform__lineage_get_upstreams(dataset_id="<endpoint>")
   ```
3. **Also read the workflow source code** — the lineage API only tracks registered
   data endpoints. Internal Luigi task dependencies (e.g., `FeatureStore`,
   `ContentToFilter`) will NOT appear in lineage results. Find the task class
   in code and read its `requires()` method.
4. For each upstream (from BOTH lineage AND code), check status
5. Find ALL workflows that:
   - Have `trigger_complete: false`, OR
   - Failed with exit code != 20, OR
   - Were never triggered

### WrapperTask Pitfall

Many pipelines use Luigi `WrapperTask` classes that aggregate multiple sub-jobs
(e.g., `VectorJob` requires Artist, Album, Track, Episode, etc. vector sub-jobs).
Each sub-job has its OWN dependencies. If ANY sub-job's dependency is missing,
the entire wrapper fails with MISSING_DEPS.

When investigating a WrapperTask failure:
- Identify ALL sub-tasks from the `requires()` method
- Check dependencies for EACH sub-task, not just the one related to your alert
- The actual blocker may be a sub-task unrelated to the alerted downstream

### Remediation
1. Fix ALL root cause workflows (there may be more than one)
2. Verify each completes (`trigger_complete: true`)
3. Verify intermediate outputs actually exist (check BQ tables, GCS files)
4. Only THEN check if downstream workflows are recovering

**Backfill order matters**: Start from upstream, work downstream.

### Verification Checklist
Before concluding a cascading failure is resolved:
- [ ] Every workflow in the chain shows `trigger_complete: true`
- [ ] Output tables/files exist for every intermediate step
- [ ] The final alerted endpoint's workflow is progressing (not still MISSING_DEPS)

---

## Schema Mismatch (Exit 30)

### Symptom
Workflow fails with Exit 30, logs mention schema or field errors.

### Diagnosis
1. Find the workflow definition:
   ```
   mcp__code-search-mcp__search_code(
     query="<task_class> f:*.py",
     repo="<component>"
   )
   ```

2. Check recent commits for schema changes

3. Compare BigQuery table schema with code expectations

### Common Causes
- Field renamed without updating downstream consumers
- Type change (STRING → INT)
- Required field added without backfill

---

## OOM Errors (Exit 137)

### Symptom
Workflow fails with Exit 137.

### Diagnosis
1. Check current resource configuration:
   ```
   mcp__code-search-mcp__search_code(
     query="worker_machine_type f:*.py",
     repo="<component>"
   )
   ```

2. Check Dataflow job metrics for memory usage patterns

### Remediation
Increase resources in one of:
- Kubernetes pod limits (for Styx container)
- Dataflow worker machine type
- Scio job parallelism (reduce to lower memory per worker)

---

## Permission Denied

### Symptom
Logs show 403 Forbidden or Permission denied.

### Diagnosis
1. Get component metadata:
   ```
   mcp__component-metadata-mcp__get_component_id_context(
     componentId="<component>"
   )
   ```

2. Identify service account from response

3. Check required permissions:
   - `roles/dataflow.worker`
   - `roles/storage.objectAdmin`
   - `roles/bigquery.dataEditor`

### Remediation
Grant missing permissions via Terraform or manual IAM update.

---

## Quick Diagnostic Commands

### Check Recent Workflow Runs
```
mcp__dataplatform__styx_get_workflow_instances(
  component_id="<component>",
  workflow_id="<workflow>",
  start="YYYY-MM-DD",
  end="YYYY-MM-DD",
  limit=10
)
```

### Get Workflow Logs
```
mcp__dataplatform__gcp_logs_get_styx_logs(
  styx_pod_name="<pod>",
  execution_date="YYYY-MM-DD"
)
```

### Trace Dependencies
```
mcp__dataplatform__lineage_get_upstreams(dataset_id="<endpoint>")
```

### Check for Errors
```
mcp__cloud-logging-mcp__diagnose_service_errors(
  container="<container>",
  namespace="<namespace>",
  projectId="<gcp-project>"
)
```
