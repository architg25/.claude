# Key2 Playability Restrictions Reference

_Adapted from refused/skills playability-debug for dynamo-mcp (no CLI tools needed)._

Use `dynamo_discover` to find key2 services and methods. Key2 exposes:

- `AudioKeyService` — `GetKey`, `GetLicenseKey`, `IsPlayable`
- `VideoKeyService` — `GetKey`, `IsPlayable`
- `DebugService` — `Audio` (restrictions by hex file_id), `Video` (restrictions by hex source_id)

## Denial Reasons

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

## Authenticated Playability Check Flow (in order)

1. Check if country is completely blocked
2. If user has `catalogue="all"` or prerelease access -> automatically playable
3. Check bootlegger status (free tier only, from Memcache)
4. Validate sale periods match (user's catalogue + country)
5. Check authorization groups via Casys (for purchased/gated content)
6. Validate file format allowed for subscription tier
7. Check abroad policy (free users must match home country)
8. Check offline download permission (free users)
9. Apply Content Control rules

## Unauthenticated Playability Check Flow

1. Check country not blocked
2. Use `catalogue="free"` and geo-country
3. Only AUDIO_EPISODE content type allowed
4. Check format (no premium/lossless)
5. Validate `allow_unauthenticated` flag

## Format Restrictions

| Category     | Formats                                              | Restriction                                   |
| ------------ | ---------------------------------------------------- | --------------------------------------------- |
| CENC (EME)   | MP4_128, MP4_256, MP4_FLAC, MP4_HE_AAC_V1_64/96      | Must use LICENSE_KEY endpoint                 |
| Premium-only | OGG_VORBIS_320, MP4_256, MP4_256_DUAL, MP4_256_CBCS  | Premium users only                            |
| Lossless     | FLAC_FLAC, FLAC_FLAC_24BIT, MP4_FLAC, MP4_FLAC_24BIT | LOSSLESS or VERY_HIGH tier; secure connection |
| Free tier    | Bitrate <= 96kbps                                    | Free users limited to low quality             |

## Sale Period Matching Pseudocode

```
for each sale_period in content.sale_periods:
    if sale_period.start <= now <= sale_period.end:
        if user.catalogue in sale_period.catalogues:
            if user.country in sale_period.countries:
                return PLAYABLE
return DENIED(SALE_PERIOD)
```

## Casys Integration

Key2 calls Casys for content with authorization groups (gated/paywalled content). If Casys returns `not_member`, Key2 denies with `CONTENT_CONTROL`. This is the bridge between Key2's format/country checks and the access-control layer.

## Key Behavioral Notes

- Key2 **never returns 404** — always serves a fallback dead key (`deadbeefdeadbeefdeadbeefdeadbeef`)
- Debug endpoints return **timestamps** of last restriction update — use to detect propagation delays
- Bootlegger detection combines: client ID spoofing, missing client-token, TLS fingerprint mismatch
- Employee users with `catalogue="all"` bypass most restrictions
- Trial users may appear as premium but have different effective catalogue — check trial flags

## Common Key2 Scenarios

**Metadata <-> Key2 Desync:** Metadata shows available but Key2 denies (or vice versa). Compare restriction timestamps in DebugService response — stale timestamps = propagation delay.

**Content Replacement:** Track/episode re-linked to new audio_id/source_id, Key2 still has restrictions for old file. Symptoms: metadata correct, Key2 debug shows stale data or unknown file_id.

**Client Caching Stale Data:** Server-side checks pass but user can't play. Client may cache old file IDs or playability responses. Ask user to clear cache, reinstall, or test on different device.

**Trial Users Appearing as Premium:** Certain trial types cause `catalogue=free` users to appear as premium. Check user account attributes for trial flags (e.g., `on-demand-trial`).

## Rate Limiting Buckets

| Bucket                            | Capacity | Fill Rate |
| --------------------------------- | -------- | --------- |
| interactive (normal)              | 300      | 0.3/s     |
| interactive-strictness_low        | 200      | 0.2/s     |
| interactive-strictness_medium     | 100      | 0.1/s     |
| interactive-strictness_high       | 30       | 0.03/s    |
| interactive-suspected_compromised | 30       | 0.001/s   |
| download                          | 10000    | 0.46/s    |
