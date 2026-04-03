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

## Key2 Playability Deep Dive

_Sourced from [refused/skills/playability-debug](https://ghe.spotify.net/refused/skills) — adapted for dynamo-mcp (no CLI tools needed)._

Use `dynamo_discover` to find key2 services and methods. Key2 exposes:

- `AudioKeyService` — `GetKey`, `GetLicenseKey`, `IsPlayable`
- `VideoKeyService` — `GetKey`, `IsPlayable`
- `DebugService` — `Audio` (restrictions by hex file_id), `Video` (restrictions by hex source_id)

### Denial Reasons

| Reason                   | Description                                                                       |
| ------------------------ | --------------------------------------------------------------------------------- |
| `COUNTRY_BLOCKED`        | Entire country blocked from content                                               |
| `SALE_PERIOD`            | Outside active sale periods, or catalogue/country combo doesn't match             |
| `FORMAT`                 | Audio format not allowed for subscription tier (e.g., OGG_VORBIS_320 for free)    |
| `FORMAT_LOSSLESS`        | Lossless format (FLAC) over insecure connection or without LOSSLESS audio quality |
| `ABROAD`                 | Free/mod user outside home country                                                |
| `DOWNLOAD_MUSIC_ON_FREE` | Free user attempting music download                                               |
| `SUSPECTED_BOOTLEGGER`   | Bootleg client detected (98% rejection rate)                                      |
| `CONTENT_CONTROL`        | Content Control Library denies access based on authorization attributes           |

### Authenticated Playability Check Flow (in order)

1. Check if country is completely blocked
2. If user has `catalogue="all"` or prerelease access → automatically playable
3. Check bootlegger status (free tier only, from Memcache)
4. Validate sale periods match (user's catalogue + country)
5. Check authorization groups via Casys (for purchased/gated content)
6. Validate file format allowed for subscription tier
7. Check abroad policy (free users must match home country)
8. Check offline download permission (free users)
9. Apply Content Control rules

### Unauthenticated Playability Check Flow

1. Check country not blocked
2. Use `catalogue="free"` and geo-country
3. Only AUDIO_EPISODE content type allowed
4. Check format (no premium/lossless)
5. Validate `allow_unauthenticated` flag

### Format Restrictions

| Category     | Formats                                              | Restriction                                   |
| ------------ | ---------------------------------------------------- | --------------------------------------------- |
| CENC (EME)   | MP4_128, MP4_256, MP4_FLAC, MP4_HE_AAC_V1_64/96      | Must use LICENSE_KEY endpoint                 |
| Premium-only | OGG_VORBIS_320, MP4_256, MP4_256_DUAL, MP4_256_CBCS  | Premium users only                            |
| Lossless     | FLAC_FLAC, FLAC_FLAC_24BIT, MP4_FLAC, MP4_FLAC_24BIT | LOSSLESS or VERY_HIGH tier; secure connection |
| Free tier    | Bitrate <= 96kbps                                    | Free users limited to low quality             |

### DRM Architecture

All DRM services are stateless proxies over Key2:

```
Client → Edge → DRM Service → Key2 (key + playability) → DRM Response → Client
Non-CENC: Client → PlayPlay → Key2 (returns obfuscated key)
```

| DRM Service       | Platforms           | Key Issues to Check                                         |
| ----------------- | ------------------- | ----------------------------------------------------------- |
| PlayPlay          | Non-CENC (OGG etc.) | Token denylist, bootleg detection, lossless client profiles |
| Widevine License  | Android, Chrome     | Compromised CDM blocking, audio denylist, VMP enforcement   |
| FairPlay License  | iOS, Safari         | Certificate versioning (legacy vs v26), protocol fallback   |
| PlayReady License | Xbox, LG, Windows   | Audio client lockdown (specific client IDs only)            |
| Director          | Video manifests     | Calls Key2 for playability, noauth endpoint skips checks    |

### DRM Error Mapping from Key2

| Key2 Status  | HTTP | Meaning                                       |
| ------------ | ---- | --------------------------------------------- |
| OK           | 200  | Key served, license generated                 |
| RATE_LIMITED | 429  | Rate limit exceeded                           |
| BAD_REQUEST  | 400  | Invalid content/file ID                       |
| FORBIDDEN    | 403  | GRM denied (country, catalogue, format, etc.) |
| NOT_FOUND    | 404  | Content key not in Key2                       |

### Key Behavioral Notes

- Key2 **never returns 404** — always serves a fallback dead key (`deadbeefdeadbeefdeadbeefdeadbeef`)
- Debug endpoints return **timestamps** of last restriction update — use to detect propagation delays
- Bootlegger detection combines: client ID spoofing, missing client-token, TLS fingerprint mismatch
- Employee users with `catalogue="all"` bypass most restrictions
- Trial users may appear as premium but have different effective catalogue — check trial flags

### Common Key2 Scenarios

**Metadata ↔ Key2 Desync:** Metadata shows available but Key2 denies (or vice versa). Compare restriction timestamps in DebugService response — stale timestamps = propagation delay.

**Content Replacement:** Track/episode re-linked to new audio_id/source_id, Key2 still has restrictions for old file. Symptoms: metadata correct, Key2 debug shows stale data or unknown file_id.

**Client Caching Stale Data:** Server-side checks pass but user can't play. Client may cache old file IDs or playability responses. Ask user to clear cache, reinstall, or test on different device.

**Trial Users Appearing as Premium:** Certain trial types cause `catalogue=free` users to appear as premium. Check user account attributes for trial flags (e.g., `on-demand-trial`).

### Rate Limiting Buckets

| Bucket                            | Capacity | Fill Rate |
| --------------------------------- | -------- | --------- |
| interactive (normal)              | 300      | 0.3/s     |
| interactive-strictness_low        | 200      | 0.2/s     |
| interactive-strictness_medium     | 100      | 0.1/s     |
| interactive-strictness_high       | 30       | 0.03/s    |
| interactive-suspected_compromised | 30       | 0.001/s   |
| download                          | 10000    | 0.46/s    |
