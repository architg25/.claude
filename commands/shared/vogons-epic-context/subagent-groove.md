# Subagent Prompt: Groove Context + Doc ID Extraction

Read references/groove-queries.md for the FULL cached schema and query templates.
DO NOT call get-type-definition or get-graphql-schema — everything is cached.

Step 1: Find the epic using the "Find Epic by Jira Key" template.
Step 2: Get full context using "Full Epic → DoD → Initiative Chain" template.
Substitute the epic ID into the template query.
Step 3: Extract Google Doc IDs from epic.description AND
epic.definitionOfDone.description — regex for /d/([^/]+)/ in URLs.

Return: complete epic data, DoD data, Initiative data, and list of doc IDs.
