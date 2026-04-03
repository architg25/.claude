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
    "requested_fields": "availability,audience_reach,authorization_groups,content_type,content_authorization_attributes,name,show_uri,episode_type,original_audio,videos",
    "request_metadata": {
      "user_info": {},
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
- `original_audio.uuid` — base64-encoded audio UUID (convert to hex for audiophile/Key2)
- `videos[]` — video file IDs (for video playability checks)

**Note:** `requested_fields` must be a comma-separated string, not an object with `paths`. The `request_metadata.user_info` should be `{}` — dynamo-mcp auto-fills it from the top-level `user_info`.

## show-api — GetShows

```json
{
  "target": "show-api",
  "package": "spotify.metadata.show.v1",
  "service": "ShowApi",
  "method": "GetShows",
  "payload": {
    "show_uris": [{ "uri": "spotify:show:XXXX" }],
    "requested_fields": "availability,audience_reach,authorization_groups,content_type,content_authorization_attributes,name,show_types,available_episode_count",
    "request_metadata": {
      "user_info": {},
      "component_id": "diagnose-entity-availability"
    }
  },
  "user_info": { "username": "<username>" }
}
```

**Key response fields:** Same as episode-api, plus:

- `show_types[]` — ORIGINAL, EXCLUSIVE, ADAPTATION
- `available_episode_count` (int)
