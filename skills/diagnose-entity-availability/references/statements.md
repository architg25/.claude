# statements Reference

## statements — GetEntity

Use `dynamo_discover` to find the exact package/service first, as Statements exposes multiple services.

```json
{
  "target": "statements",
  "package": "spotify.statements.v2",
  "service": "Statements",
  "method": "GetEntity",
  "payload": {
    "uri": "spotify:episode:XXXX"
  }
}
```

**Key response fields:**

- `salePeriod[]` — market + catalogue restrictions with time windows
- `segmentBlockPeriod[]` — content toggling blocks
- `regionalBlock[]` — policy-based market blocks
- `takenDown` (bool)
- `unpublished` (bool)
- `validity` (bool) — transcoded media exists, non-empty title
- `authorizationInfo.is_paywall_content` (bool)
- `authorizationInfo.grants[]` — market + Casys group requirements
- `isGatedContent` (bool)
- `isEmployeeOnly` (bool)
- `entityLifecycle` — lifecycle state
- `audioRelation` / `audioRelationPending` — transcoding status
- `computedSalePeriods[]` — pre-computed by time/country/catalog
