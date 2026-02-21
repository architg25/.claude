# Custom Dataset Exposure

SQL-based exposure filtering in EP UI.

## Overview

Define exposure with SQL query directly in Experimentation Platform UI.

## When to Use

- One-off exposure logic
- No existing data endpoint
- Quick iteration needed

## Configuration Steps

1. Navigate to experiment in EP UI
2. Go to "Exposure" settings
3. Select "Custom Dataset Exposure"
4. Enter SQL query

## SQL Query Format

```sql
SELECT DISTINCT spotify_user_id
FROM `project.dataset.events`
WHERE event_date BETWEEN @start_date AND @end_date
  AND feature_visible = true
  AND user_interacted = true
```

### Required Elements

| Element | Description |
|---------|-------------|
| `spotify_user_id` | Must be in SELECT |
| Date filtering | Use @start_date, @end_date |
| DISTINCT | Avoid duplicate users |

## Example: Widget Visibility

```sql
SELECT DISTINCT spotify_user_id
FROM `project.dataset.widget_impressions`
WHERE event_date BETWEEN @start_date AND @end_date
  AND widget_type = 'new_feature'
  AND impression_duration_ms > 1000
```

## Example: Scroll Depth

```sql
SELECT DISTINCT spotify_user_id
FROM `project.dataset.page_events`
WHERE event_date BETWEEN @start_date AND @end_date
  AND page = 'search_results'
  AND scroll_depth_pct > 80
```

## Validation

1. Run query manually to verify results
2. Check user count is reasonable
3. Verify no treatment bias in filter logic
4. Compare exposed vs total assigned users
