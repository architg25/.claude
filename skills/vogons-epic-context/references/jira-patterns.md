# Atlassian MCP — Jira Query Patterns

Use `mcp__atlassian-mcp__list_tickets` with JQL queries.

## Vogons Jira Project

Project key: `CONACCESS`

## Common JQL Queries

### By exact key

```
key = CONACCESS-5
```

### By keyword in summary

```
project = CONACCESS AND summary ~ "Availability Catalog"
```

### Active epics

```
project = CONACCESS AND issuetype = Epic AND status != Done
```

### All issues for a specific epic

```
project = CONACCESS AND "Epic Link" = CONACCESS-5
```

## Useful Response Fields

The list_tickets response includes for each issue:

- `key` — e.g. CONACCESS-5
- `fields.summary` — ticket title
- `fields.description` — ticket description (often empty for Vogons)
- `fields.status.name` — current status
- `fields.assignee.displayName` — assignee
- `fields.priority.name` — priority level
- `fields.issuetype.name` — Epic, Story, Task, etc.
- `fields.issuelinks` — linked issues

## Tips

- Vogons Jira descriptions are often empty — Groove is the primary source of truth
- Use Jira mainly to check for linked issues, subtasks, or status not reflected in Groove
- `max_results` defaults to 50, increase if needed
