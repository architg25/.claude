# episode-api & show-api Reference

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
