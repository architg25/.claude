# Custom Source

Using pre-defined data endpoints as exposure filters.

## Overview

Custom Source uses an existing data endpoint containing exposed user IDs.

## When to Use

- Data endpoint already tracks the exposed population
- Endpoint maintained by your team
- Stable, well-tested exposure logic

## Configuration

Configure in `exp-planner` repository:

```yaml
# In exp-planner configuration
custom_exposure:
  source: data_endpoint
  endpoint_id: "myteam.exposed-users.daily"
  user_id_column: "spotify_user_id"
```

## Requirements

| Requirement | Description |
|-------------|-------------|
| Data endpoint | Must exist and be populated |
| User ID column | Must contain spotify_user_id |
| Daily refresh | Endpoint should update daily |
| Coverage | Must capture all exposed users |

## Validation

1. Verify endpoint has data for experiment period
2. Check user ID column format matches EP expectations
3. Confirm refresh schedule aligns with experiment needs

## Limitations

- Requires existing data infrastructure
- Changes require exp-planner deployment
- Less flexible than Custom Dataset
