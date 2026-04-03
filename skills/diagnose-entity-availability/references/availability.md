# availability-api & entity-live-status Reference

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

## entity-live-status — GetLiveStatus

Especially useful for `TAKEN_DOWN_FOR_LEGAL_REASONS` and `NOT_FOUND` — gives detailed reasons why an entity is unavailable, which show-api/episode-api don't expose.

```json
{
  "target": "entity-live-status",
  "package": "spotify.entitylivestatus",
  "service": "EntityLiveStatus",
  "method": "GetLiveStatus",
  "payload": {
    "kind": "SHOW",
    "uri": "spotify:show:XXXX",
    "country_code": "<country>"
  }
}
```

**`kind` values:** `SHOW`, `EPISODE`, `AUDIOBOOK`, `AUDIOBOOKCHAPTER`

**Key response fields:**

- `unavailableReasons[]` — list of `{type, description}` entries explaining why the entity is unavailable
  - `VALIDATION` — failed validation (empty name, no cover art, no episodes, no transcoded media, etc.)
  - `UNPUBLISHED` — entity is unpublished
  - `BLOCKED_BY_SALE_PERIOD` — blocked in specific markets/catalogues at current time
  - `RESTRICTED_LIFECYCLE` — restricted for streaming by its lifecycle state
  - `TAKEN_DOWN` — explicitly taken down
- `v4LiveStatus[]` / `v5LiveStatus[]` — which domains have the entity cached
