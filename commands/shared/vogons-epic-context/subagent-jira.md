# Subagent Prompt: Jira Context

Read references/jira-patterns.md for JQL patterns.

Use mcp**atlassian-mcp**list_tickets with JQL: key = {JIRA_KEY}
(or: project = CONACCESS AND summary ~ "{keyword}")

Return: summary, description, status, assignee, priority, linked issues.
Note if description is empty.
