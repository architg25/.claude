---
name: Data Endpoints
description: Comprehensive tooling for Spotify data endpoints. Use this skill when the user wants to (1) view actual data records from endpoints, (2) get endpoint schema/metadata, (3) check partition status and SLO compliance, (4) view lineage (upstream/downstream dependencies), (5) get a comprehensive overview of an endpoint, or (6) validate output for PII. Supports AVRO, Parquet, and TFRecords formats.
allowed-tools:
  - Bash
  - Read
  - mcp__dataplatform__greg_get_dataset
  - mcp__dataplatform__lineage_get_upstreams
  - mcp__dataplatform__lineage_get_downstreams
  - mcp__dataplatform__styx_get_workflows
  - mcp__dataplatform__styx_get_workflow
  - mcp__dataplatform__styx_get_workflow_instances
  - mcp__dataplatform__data_counters_get_dataset_counters
---

# Data Endpoints

Comprehensive toolkit for working with Spotify data endpoints.

## Important: Use MCP Tools First

**Prefer MCP tools over Python scripts.** The dataplatform MCP tools are more reliable, require no local dependencies, and integrate directly into Claude Code sessions.

| Capability | MCP Tool (Preferred) | Script (Legacy/Unique) |
|------------|---------------------|------------------------|
| Get metadata & schema | `greg_get_dataset` | — |
| Get lineage | `lineage_get_upstreams/downstreams` | — |
| Check workflow status | `styx_get_workflow_instances` | — |
| Check partition status | — | `get_endpoint_status.py` |
| View actual data records | — | `view_endpoint_data.py` |
| Validate no PII in output | — | `validate_no_pii.py` |

## Via MCP Tools (Recommended)

### Get Dataset Metadata & Schema

```
mcp__dataplatform__greg_get_dataset(dataset_id="<endpoint_id>")
```

Returns: owner, description, lifecycle, SLO, retention, schema, storage URI, component ID.

### Get Lineage

```
mcp__dataplatform__lineage_get_upstreams(dataset_id="<endpoint_id>")
mcp__dataplatform__lineage_get_downstreams(dataset_id="<endpoint_id>")
```

Returns: list of upstream/downstream endpoint IDs.

### Get Styx Workflow Status

```
mcp__dataplatform__styx_get_workflow_instances(
  component_id="<component>",
  workflow_id="<workflow>",
  start="YYYY-MM-DD",
  end="YYYY-MM-DD",
  limit=5
)
```

Returns: execution history with triggers, statuses, and exit codes.

### Get All Workflows for Component

```
mcp__dataplatform__styx_get_workflows(component_id="<component>")
```

Returns: all workflows for a component with schedules and Docker images.

## Via Script (Unique Capabilities Only)

These scripts provide capabilities not available via MCP:

### Check Partition Status and SLO Compliance

```bash
python ~/.claude/skills/data-endpoints/scripts/get_endpoint_status.py <endpoint_id>
python ~/.claude/skills/data-endpoints/scripts/get_endpoint_status.py <endpoint_id> --state ERROR
python ~/.claude/skills/data-endpoints/scripts/get_endpoint_status.py <endpoint_id> --from 2025-01-01 --to 2025-01-23
```

### View Data Records

```bash
# View 5 records from most recent partition
python ~/.claude/skills/data-endpoints/scripts/view_endpoint_data.py <endpoint_id>

# With anonymization (ALWAYS use for output)
python ~/.claude/skills/data-endpoints/scripts/view_endpoint_data.py <endpoint_id> --anonymize

# Specific partition and count
python ~/.claude/skills/data-endpoints/scripts/view_endpoint_data.py <endpoint_id> --partition 2025-01-21 --num-records 20
```

### Validate No PII

```bash
python ~/.claude/skills/data-endpoints/scripts/validate_no_pii.py --text "your text here"
python ~/.claude/skills/data-endpoints/scripts/validate_no_pii.py --file path/to/file
```

## Prerequisites (for Scripts)

```bash
# Hades CLI and data viewing tools
brew tap spotify/sptaps git@ghe.spotify.net:shared/homebrew-spotify.git
brew install hades-cli
brew tap spotify/public
brew install gcs-avro-tools gcs-parquet-cli tfreader

# GCP authentication
gcloud auth application-default login
```

**Java Note:** `avro-tools` and `parquet-cli` require Java 17 or earlier. Switch with:
```bash
source ~/.sdkman/bin/sdkman-init.sh && sdk use java 17.0.12-amzn
```

## PII Handling

**ALWAYS use `--anonymize` when viewing data that will be included in output.**

| Data Type | Anonymization |
|-----------|---------------|
| User text | `"sample text N"` |
| Names | `"Test User N"` |
| Email | `"testN@example.com"` |
| Location | `"Test City"`, `"0.0,0.0"` |

**Safe to use as-is:** userId, country codes, language codes, age, Track/album URIs.

## Troubleshooting

### Java Version Errors
```bash
source ~/.sdkman/bin/sdkman-init.sh && sdk use java 17.0.12-amzn
```

### Authentication Issues
```bash
gcloud auth application-default login
```

### Missing Tools
```bash
python ~/.claude/skills/data-endpoints/scripts/view_endpoint_data.py --check-tools <any_endpoint>
```
