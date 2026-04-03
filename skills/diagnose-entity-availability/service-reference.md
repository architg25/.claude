# Service Reference — Entity Availability Diagnosis

Exact `dynamo_call_method` parameters for each service in the availability pipeline. Subagents: read this file for call templates before making service calls.

## episode-api — GetEpisodes

```json
{
  "target": "episode-api",
  "package": "spotify.metadata.episode.v1",
  "service": "EpisodeApi",
  "method": "GetEpisodes",
  "payload": {
    "episode_uris": [{ "uri": "spotify:episode:XXXX" }],
    "requested_fields": {
      "paths": [
        "availability",
        "playability",
        "audience_reach",
        "authorization_groups",
        "content_type",
        "content_authorization_attributes",
        "name",
        "show_uri",
        "episode_type",
        "duration"
      ]
    },
    "request_metadata": {
      "user_info": {
        "user_id": "<user_id>",
        "market_country_iso": "<country>",
        "catalogue": "<catalogue>",
        "is_employee": false
      },
      "component_id": "diagnose-entity-availability"
    }
  },
  "user_info": { "username": "<username>" }
}
```

**Key response fields:**

- `entity_status`: OK, NOT_FOUND, TAKEN_DOWN_FOR_LEGAL_REASONS, PERMISSION_DENIED
- `availability.playability.is_playable` (bool) — the REAL playability
- `availability.playability.restriction_details[].verdict` — VERDICT_COUNTRY_RESTRICTED, VERDICT_CATALOGUE_RESTRICTED, VERDICT_USER_LACKS_ACCESS, VERDICT_UNAVAILABLE
- `availability.visibility.is_visible` (bool)
- `audience_reach` — AUDIENCE_REACH_PAYWALL if gated
- `authorization_groups[]` — `"namespace:group_id"` strings
- `content_type` — PODCAST, CHAPTER, PODCAST_SHORT, LESSON, USER_HIGHLIGHT

## show-api — GetShows

```json
{
  "target": "show-api",
  "package": "spotify.metadata.show.v1",
  "service": "ShowApi",
  "method": "GetShows",
  "payload": {
    "show_uris": [{ "uri": "spotify:show:XXXX" }],
    "requested_fields": {
      "paths": [
        "availability",
        "playability",
        "audience_reach",
        "authorization_groups",
        "content_type",
        "content_authorization_attributes",
        "name",
        "show_types",
        "available_episode_count"
      ]
    },
    "request_metadata": {
      "user_info": {
        "user_id": "<user_id>",
        "market_country_iso": "<country>",
        "catalogue": "<catalogue>",
        "is_employee": false
      },
      "component_id": "diagnose-entity-availability"
    }
  },
  "user_info": { "username": "<username>" }
}
```

**Key response fields:** Same as episode-api, plus:

- `show_types[]` — ORIGINAL, EXCLUSIVE, ADAPTATION
- `available_episode_count` (int)

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

## casys — Check

Use `dynamo_discover` to find casys first.

```json
{
  "target": "casys",
  "package": "spotify.casys.api.v1",
  "service": "Cas",
  "method": "Check",
  "payload": {
    "user_id": "<user_id>",
    "groups": [
      { "namespace": "PODCAST_PAYWALL", "group_identifier": "<group_id>" },
      { "namespace": "CONTENT_LINK", "group_identifier": "<group_id>" }
    ]
  }
}
```

For audiobooks, also call:

```json
{
  "method": "CheckWithoutCapping",
  "payload": { "...same as Check..." }
}
```

**Key response fields:**

- `statuses[].status` — `member {}` (allowed) or `not_member {reason: CONSUMPTION_CAPPED}` (blocked)
- `statuses[].group` — which group this status is for

**Authorization group namespaces:**

| Namespace                | Content Type                 |
| ------------------------ | ---------------------------- |
| `PODCAST_PAYWALL`        | Anchor paywalled podcasts    |
| `CONTENT_ACTIVATE`       | One-time activation          |
| `CONTENT_LINK`           | Account linking (SOA)        |
| `AUDIOBOOK_DIRECT_SALES` | Purchased audiobooks         |
| `PREMIUM_AUDIOBOOKS`     | Audiobooks in Premium        |
| `AUDIOBOOK_PROMOTION`    | Promotional audiobook access |
| `FEATURE_BUNDLE`         | Tier-gated features          |
| `ENTERPRISE_PODCAST`     | Enterprise/internal          |
| `PERSONAL_CONTENT`       | Personal content             |

## entity-access-context-api — GetManyUserAccessContext

Use `dynamo_discover` to find the service first.

```json
{
  "target": "entity-access-information-system",
  "package": "spotify.entityaccesscontextapi.v1",
  "service": "EntityAccessContextApi",
  "method": "GetManyUserAccessContext",
  "payload": {
    "user": {
      "user_id": "<user_id>",
      "market": "<country>",
      "catalogue": "<catalogue>",
      "is_employee": false
    },
    "entity_uris": ["spotify:episode:XXXX"]
  }
}
```

Entity-only (no user):

```json
{
  "method": "GetManyEntityAccessContext",
  "payload": {
    "entity_uris": ["spotify:episode:XXXX"],
    "market": "<country>"
  }
}
```

**Key response fields:**

- `contexts[].is_gated` (bool)
- `contexts[].access_types[]` — ANCHOR_PAYWALL, OAP_OTP, OAP_LINKING, DIRECT_SALE, SPOTIFY_SUBSCRIPTION, PROMO_CODE, ENTERPRISE

## entity-live-status — GetLiveStatus

Use `dynamo_discover` to find the service first.

```json
{
  "target": "entity-live-status",
  "package": "spotify.entitylivestatus",
  "service": "EntityLiveStatus",
  "method": "GetLiveStatus",
  "payload": {
    "uri": "spotify:episode:XXXX",
    "country_code": "<country>"
  }
}
```

## availability-api — GetAvailabilitiesWithUserInfo

Use `dynamo_discover` to find the service first.

```json
{
  "target": "availability-api",
  "package": "spotify.metadata.availability.v1",
  "service": "AvailabilityApi",
  "method": "GetAvailabilitiesWithUserInfo",
  "payload": {
    "availability_ids": ["<id_from_entity>"],
    "user_info": {
      "user_id": "<user_id>",
      "user_country": "<country>",
      "user_catalogue": "<catalogue>",
      "is_employee": false
    },
    "requested_fields": {
      "paths": ["playability", "visibility", "policy_decisions", "access_info"]
    }
  }
}
```

**Key response fields:**

- `playability.is_playable` (bool)
- `visibility.is_visible` (bool)
- `policy_decisions[].verdict` — VERDICT_COUNTRY_RESTRICTED, VERDICT_CATALOGUE_RESTRICTED, VERDICT_USER_LACKS_ACCESS, VERDICT_UNAVAILABLE
- `access_info`

## key2 — IsPlayable / DebugService

Use `dynamo_discover` to find key2 services and methods. Key2 exposes:

- `AudioKeyService` — `GetKey`, `GetLicenseKey`, `IsPlayable`
- `VideoKeyService` — `GetKey`, `IsPlayable`
- `DebugService` — diagnostic endpoints

Call `IsPlayable` or DebugService endpoints with the entity/file context.

**Key2 denial reasons:**

| Reason                 | Description                         |
| ---------------------- | ----------------------------------- |
| `COUNTRY_BLOCKED`      | Entire country blocked              |
| `SALE_PERIOD`          | Outside active sale periods         |
| `FORMAT`               | Audio format not allowed for tier   |
| `FORMAT_LOSSLESS`      | Lossless without lossless tier      |
| `SUSPECTED_BOOTLEGGER` | Bootleg client (98% rejection)      |
| `CONTENT_CONTROL`      | CCL denies based on auth attributes |
