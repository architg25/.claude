# Debugging Exposure

Troubleshooting exposure issues.

## Exposure Not Logged

### Symptoms
- Zero or low exposure count
- Metrics not calculating

### Debugging Steps

1. **Check property resolution**
   ```java
   log.info("Resolved config: {}", config.get(MY_PROPERTY));
   ```

2. **Verify exposure call**
   ```java
   log.info("Exposing user {} for experiment {}", userId, experimentId);
   exposerLib.expose(userId, experimentId);
   ```

3. **Check exposure pipeline**
   - Verify exposure events in logging
   - Check pipeline latency (24-48h)

## Exposure Count Mismatch

### Symptoms
- Exposed count << assigned count
- More than expected filtering

### Investigation

| Check | How |
|-------|-----|
| Filter too aggressive | Compare filter criteria to user behavior |
| Feature not visible | Check feature area visibility |
| Code path not reached | Add logging to exposure path |

## SRM Investigation

### Symptoms
- Variant proportions don't match allocation

### Steps

1. **Segment by platform**
   - Is SRM specific to iOS/Android/Web?

2. **Segment by country**
   - Is SRM specific to certain markets?

3. **Check timing**
   - Is SRM worse in early/late experiment period?

4. **Review filter logic**
   - Is filter treatment-agnostic?

## Metrics Not Joining

### Symptoms
- Exposure logged but metrics empty

### Checks

1. **User ID format**
   - Exposure uses spotify_user_id?
   - Metrics use same ID format?

2. **Date alignment**
   - Exposure date matches metric date range?

3. **Pipeline timing**
   - Both datasets refreshed?

## Useful Queries

### Check Exposure Counts
```sql
SELECT variant, COUNT(DISTINCT user_id) as exposed_users
FROM exposure_table
WHERE experiment_id = 'my_experiment'
  AND date BETWEEN @start AND @end
GROUP BY variant
```

### Check Filter Coverage
```sql
SELECT
  COUNT(DISTINCT e.user_id) as exposed,
  COUNT(DISTINCT a.user_id) as assigned,
  COUNT(DISTINCT e.user_id) / COUNT(DISTINCT a.user_id) as coverage
FROM assignments a
LEFT JOIN exposures e ON a.user_id = e.user_id
WHERE a.experiment_id = 'my_experiment'
```

## Support

- #experiment-support - Exposure questions
- #metrics-hub - Metrics join issues
