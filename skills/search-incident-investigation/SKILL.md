---
name: search-incident-investigation
description: Investigates incidents on Spotify Search backend services (search-api, search-influence, searchrank, etc.). Use when (1) investigating a PagerDuty alert for a Search service, (2) tracing service dependency issues in the searchrank ecosystem, (3) determining root cause of latency/error-rate spikes, (4) finding relevant runbooks and past incidents, or (5) generating remediation suggestions. NOT for data pipeline/endpoint incidents (use data-endpoint-investigation instead).
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - mcp__o11y-agg-mcp__list_alerts
  - mcp__o11y-agg-mcp__get_alert
  - mcp__o11y-agg-mcp__get_alert_timeline
  - mcp__o11y-agg-mcp__list_incidents
  - mcp__o11y-agg-mcp__get_incident
  - mcp__o11y-agg-mcp__get_incident_timeline
  - mcp__o11y-agg-mcp__query_metrics
  - mcp__o11y-agg-mcp__query_range_metrics
  - mcp__o11y-agg-mcp__list_slos
  - mcp__o11y-agg-mcp__get_slo
  - mcp__o11y-agg-mcp__list_dashboards
  - mcp__o11y-agg-mcp__get_dashboard
  - mcp__o11y-agg-mcp__get_service_dependencies
  - mcp__o11y-agg-mcp__get_enriched_dependencies
  - mcp__o11y-agg-mcp__search_traces
  - mcp__o11y-agg-mcp__list_trace_services
  - mcp__o11y-agg-mcp__list_component_operations
  - mcp__o11y-agg-mcp__get_component_overview
  - mcp__o11y-agg-mcp__get_component_metadata
  - mcp__o11y-agg-mcp__get_deployment_history
  - mcp__o11y-agg-mcp__list_gcp_incidents
  - mcp__cloud-logging-mcp__diagnose_service_errors
  - mcp__cloud-logging-mcp__get_error_count
  - mcp__deployments-mcp__get_pod_errors
  - mcp__deployments-mcp__get_deployment_summary
  - mcp__grodor-mcp__list_resources
  - mcp__grodor-mcp__list_resources_batch
  - mcp__component-metadata-mcp__get_component_id_context
  - mcp__aika-search-mcp__spotify_internal_search
  - mcp__code-search-mcp__search_code
  - mcp__code-search-mcp__read_file
  - mcp__atlassian-mcp__search_issues_advanced
  - mcp__google-drive-mcp__list_drive_files
  - mcp__google-drive-mcp__get_document_preview
  - mcp__google-drive-mcp__get_document_structure
  - mcp__google-drive-mcp__get_document_section
---

# Search Incident Investigation

Systematic investigation of incidents on Spotify Search backend services using MCP tools.

## Quick Start

For a quick investigation, use these MCP tools in order:

### 1. Get Service Overview
```
mcp__o11y-agg-mcp__get_component_overview(
  component="<service>",
  includeResources=["RESOURCE_TYPE_ALERTS", "RESOURCE_TYPE_INCIDENTS", "RESOURCE_TYPE_SLOS"]
)
```
Returns: alerts, incidents, SLOs, and metadata for the service.

### 2. Check Alerts and Recent Deployments
```
mcp__o11y-agg-mcp__list_alerts(component="<service>", states=["ALERT_STATE_FIRING"])
mcp__o11y-agg-mcp__get_deployment_history(component="<service>", limit=5)
```

### 3. Check Dependencies
```
mcp__o11y-agg-mcp__get_enriched_dependencies(
  component="<service>",
  includeAlerts=true,
  includeMetrics=true,
  includeDeployments=true,
  lookbackHours=6
)
```
Returns: dependency health with alerts, metrics, and recent deployments.

### 4. Get Logs for Root Cause
```
mcp__component-metadata-mcp__get_component_id_context(componentId="<service>")
```
Use the returned `projectId` and `namespace` in:
```
mcp__cloud-logging-mcp__diagnose_service_errors(
  projectId="<from_above>",
  namespace="<from_above>",
  container="<service>",
  hours=3,
  limit=5
)
```

## Input Parsing

### PagerDuty URL
Extract the incident ID from URLs like `https://spotify.pagerduty.com/incidents/PXXXXXX`:
```
mcp__o11y-agg-mcp__get_incident(incidentId="PXXXXXX")
```
The response contains the affected service name and alert details.

### Alert Name
If given an alert name, search for it:
```
mcp__o11y-agg-mcp__list_alerts(component="<service>")
```
Match the alert by name in the results.

### Direct Service Name
If given a service name directly (e.g., "search-influence is down"), use the service name as the `component` parameter in MCP tool calls.

## Investigation Workflow

### Phase 0: Context Extraction

From the user's input, extract:
- **Service name** (e.g., `search-influence`, `searchrank`, `search-api`)
- **Alert type** (latency, error rate, pod health, OOM, timeout)
- **Incident ID** (if PagerDuty URL provided)

Determine the service's on-call rotation. See [service-catalog.md](service-catalog.md) for rotation mappings.

### Phase 1: Quick Health Assessment

Run these in parallel:

1. **Component overview**: `get_component_overview` with alerts, incidents, and SLOs
2. **Firing alerts**: `list_alerts` with `states=["ALERT_STATE_FIRING"]`
3. **Recent deployments**: `get_deployment_history` with `limit=5`
4. **Pod errors**: `get_pod_errors` for infrastructure issues

**What to look for**:
- Correlated alerts on the same or related services
- Recent deployments that correlate with the alert start time
- Pods in CrashLoopBackOff, OOMKilled, or ImagePullBackOff states
- SLO error budget exhaustion

### Phase 2: Dependency Analysis

Use `get_enriched_dependencies` with `includeAlerts=true`, `includeMetrics=true`, `includeDeployments=true`.

**Searchrank ecosystem special handling**: See [alert-patterns.md](alert-patterns.md) for escalation rules. Key rule: if `search-influence` is alerting, check `searchrank` services **first** before investigating search-influence itself.

Identify which dependencies are unhealthy and whether the issue is:
- **Upstream**: A dependency is failing, causing cascading failures
- **Self-inflicted**: The service itself is the root cause (e.g., bad deployment, resource exhaustion)
- **Platform**: GCP infrastructure issue affecting multiple services

### Phase 3: Deep Investigation

For the suspected root cause service:

1. **Get component metadata** for GCP project/namespace:
   ```
   mcp__component-metadata-mcp__get_component_id_context(componentId="<service>")
   ```

2. **Search for errors** (stack traces, exceptions):
   ```
   mcp__cloud-logging-mcp__diagnose_service_errors(
     projectId="<projectId>",
     namespace="<namespace>",
     container="<service>",
     hours=3,
     limit=5
   )
   ```

3. **Search traces** for errors:
   ```
   mcp__o11y-agg-mcp__search_traces(
     component="<service>",
     errorOnly=true,
     limit=10,
     timeRange={"lookbackHours": 3}
   )
   ```

4. **Check SLO status**:
   ```
   mcp__o11y-agg-mcp__list_slos(component="<service>", includeErrorBudget=true)
   ```

5. **Check GCP incidents** (platform-level issues):
   ```
   mcp__o11y-agg-mcp__list_gcp_incidents(component="<service>")
   ```

### Phase 4: Runbook Retrieval

Retrieve the runbook for the root cause service:

**Primary method** (direct read):
```
mcp__code-search-mcp__read_file("docs/runbook.md", "search-platform/<service>")
```

**Variant paths** (some services use different names):
- `docs/on_call_runbook.md` (search-brain)
- `docs/goalie_runbook.md` (search-brain)

**Fallback** (search techdocs):
```
mcp__aika-search-mcp__spotify_internal_search(
  query="<service> runbook alert",
  data_source="techdocs"
)
```

**Central runbook index**:
```
mcp__code-search-mcp__read_file(
  "docs/operations/on-call-runbooks.md",
  "search-platform/search-documentation"
)
```

Extract alert-specific troubleshooting steps from the runbook and include them in the report.

### Phase 5: Historical Context

Search for past incidents and discussions:

**JIRA search** (past incidents):
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query="project = SEARCH AND type = Incident AND text ~ \"<service>\" ORDER BY created DESC",
  max_results=5
)
```

**Slack search** (past discussions):
```
mcp__aika-search-mcp__spotify_internal_search(
  query="<service> incident <alert_type>",
  data_source="slack"
)
```

**Google Drive search** (past incident reviews):
```
mcp__google-drive-mcp__list_drive_files(
  query="incident review <service>"
)
```

If results are found, preview the most relevant ones:
```
mcp__google-drive-mcp__get_document_preview(fileId="<doc_id>")
```

For detailed review content, get the document structure and read key sections (Summary, Timeline, Root Cause/Why, Remediations):
```
mcp__google-drive-mcp__get_document_structure(fileId="<doc_id>")
mcp__google-drive-mcp__get_document_section(fileId="<doc_id>", sectionIds=["<relevant_section_ids>"])
```

**Effective search queries for Google Drive**:
- `"incident review <service>"` — find reviews for a specific service
- `"INCIDENT-XXXXX"` — find docs for a specific incident number
- `"incident review searchrank"` — searchrank-specific reviews

Include relevant past incidents in the report if they match the current symptoms.

### Phase 6: Check if the Problem is Self-Resolving

Before generating the report, check whether the incident is **already recovering** by analyzing metric trends.

#### Step 1: Check Error Rate Trend

**MCP: Query error rate trend over recent window**
```
mcp__o11y-agg-mcp__query_range_metrics(
  query="rate(grpc_server_handled_total{grpc_code!='OK', service='<service>'}[5m]) / rate(grpc_server_handled_total{service='<service>'}[5m])",
  start="<15_min_ago_ISO>",
  end="<now_ISO>",
  step="5m"
)
```

- **Decreasing toward baseline** → Self-resolving
- **Plateaued at elevated level** → Stabilized but not recovering
- **Still increasing** → Getting worse

**Note**: Service-specific metric names vary. If the above query returns no data, look up the service's dashboards dynamically:
```
mcp__o11y-agg-mcp__list_dashboards(component="<service>")
mcp__o11y-agg-mcp__get_dashboard(component="<service>", dashboardId="<id>")
```
Extract the actual PromQL queries from the dashboard panels.

#### Step 2: Check Latency Trend

**MCP: Query P99 latency trend**
```
mcp__o11y-agg-mcp__query_range_metrics(
  query="histogram_quantile(0.99, rate(grpc_server_handling_seconds_bucket{service='<service>'}[5m]))",
  start="<15_min_ago_ISO>",
  end="<now_ISO>",
  step="5m"
)
```

- **Returning toward pre-incident baseline** → Recovering
- **Flat at elevated level** → Not recovering

#### Step 3: Check Alert Timeline

**MCP: Check if the alert is transitioning toward resolution**
```
mcp__o11y-agg-mcp__get_alert_timeline(alertId="<alert_id>", hoursBack=2)
```

Check if the alert has transitioned from FIRING → PENDING or RESOLVED. Alert auto-resolution is a strong signal.

#### Step 4: Check for Deployment Rollback

**MCP: Check if a rollback deployment correlates with recovery**
```
mcp__o11y-agg-mcp__get_deployment_history(component="<service>", limit=5)
```

If a recent deployment correlated with the incident start AND a subsequent rollback deployment is visible, the fix is likely in progress.

#### Decision Framework

```
Check error rate and latency trends (over a recent window):
├── Both decreasing → LIKELY SELF-RESOLVING
│   ├── Recent rollback visible? → HIGH CONFIDENCE (deployment fix)
│   ├── Dependency alerts resolving? → HIGH CONFIDENCE (upstream recovering)
│   └── No obvious cause? → Continue monitoring
├── Error rate decreasing, latency stable → PARTIALLY RECOVERING
│   └── May need more time; monitor
├── Both flat at elevated levels → STALLED
│   └── Intervention likely needed
└── Either increasing → NOT SELF-RESOLVING
    └── Active investigation needed
```

If **LIKELY SELF-RESOLVING** or **HIGH CONFIDENCE**: Report that the incident appears to be recovering and recommend monitoring rather than active remediation. Include the metric trend data in the report.

### Phase 7: Report Generation

Generate a structured investigation report. See the agent definition for the full output template.

### Phase 8: Incident Review Generation (Optional)

After generating the investigation report, offer to generate a pre-filled incident review markdown file. This phase is **optional** — only proceed if the user requests it.

**Output**: A markdown file at `/tmp/incident-review-INCIDENT-XXXXX.md` following the PZN 5Ys template structure.

The user can then:
- Convert it to a Google Doc using the `google-docs` skill: `python ~/.claude/skills/google-docs/scripts/gdocs.py create /tmp/incident-review-INCIDENT-XXXXX.md --name "INCIDENT-XXXXX / PZN / JAM / WDYM / <summary>"`
- Manually copy the content into a duplicated PZN template doc
- Use it as-is for internal reference

**INCIDENT-XXXXX IDs**: These are Jira ticket numbers from the **INCIDENT** project. They are typically created via `/jeli open` in any Slack channel, which auto-creates the Jira ticket and a dedicated `#incident-XXXXX` Slack channel. See [service-catalog.md](service-catalog.md) for details.

**Template structure** (PZN 5Ys format):

```markdown
# INCIDENT-XXXXX / PZN / JAM / WDYM / <incident summary>

## Summary
<One-sentence root cause from Phase 3>

## Description
<3-5 sentence overview of the incident>

## Impact
<Services/features affected from Phase 2 dependency analysis>

## Participants
- <To be filled by the engineer>

## Timeline
All times in UTC.

| Time (UTC) | Event |
|------------|-------|
| <timestamp> | <alert fired / deployment / error spike> |
| ... | ... |

## Graphs
<Insert relevant graphs as images — links are ephemeral>

## Technical Clarification
<Error details, stack traces from Phase 3 logs>

## Why (5 Whys)
<To be filled during the review meeting>

## Learnings
<To be filled during the review meeting>

## Suggested Actions
<To be filled during the review meeting>

## Selected Actions

### Stop-work
<Must have an owner who was a participant>

### Backlog
<Lower priority items>
```

**Sections to pre-fill from investigation data**:
- **Summary**: One-sentence root cause from Phase 3
- **Description**: Brief overview synthesized from the investigation report
- **Impact**: Services/features affected from Phase 2 dependency analysis
- **Timeline**: Key timestamps from alert timeline and deployment history
- **Technical Clarification**: Error details, stack traces from Phase 3 logs

**Sections to leave for the review meeting**:
- Participants (partially — add the investigating engineer)
- Graphs (requires manual screenshot insertion)
- Why (5 Whys)
- Learnings
- Suggested Actions / Selected Actions

**Important**: The generated markdown is a starting point. The engineer must review and edit it before the 5Ys review meeting. Always inform the user that the pre-filled content needs human review.

**Reference templates**:
- Primary PZN 5Ys: https://docs.google.com/document/d/1LyI7-mx7gHggW968OZK6bXCoThdP280E8U3Uze-5qZk/edit
- Search PA/WDYM variant: https://docs.google.com/document/d/1AD7em9sISTDXFWWklsmc6XEKEDq9tvH6IgR8WtTjWqE/edit

## Remediation Guidance

### Common Remediation Actions

| Symptom | Potential Remediation | Evidence Needed |
|---------|----------------------|-----------------|
| Recent deployment correlates with error spike | Rollback deployment | Deployment timestamp vs alert start time |
| OOMKilled pods | Increase memory limits | Pod events showing OOMKilled |
| High latency from dependency | Check dependency health, scale if needed | Trace data showing slow dependency calls |
| CrashLoopBackOff | Check logs for startup errors | Pod events and container logs |
| GCP incident active | Wait for GCP resolution, consider failover | GCP incident details |
| GCP incident active, single region | Podlink traffic to healthy region | See Podlinking section below; check runbook first |
| Error rate spike without deployment | Check for traffic spike, upstream changes | Metrics showing traffic patterns |

**IMPORTANT**: Never auto-execute remediation actions. Always provide commands/steps for the user to execute manually.

### Podlinking (Traffic Redirection)

Podlinking routes all traffic for a service from one GCP region (pod) to another. Use when a service is degraded in one region with no quick fix.

#### Before Podlinking: Check the Runbook

**IMPORTANT**: Always check the service's runbook first. Some services explicitly discourage podlinking.

```
mcp__code-search-mcp__read_file("docs/runbook.md", "search-platform/<service>")
```

Search the runbook content for "podlink". If the runbook discourages podlinking, follow the runbook's guidance instead.

#### When to Podlink

**Valid scenarios (if runbook does not prohibit):**
- Service degradation isolated to one region with no quick fix available
- Regional GCP infrastructure issues
- Deployment issues affecting a specific region
- Company-wide incidents with ATC guidance

**When NOT to podlink:**
- Very large services (can saturate inter-region network quotas)
- Services with cross-region data dependencies (replication lag issues)
- During multi-region issues
- Without verifying target region capacity

#### Pre-Checks (Critical)

1. **Verify target region capacity**: CPU utilization should have significant headroom — the target region will absorb roughly double the traffic. Check HPA status: current replicas vs max replicas (need significant headroom). Check memory utilization.

2. **Pre-scale target region** if headroom is insufficient:
   ```bash
   # For Gantry-managed services
   bazel run //gantry/gantryctl -- scale <project> <service> --min=<N> --max=<M> --cpu=80
   ```

3. **Check for existing podlinks**: Verify no conflicting podlinks exist

4. **Check network quotas**: For large services, verify inter-region egress quota has headroom

#### Execution Steps

1. Navigate to service's Backstage page → "Podlinks" under "Operation"
2. Select the appropriate protocol tab (grpc, hm, http)
3. **Apply podlink for ALL protocols the service uses** (common mistake: only doing one)
4. In the REGION column, find the problematic region
5. Set the REDIRECT column to the target healthy region
6. Wait 2-5 minutes for propagation
7. Verify traffic shift in dashboards

#### Post-Podlink Monitoring

**Immediate (0-5 minutes):**
- Confirm source region traffic → 0 RPS
- Confirm target region RPS increase
- Check error rates in target region
- Expect some latency increase (cross-region)

**Ongoing:**
- CPU/Memory utilization in target region
- HPA scaling behavior
- Network egress quotas
- Downstream service impacts

#### Risks

1. **Inter-region network quota saturation**: Large services can consume the entire egress quota, impacting ALL services in the corridor
2. **Lingering traffic (edge-proxy)**: Services exposed via edge-proxy can retain stale instances. Fix: redeploy the service after removing the podlink
3. **Cascading failures**: Target region overload can cascade to downstream services
4. **HPA may be too slow**: HPA often cannot scale fast enough for a sudden 2x traffic increase. Pre-scaling is essential

#### Reverting

- Remove podlinks as soon as the underlying issue is resolved
- For edge-proxy services: redeploy after removing podlink to clear stale instances
- Monitor source region metrics after revert to confirm healthy

#### Podlinking Support

- #fabric (Slack) — Podlinks support
- #alf (Slack) — Capacity and quota monitoring
- https://backstage.spotify.net/docs/default/component/service-discovery/overview/podlinks/ — Podlinks documentation

## Related Skills

- [service-catalog.md](service-catalog.md) - On-call rotations, service dependencies, runbook paths
- [alert-patterns.md](alert-patterns.md) - Common alerts, root causes, searchrank escalation rules
