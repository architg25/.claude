# casys & Access Context Reference

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

## casys — CheckWithoutCapping

For audiobooks, also call:

```json
{
  "target": "casys",
  "package": "spotify.casys.api.v1",
  "service": "Cas",
  "method": "CheckWithoutCapping",
  "payload": {
    "user_id": "<user_id>",
    "groups": [
      { "namespace": "PODCAST_PAYWALL", "group_identifier": "<group_id>" },
      { "namespace": "CONTENT_LINK", "group_identifier": "<group_id>" }
    ]
  }
}
```

**Key response fields:**

- `statuses[].status` — `member {}` (allowed) or `not_member {reason: CONSUMPTION_CAPPED}` (blocked)
- `statuses[].group` — which group this status is for

## Authorization Group Namespaces

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

## entity-access-context-api — GetManyEntityAccessContext

Entity-only (no user):

```json
{
  "target": "entity-access-information-system",
  "package": "spotify.entityaccesscontextapi.v1",
  "service": "EntityAccessContextApi",
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

## podcast-subscription-extension

Use `dynamo_discover` to find podcast-subscription-extension. This service provides paywall/subscription context for podcast episodes.

**Key response fields:**

- `is_paywalled` (bool) — whether the episode is behind a paywall
- `is_user_subscribed` (bool) — whether the user has an active subscription to the show
- `explanation.type` — reason for the access decision
- `signifier` — display hint for client UI (e.g., padlock icon)
