---
name: diagnose-entity-availability
description: Use when a user reports an episode, show, or audiobook is not available, not playable, blocked, showing a padlock, has playback errors, or is missing from a market — diagnoses root cause across the availability pipeline using live service calls
allowed-tools:
  - mcp__dynamo-mcp__dynamo_discover
  - mcp__dynamo-mcp__dynamo_call_method
  - Agent
---

# Diagnose Entity Availability

Investigate why an episode, show, or audiobook is unavailable/unplayable. Uses live dynamo-mcp calls and parallel subagent teams.

## When to Use

- "Why can't user X play episode Y?"
- "Episode/show/audiobook not available in market Z"
- "Padlock showing on episode"
- "Metadata says playable but audio won't play"
- "Episode/show not found or missing"
- "Audiobook says listening hours exceeded"
- Any entity availability or playability investigation

## When NOT to Use

- **Music tracks** — different availability system entirely
- **RSS feed / ingestion issues** — see `statements-platform-services/statements-library/docs/operations/debugging-missing-episode-or-show.md`
- **Service outages** — check Grafana/alerts first, this skill diagnoses per-entity issues

## Input Gathering

### Required

- **Entity URI** — `spotify:episode:...`, `spotify:show:...`, `spotify:audiobook:...`, or `spotify:audiobookchapter:...`

### Optional (auto-enrich when provided)

- **User identifier** — user ID, username, or email. Invoke `spotify-user-lookup` to resolve canonical user_id, country, catalogue, and employee status. Do NOT ask the user for country/catalogue separately.
- **Symptom** — if not described, ask: (1) not found, (2) visible but locked, (3) not visible in search, (4) metadata says playable but won't play, (5) not available in market, (6) listening hours exceeded, (7) other.

### URI Rewriting

| Input URI                     | Rewrite To           | API                       |
| ----------------------------- | -------------------- | ------------------------- |
| `spotify:episode:ID`          | (keep)               | episode-api `GetEpisodes` |
| `spotify:show:ID`             | (keep)               | show-api `GetShows`       |
| `spotify:audiobook:ID`        | `spotify:show:ID`    | show-api `GetShows`       |
| `spotify:audiobookchapter:ID` | `spotify:episode:ID` | episode-api `GetEpisodes` |

**CRITICAL: Never assume podcast vs audiobook from the URI.** The triage call's `content_type` is the source of truth (`PODCAST`, `CHAPTER`, `PODCAST_SHORT`, `LESSON`, `USER_HIGHLIGHT`).

## Phase 1: Triage

One call to determine which subagent branches to spawn.

**For episode/audiobookchapter URIs** — call episode-api `GetEpisodes`:

```json
dynamo_call_method:
  target: "episode-api"
  package: "spotify.metadata.episode.v1"
  service: "EpisodeApi"
  method: "GetEpisodes"
  payload: {
    "episode_uris": [{"uri": "<URI>"}],
    "requested_fields": "availability,audience_reach,authorization_groups,content_type,content_authorization_attributes,name,show_uri,episode_type,original_audio,videos",
    "request_metadata": {
      "user_info": {
        "user_id": "<user_id>",
        "market_country_iso": "<country>",
        "catalogue": "<catalogue>",
        "is_employee": false
      },
      "component_id": "diagnose-entity-availability"
    }
  }
  user_info: {"username": "<username>"}
```

**For show/audiobook URIs** — use show-api `GetShows` with `show_uris` instead of `episode_uris`, and add `show_types` and `available_episode_count` to requested fields. No `original_audio`/`videos` for shows.

**If no user context**, default to `market_country_iso: "GB"` and `catalogue: "premium"` in `request_metadata.user_info` (availability only needs market + catalogue, not a real user). Flag to the user that you're using defaults. For user-specific checks (Casys, subscription), a real user identifier is still needed.

**Extract:** `entity_status`, `availability.playability` + `restriction_details`, `availability.visibility`, `audience_reach`, `authorization_groups`, `content_type`, `name`, `original_audio.uuid` (for Key2 checks), `videos` (for video playability).

## Phase 2: Branch Routing

| Triage Result                                 | Subagents (parallel)                                        | Needs User Context? |
| --------------------------------------------- | ----------------------------------------------------------- | ------------------- |
| `NOT_FOUND` / entity missing                  | entity-live-status + Statements                             | No                  |
| `TAKEN_DOWN_FOR_LEGAL_REASONS`                | entity-live-status + Statements                             | No                  |
| `PERMISSION_DENIED` (CCL block)               | entity-live-status + Statements                             | No                  |
| Visible + not playable + `USER_LACKS_ACCESS`  | Casys + podcast-subscription-ext + entity-access-context    | Yes                 |
| Visible + not playable + `CONSUMPTION_CAPPED` | Casys (Check + CheckWithoutCapping) + entity-access-context | Yes                 |
| `COUNTRY_RESTRICTED`                          | entity-live-status + availability-api                       | Partial (market)    |
| `CATALOGUE_RESTRICTED`                        | entity-live-status + availability-api                       | Partial (catalogue) |
| Playable in metadata but audio won't play     | Key2 + entity-live-status                                   | Yes                 |
| Everything looks fine / unclear               | ALL agents                                                  | Best effort         |

If user context is missing for a branch that needs it, run entity-level agents only and tell the user what can't be checked.

## Phase 3: Subagent Dispatch

Dispatch all agents for the selected branch in a **single message** (parallel execution). Each subagent must read the relevant reference file from `~/.claude/skills/diagnose-entity-availability/references/`.

| Agent                 | Reference File                    | Key Checks                                                      |
| --------------------- | --------------------------------- | --------------------------------------------------------------- |
| Casys                 | `references/casys.md`             | Per-group Member/NotMember, CONSUMPTION_CAPPED reason           |
| Podcast-Sub-Ext       | `references/casys.md`             | is_paywalled, is_user_subscribed, explanation type              |
| Entity-Access-Context | `references/casys.md`             | is_gated, access_types, how user could get access               |
| Entity-Live-Status    | `references/availability.md`      | Validation status, live status                                  |
| Availability-API      | `references/availability.md`      | Playability/visibility verdicts, policy decisions               |
| Key2                  | `references/key2-restrictions.md` | Denial reasons, restriction timestamps, format checks           |
| Statements (fallback) | `references/statements.md`        | Entity existence, sale periods, taken_down, validity, auth info |

**Statements is a fallback** — episode-api/show-api triage already surfaces availability, auth groups, and content type. Only dispatch the Statements agent when triage returns NOT_FOUND, TAKEN_DOWN, or when you need raw sale periods/regional blocks that the triage doesn't expose. Statements has strict SA access policies and may be inaccessible.

**Key2 requires audiophile hop** — Key2's IsPlayable/DebugService expects file IDs (20-byte, hex/base64), not the audio UUID from episode-api. Call `audiophile` `DebugService/Audio` with the audio UUID first to get file IDs, then pass those to Key2.

Each subagent prompt should include: entity URI, user context, triage results, content type, and instruct it to read the reference file. Subagents report findings as `{service, status, diagnosis, evidence}`.

## Phase 4: Synthesis

### 1. Root Cause

- "Episode is paywalled (PODCAST_PAYWALL) and user is not a member of group `podcast_paywall:12988357`."
- "Sale periods only include GB, DE, FR — user is in US."
- "Consumption capped — listening hours exceeded this billing period."

### 2. Evidence Chain

- Which service said what, with key field values (e.g., `episode-api: playable=false, verdict=USER_LACKS_ACCESS`).
- Include all subagent results in a compact list.

### 3. Discrepancies

- Metadata says playable but Key2 denies -> propagation delay
- Casys says Member but podcast-sub-ext says not_subscribed -> caching (3-min TTL)
- Entity-access-context says not gated but episode has authorization_groups -> stale aggregation

### 4. Suggested Next Steps

- **Paywall:** User needs to subscribe; unlock method: ANCHOR_PAYWALL
- **Geo-block:** Content restricted to markets [list]; user is in [market]
- **Catalogue:** Requires [premium/free]; user has [catalogue]
- **Capped:** Access exists but listening hours exceeded
- **Propagation delay:** Wait ~30 minutes for Key2 to sync
- **Taken down:** Check Statements for reason
- **Not found:** Check ingestion pipeline (see debugging-missing-episode-or-show.md)
- **Content replacement:** File ID mismatch — Key2 may have stale file mappings
- **DRM layer:** Key2 allows but DRM proxy denies — platform-specific issue
- **Trial user:** Effective catalogue may differ from subscription tier
- **Client caching:** Server-side correct; suggest cache clear / different device
- **Format restriction:** Audio format not allowed for tier (e.g., FLAC requires lossless)

## Gotchas

1. **Legacy `playability` field is visibility** — `Episode.playability` (field 22) only indicates visibility; always use `availability.playability`.
2. **Never assume podcast vs audiobook from URI** — check `content_type` from triage.
3. **URI rewriting required** — `spotify:audiobook:ID` -> `spotify:show:ID`, `spotify:audiobookchapter:ID` -> `spotify:episode:ID`.
4. **Employee override** — employees bypass most restrictions (`catalogue="all"`); warn if target user is employee.
5. **Dual enforcement** — metadata (episode-api) and Key2 resolve playability independently via separate async pipelines; they can disagree.
6. **Consumption capping** — user can be Casys Member but denied due to exceeded hours; use `CheckWithoutCapping` to distinguish.
7. **Casys routing varies by content type** — episode-api uses CasysStrategy for PODCAST/CHAPTER, AvailabilityStrategy for LESSON/USER_HIGHLIGHT.
8. **CCL full authority** — when enabled, CCL (not Casys) is the authority for PLAY decisions; PERMISSION_DENIED likely means CCL.
9. **Propagation delays** — Statements publishes to two pipelines; typical sync is minutes but can lag hours under load.

## Error Handling

- **Service call fails** — report what couldn't be checked, continue with available data.
- **Impersonation fails** — note the gap, suggest explicit `impersonate` parameter.
- **No user context** — run entity-level checks only; state clearly what can't be checked.
- **Truncated response** — dynamo-mcp truncates at 20k chars; note it and work with available data.
