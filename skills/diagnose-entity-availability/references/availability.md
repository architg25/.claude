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
