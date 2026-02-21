# Alert Patterns and Escalation Rules

Common alert types, typical root causes, and the searchrank ecosystem escalation rules for Spotify Search services.

## Searchrank Alert Escalation Rules

The searchrank ecosystem has a strict dependency chain. When investigating alerts, **always check downstream dependencies before blaming the alerting service**.

### Priority Investigation Order

#### 1. search-influence alert
Check these services **in order** before investigating search-influence itself:
1. **searchrank** health (mandatory dependency - search-influence cannot function without it)
2. **searchrank-features** health (feature extraction for ranking)
3. **searchrank-feature-store** health (feature storage)
4. Only then investigate **search-influence** itself

#### 2. searchrank alert
Check these:
1. **searchrank-features** health (feature extraction)
2. **searchrank-feature-store** health (feature storage)
3. Recent **deployments** to searchrank
4. **Model serving** health (if applicable)

#### 3. search-api alert
Check these:
1. **search-influence** health (ranking orchestration)
2. All **candidate sources** (search-wasp, search-sparse, search-personal-retrieval, search-override, search-brain)
3. **search-api's own** health and recent deployments

#### 4. Any Search service alert
Always check:
1. **GCP platform incidents** (`list_gcp_incidents`) - platform-wide issues affect all services
2. **Recent deployments** (`get_deployment_history`) - correlate deploy time with alert start
3. **Correlated alerts** on other Search services (`list_alerts`) - multiple alerts suggest systemic issue

## Investigation Decision Tree

```
Alert fires for service X
    |
    v
Is X part of searchrank ecosystem?
(search-influence, searchrank, searchrank-features, searchrank-feature-store)
    |                               |
    YES                             NO
    |                               |
    v                               v
Check downstream deps          Check own health first
first (see escalation          (overview, pods, logs)
rules above)                       |
    |                               v
    v                          Check dependencies
Found unhealthy dep?           (get_enriched_dependencies)
    |           |                   |
    YES         NO                  v
    |           |              Found unhealthy dep?
    v           v              |           |
Investigate  Investigate       YES         NO
the dep      X itself          |           |
                               v           v
                           Investigate  Check GCP incidents,
                           the dep      traffic patterns,
                                        recent changes
```

## Common Alert Types

| Alert Category | Typical Symptoms | Common Root Causes | First Check |
|---------------|------------------|-------------------|-------------|
| **Latency spike** | p99/p95 latency exceeds threshold | Dependency slowdown, GCP issue, traffic spike, bad deployment | Dependencies, then deployments |
| **Error rate** | 5xx rate exceeds threshold | Bad deployment, dependency failure, resource exhaustion | Recent deployments, dependency health |
| **Pod health** | CrashLoopBackOff, OOMKilled | Memory leak, config error, bad image | Pod events, container logs |
| **Timeout** | Request timeouts to dependencies | Dependency overloaded, network issue, GCP incident | Dependency health, GCP incidents |
| **SLO breach** | Error budget exhausted | Sustained degradation from any of the above | SLO status, then trace the underlying cause |
| **Traffic anomaly** | Unusual traffic patterns | Client-side issue, bot traffic, upstream routing change | Metrics for traffic volume |

## Alert-to-Root-Cause Mapping

### Latency Alerts

| Alerting Service | Most Likely Root Cause | Investigation Steps |
|-----------------|----------------------|---------------------|
| search-influence | searchrank latency | Check searchrank p99, recent searchrank deploys |
| search-api | search-influence or candidate source latency | Check search-influence, then each candidate source |
| searchrank | searchrank-features or model serving latency | Check feature extraction time, model inference time |

### Error Rate Alerts

| Alerting Service | Most Likely Root Cause | Investigation Steps |
|-----------------|----------------------|---------------------|
| search-influence | searchrank errors/unavailability | Check searchrank error rate and pod health |
| search-api | search-influence unavailability | Check search-influence, fallback activation |
| searchrank | Feature store errors, model errors | Check searchrank-features, feature-store health |

### Pod Health Alerts

| Symptom | Typical Root Cause | Remediation |
|---------|-------------------|-------------|
| OOMKilled | Memory leak or undersized limits | Increase memory limits, investigate leak |
| CrashLoopBackOff | Startup failure, config error, bad deploy | Check logs, rollback if recent deploy |
| ImagePullBackOff | Registry issue, bad image tag | Check image tag, retry, or rollback |
| Pending pods | Resource constraints, node pressure | Check node capacity, resource quotas |

## Historical Pattern Queries

### JIRA Search for Past Incidents
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query="project = SEARCH AND type = Incident AND text ~ \"<service>\" AND text ~ \"<alert_type>\" ORDER BY created DESC",
  max_results=5
)
```

### Slack Search for Past Discussions
```
mcp__aika-search-mcp__spotify_internal_search(
  query="<service> <alert_type> incident",
  data_source="slack"
)
```
