---
name: spotify-user-lookup
description: Use when looking up Spotify user information given a username, user_id, email, or other identifier. Covers account attributes (country, product, gender, age, etc.) and how dynamo-mcp auto-resolves user context.
allowed-tools:
  - mcp__dynamo-mcp__dynamo_discover
  - mcp__dynamo-mcp__dynamo_call_method
---

# Spotify User Lookup

Look up user account data and attributes via dynamo-mcp.

**Default user:** Read `~/.claude/skills/spotify-user-lookup/.env` for `SPOTIFY_USERNAME`. When the user says "my account", "my info", or "look me up" without specifying a username, use this value.

## Primary Service: useraccount / GetAccount

This is the go-to for almost all user lookups. Flexible identifier input, wide attribute coverage.

```
target:  useraccount
package: com.spotify.useraccount.v1
service: UserAccount
method:  GetAccount
```

### Identifiers

Pass exactly one in `identifier`:

| Key                                                                                          | Example                              |
| -------------------------------------------------------------------------------------------- | ------------------------------------ |
| `username`                                                                                   | `"architg"`                          |
| `user_id`                                                                                    | `"7def9c2747844b768d41a4d17be76c82"` |
| `email`                                                                                      | `"user@example.com"`                 |
| `phone_number`                                                                               | `"+1234567890"`                      |
| `facebook_uid`, `apple_id`, `samsung_id`, `google_id`, `amazon_id`, `discord_id`, `naver_id` | Third-party linked IDs               |
| `public_account_id`                                                                          | Public-facing account ID             |

Use `requested_identifiers` to get back other identifier types: `USER_ID`, `USERNAME`, `EMAIL`, `PHONE_NUMBER`, `PUBLIC_ACCOUNT_ID`, etc.

### Common Attributes

Pass as strings in `requested_attributes`. Response values come back as `stringValue`, `boolValue`, or `longValue`.

| Attribute           | Returns                    | Notes                                                                              |
| ------------------- | -------------------------- | ---------------------------------------------------------------------------------- |
| `country`           | `"US"`, `"GB"`, etc.       | Registration country                                                               |
| `catalogue-no-env`  | `"free"`, `"premium"`      | Subscription tier. **Use this, not `catalogue`** (which requires environment_data) |
| `product`           | `"free"`, `"premium"`      | Same as catalogue but as product name                                              |
| `gender`            | `"male"`, `"female"`, etc. |                                                                                    |
| `birthdate`         | `"2002-05-18"`             | ISO date                                                                           |
| `user-age`          | `23` (longValue)           | Computed age                                                                       |
| `employee`          | bool                       | Spotify employee flag                                                              |
| `email`             | string                     | Account email                                                                      |
| `name`              | string                     | Display/product name                                                               |
| `is-guest`          | bool                       | Guest account                                                                      |
| `deleted`           | bool                       | Account deleted                                                                    |
| `in-grace`          | bool                       | Subscription grace period                                                          |
| `feature-set-id`    | string                     | e.g. `"spotify/featureset/mh0qmdw2ne_US"`                                          |
| `private-attr-blob` | string                     | Encoded private attributes blob                                                    |

**Full attribute list:** https://backstage.spotify.net/user-account-platform/account-attributes

### Attributes Requiring environment_data

Some attributes (e.g. `type`, `catalogue`) need client token or backend environment context. You'll get `INVALID_ARGUMENT: Requires environment data: <attr>`. Use the `-no-env` variant when available (e.g. `catalogue-no-env`), or skip these attributes.

### Example Call

```json
{
  "identifier": { "username": "someuser" },
  "requested_identifiers": ["USER_ID", "EMAIL"],
  "requested_attributes": [
    "country",
    "catalogue-no-env",
    "product",
    "gender",
    "birthdate",
    "employee"
  ]
}
```

## Auto-Resolution in dynamo-mcp

When calling **any** service via `dynamo_call_method` with `user_info`, the MCP server auto-resolves missing fields. Just pass `{"username": "someuser"}` and the server fills in `user_id`, `country`, and `catalogue_str` automatically via GetAccount. Don't guess these fields.

## Services You Can't Use

- **user-info / GetSpotifyUser** — All authorized SAs are locked down. Use `useraccount/GetAccount` instead.
- **user-stats / StatsService** — Requires SAs on `highlights-and-stats` accounts, no impersonation access.

## Common Mistakes

- Using `catalogue` instead of `catalogue-no-env` (fails without environment_data)
- Guessing country/catalogue when passing `user_info` to other services (let auto-resolution handle it)
- Requesting `type` attribute without environment_data
