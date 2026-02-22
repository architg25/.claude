# Subagent Prompt: Replace/Append Jira Epic Description

{Replace|Append} the description of Jira epic {JIRA_KEY}.

If replacing: Use mcp**atlassian-mcp**edit_ticket with issue_key: "{JIRA_KEY}"
and description set to the new summary below.

If appending: First fetch the current description via
mcp**atlassian-mcp**list_tickets with jql_query: "key = {JIRA_KEY}",
then use mcp**atlassian-mcp**edit_ticket with issue_key: "{JIRA_KEY}"
and description set to: {existing_description}\n\n{new_summary}

Return: "WRITTEN" | "ERROR: {reason}"

--- SUMMARY ---
{formatted_summary}
