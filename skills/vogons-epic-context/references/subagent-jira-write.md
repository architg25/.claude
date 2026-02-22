# Subagent Prompt: Write Jira Epic Description

Write a description to Jira epic {JIRA_KEY}.

Step 1: Check existing description via mcp**atlassian-mcp**list_tickets
with jql_query: "key = {JIRA_KEY}". Note whether the description field
is empty or has content.

Step 2: If description is empty, write directly. If not empty, report back
"EXISTING_CONTENT" and stop — do NOT write yet.

Step 3 (if empty): Use mcp**atlassian-mcp**edit_ticket with
issue_key: "{JIRA_KEY}" and description set to the summary below.

Return: "WRITTEN" | "EXISTING_CONTENT" | "ERROR: {reason}"

--- SUMMARY TO WRITE ---
{formatted_summary}
