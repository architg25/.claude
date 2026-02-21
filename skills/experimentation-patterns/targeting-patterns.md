# Targeting Patterns

Configuring experiment audience targeting.

## Available Targeting Options

| Targeting | Description | Use Case |
|-----------|-------------|----------|
| Country | Geographic markets | Market-specific features |
| Platform | iOS, Android, Web | Platform-specific changes |
| App Version | Minimum version | New API requirements |
| User Segment | Custom BigQuery segment | Specific user groups |

## Country Targeting

```
Markets: US, GB, DE
```

**Considerations:**
- Larger markets = faster experiment
- Consider cultural differences
- Check metric availability per market

## Platform Targeting

```
Platforms: iOS, Android
```

**Considerations:**
- Platform-specific features only
- Mobile property propagation delay
- Consider cross-platform analysis

## App Version Targeting

```
iOS >= 8.7.0
Android >= 8.7.0.1000
```

**When Required:**
- New SDK features
- API changes
- Bug fixes in specific versions

## User Segment Targeting

Custom BigQuery-based segments:

```sql
SELECT user_id
FROM user_segments
WHERE segment = 'power_users'
```

**Considerations:**
- Requires BigQuery targeting setup
- May have bloom filter false positives (offline)
- Use online resolution for accuracy

## Exclusivity Groups

Prevent users from being in multiple experiments:

```
Exclusivity Group: search_ranking_experiments
```

**When to Use:**
- Experiments affect same user journey
- Properties could interact
- Need clean measurement

## Targeting Validation

1. Check targeting covers sufficient users
2. Verify no unintended exclusions
3. Test with specific user IDs
4. Monitor early SRM for targeting issues
