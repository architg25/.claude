# DRM Services Reference

_Adapted from refused/skills for dynamo-mcp._

## Architecture Overview

All DRM services are stateless proxies over Key2:

```
CENC path:     Client -> Edge -> DRM Service -> Key2 (key + playability) -> DRM Response -> Client
Non-CENC path: Client -> PlayPlay -> Key2 (returns obfuscated key)
```

## PlayPlay

Non-CENC DRM (OGG Vorbis, etc.) for desktop, older clients.

**Endpoints:** Use `dynamo_discover` to find PlayPlay services.

**Error codes:**

- 403 — Key2 FORBIDDEN (country, catalogue, format, bootleg)
- 429 — Key2 RATE_LIMITED
- 400 — invalid file/content ID

**Key rules:**

- Token denylist — specific client tokens can be blocked
- Bootleg detection — client ID spoofing, missing client-token, TLS fingerprint
- Lossless client profiles — only allowed for specific client profiles

## Widevine License

Android, Chrome, Chromecast.

**Endpoints:** Use `dynamo_discover` to find Widevine License services.

**CDM blocking:** Compromised Content Decryption Modules are blocked by device ID. Symptoms: 403 on specific devices only.

**Audio denylist:** Specific audio content can be denylisted from Widevine entirely (rare, used for high-value content protection).

**VMP (Verified Media Path):** Enforced on some platforms to ensure playback through verified software stack.

## FairPlay License

iOS, macOS Safari.

**Endpoints:** Use `dynamo_discover` to find FairPlay License services.

**Certificate versioning:** Legacy certificates (pre-v26) vs current (v26+). Older clients may need protocol fallback.

**Protocol fallback:** If v2 protocol fails, service attempts v1 for backward compatibility with older iOS versions.

## PlayReady License

Xbox, LG TVs, Windows.

**Endpoints:** Use `dynamo_discover` to find PlayReady License services.

**Audio client lockdown:** Only specific client IDs are allowed to request PlayReady audio licenses. Unknown client IDs get 403.

## Director

Video manifest service — resolves video playability.

**Endpoints:** Use `dynamo_discover` to find Director services.

**Playability check:** Calls Key2 for video playability before serving manifest.

**noauth endpoint:** Skips auth checks entirely — used for public/preview content. If content plays on noauth but not on auth endpoint, the issue is in the auth/access layer, not content availability.

## DRM Error Mapping from Key2

| Key2 Status  | HTTP | Meaning                                       |
| ------------ | ---- | --------------------------------------------- |
| OK           | 200  | Key served, license generated                 |
| RATE_LIMITED | 429  | Rate limit exceeded                           |
| BAD_REQUEST  | 400  | Invalid content/file ID                       |
| FORBIDDEN    | 403  | GRM denied (country, catalogue, format, etc.) |
| NOT_FOUND    | 404  | Content key not in Key2                       |
