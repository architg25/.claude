# Search Service Catalog

On-call rotations, service dependencies, runbook locations, and escalation channels for Spotify Search backend services.

## On-Call Rotations

| Rotation | Focus Area | Services |
|----------|------------|----------|
| **A: Orchestration & Destination** | Query orchestration, search results | search-api, search-influence, swiper, collector |
| **B: Ranking & Suggestions** | ML ranking, autocomplete, suggestions | searchrank, searchrank-features, searchrank-feature-store, searchrank-gen-recs, search-freetier, search-nlp, search-autocomplete, search-quespa |
| **C: Voice & Browse** | Voice search, browse experience | voice, browse-graphql, bowser, yoshi |
| **D: Retrieval** | Candidate retrieval, personalization | search-override, search-sparse, search-personal-retrieval, personal-search, search-offline-candidates, search-wasp, searchrecs, search-brain |

## Dependency Chain

### Critical Path (Query Flow)

```
Clients (Mobile/Desktop/Web)
    |
    v
searchview (80% of traffic)
    |
    v
search-api (Critical Tier 1 service)
    |
    v
search-influence (Orchestration layer - Rotation A)
    |                               \
    v                                v
searchrank (ML ranking)       [Candidate sources]
    |                          search-wasp
    v                          search-sparse
searchrank-features            search-personal-retrieval
    |                          search-override
    v                          search-brain
searchrank-feature-store
```

### Key Dependency Rules

1. **search-influence depends on searchrank** - This is a **mandatory** dependency. search-influence cannot function without ranking scores from searchrank. There is no fallback.
2. **search-api has a fallback** when search-influence is unavailable, but performance degrades significantly.
3. **searchrank depends on searchrank-features** for feature extraction, which depends on **searchrank-feature-store** for feature storage.

### Implication for Incident Investigation

When `search-influence` alerts fire, the root cause is **more often in searchrank** than in search-influence itself. Always investigate downstream before blaming the alerting service.

## Runbook Locations

| Service | Runbook Path | Retrieval Command |
|---------|-------------|-------------------|
| search-api | `docs/runbook.md` | `mcp__code-search-mcp__read_file("docs/runbook.md", "search-platform/search-api")` |
| search-influence | `docs/runbook.md` | `mcp__code-search-mcp__read_file("docs/runbook.md", "search-platform/search-influence")` |
| searchrank | `docs/runbook.md` | `mcp__code-search-mcp__read_file("docs/runbook.md", "search-platform/searchrank-service")` |
| searchrank-features | `docs/runbook.md` | `mcp__code-search-mcp__read_file("docs/runbook.md", "search-platform/searchrank-features")` |
| search-override | `docs/runbook.md` | `mcp__code-search-mcp__read_file("docs/runbook.md", "search-platform/search-override")` |
| search-brain | `docs/on_call_runbook.md` | `mcp__code-search-mcp__read_file("docs/on_call_runbook.md", "search-platform/search-brain")` |
| search-brain (goalie) | `docs/goalie_runbook.md` | `mcp__code-search-mcp__read_file("docs/goalie_runbook.md", "search-platform/search-brain")` |

### Central Runbook Index

The central index of all Search on-call runbooks:
```
mcp__code-search-mcp__read_file("docs/operations/on-call-runbooks.md", "search-platform/search-documentation")
```

### Runbook Fallback Search

If the standard path doesn't work:
```
mcp__code-search-mcp__search_code("f:runbook r:search-platform/<service>")
```

Or via techdocs:
```
mcp__aika-search-mcp__spotify_internal_search(query="<service> runbook", data_source="techdocs")
```

## Slack Channels

| Channel | Purpose |
|---------|---------|
| #search-oncall | Primary on-call channel for all Search incidents |
| #search-support | General search infrastructure support |
| #search-dvalin | Vespa operations and Vespacito |
| #search-donatello | Ratatoskr/indexing support |
| #search-golden-path | Golden Path questions |

## Incident IDs and Review Process

### INCIDENT-XXXXX Numbers
INCIDENT-XXXXX IDs are sequential Jira ticket numbers from the **INCIDENT** project.

**Primary creation method**: `/jeli open` in any Slack channel
- Opens a form to select incident type, name, and severity
- Creates an INCIDENT ticket in Jira automatically
- Creates a dedicated Slack channel `#incident-XXXXX`

**Secondary methods**: Manual creation in the INCIDENT Jira project, or programmatic creation by monitoring systems.

**IMOC (Incident Management On-Call)**: Coordinates complex incidents. IMOC L1 must acknowledge within 30 minutes.
- IMOC docs: https://backstage.spotify.net/docs/default/component/imoc-docs/
- IMOC Handbook: https://backstage.spotify.net/docs/default/component/imoc-docs/handbook/handbook/

### Incident Review Process
After an incident is resolved, an incident review (5Ys) should be conducted using the PZN template.

**PZN-OOPS** manages the incident review process:
- Slack: `#pzn-oops`
- Offers facilitation help for 5Ys methodology
- `#pzn-tech` for finding experienced facilitators for S0 incidents

### Incident Review Templates
- Primary PZN 5Ys: https://docs.google.com/document/d/1LyI7-mx7gHggW968OZK6bXCoThdP280E8U3Uze-5qZk/edit
- Search PA/WDYM variant: https://docs.google.com/document/d/1AD7em9sISTDXFWWklsmc6XEKEDq9tvH6IgR8WtTjWqE/edit

### Shared Incident Review Folders
- https://drive.google.com/drive/folders/1FmXHb7NOstWHWE4nTkJcFZ_ZAih1X39n
- https://drive.google.com/drive/folders/1zlCxinDWi7alAP8p3Y7saWojBASc99-W

## Component Metadata Lookup

Always look up GCP project IDs and namespaces dynamically rather than hardcoding:
```
mcp__component-metadata-mcp__get_component_id_context(componentId="<service>")
```
This returns the `projectId`, `namespace`, and other deployment details needed for log queries.
