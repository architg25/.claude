---
name: dippy-rules
description: Use when the user wants to add, remove, or list Dippy rules in their ~/.dippy/config file. Triggers on mentions of "dippy", "allow command", "deny command", "block command", or managing command safety rules.
---

# Dippy Rules Manager

Manage rules in `~/.dippy/config` for the Dippy command safety gating tool.

## Rule Syntax

Each line in the config is one rule:

```
<action> <command-prefix> ["optional message"]
```

- **action**: `allow`, `deny`, or `ask` for Bash commands; `allow-mcp`, `deny-mcp`, or `ask-mcp` for MCP tools
- **command-prefix**: Matches the command and anything after it (e.g. `git` matches `git commit`, `git push`, etc.)
- **MCP pattern**: For MCP rules, use the tool name pattern with `*` wildcards (e.g. `mcp__github__get_*`)
- **message** (optional, quoted): Shown to the user when the rule triggers. Most useful with `deny`.
- Lines starting with `#` are comments.

## How to Manage Rules

1. **Read** `~/.dippy/config` first (create it if it doesn't exist)
2. **Add** a rule: append the line to the config
3. **Remove** a rule: delete the matching line
4. **List** rules: read and display the config

When adding, check for conflicts first — e.g. if the user says "allow npm" but there's already a `deny npm` line, remove the old one and explain what you did.

Keep comments that exist in the file. When adding rules, add a comment if the user gave a reason.

## Examples

User: "allow all git commands in dippy"
Action: Append `allow git` to `~/.dippy/config`

User: "block docker system prune"
Action: Append `deny docker system prune` to config

User: "deny rm -rf with message 'use trash-cli instead'"
Action: Append `deny rm -rf "use trash-cli instead"` to config

User: "remove the git allow rule"
Action: Delete the `allow git` line from config

User: "what are my dippy rules"
Action: Read and display `~/.dippy/config`

User: "allow all code-search MCP tools"
Action: Append `allow-mcp mcp__code-search__*` to config

User: "block all MCP delete operations"
Action: Append `deny-mcp mcp__*__delete_*` to config
