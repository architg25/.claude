# Metrics Hub Attributes

Boolean attributes for reusable exposure filtering.

## Overview

Define exposure logic as Metrics Hub boolean attribute, reusable across experiments.

## When to Use

- Complex exposure logic
- Reuse across multiple experiments
- Need maintainable, testable logic

## Creating an Attribute

1. Navigate to Metrics Hub
2. Create new boolean attribute
3. Define logic (SQL or config)
4. Connect to experiment in EP

## Example: Long Query Filter

```sql
-- Attribute: is_long_query_user
SELECT user_id,
       MAX(CASE WHEN query_length > 3 THEN true ELSE false END) as value
FROM search_queries
GROUP BY user_id
```

## Example: Feature Engagement

```sql
-- Attribute: used_new_feature
SELECT user_id,
       MAX(CASE WHEN feature_id = 'new_feature' THEN true ELSE false END) as value
FROM feature_usage
GROUP BY user_id
```

## Connecting to Experiment

In EP UI:
1. Go to experiment exposure settings
2. Select "Metrics Hub Attribute"
3. Choose your attribute
4. Configure inclusion criteria

## Best Practices

| Practice | Reason |
|----------|--------|
| Clear naming | `is_X_user` pattern |
| Document logic | Future maintenance |
| Test independently | Verify before experiment |
| Version if changed | Avoid mid-experiment changes |
