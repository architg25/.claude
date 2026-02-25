# Subagent Prompt: Replace/Append Jira Epic Description

{Replace|Append} the description of Jira epic {JIRA_KEY}.

Step 1: Read /Users/architg/.claude/commands/shared/vogons-epic-context/adf-format.md
to understand how to construct ADF JSON.

Step 2: Convert the summary below into a valid ADF JSON document following the
node reference. Key rules:

- Each section heading (Overview, Context, etc.) → heading node level 2
- Each paragraph of text → paragraph node
- Each bullet point → listItem in a bulletList
- Each link [text](url) → paragraph containing an inlineCard node
- The disclaimer → rule node, then paragraph with italic text
- Any Jira key (e.g. CONACCESS-18) → hyperlink text node with href https://jira.spotify.net/browse/{KEY}

Step 3: If appending, first fetch the current description via
mcp**atlassian-mcp**list_tickets with jql_query: "key = {JIRA_KEY}".
Note: appending to ADF is complex — prefer replacing unless user insists.

Step 4: Use mcp**atlassian-mcp**edit_ticket with:

- issue_key: "{JIRA_KEY}"
- custom_fields: a JSON string containing {"description": {your ADF doc}}
- Do NOT set the description parameter

Return: "WRITTEN" | "ERROR: {reason}"

--- SUMMARY ---
{formatted_summary}
