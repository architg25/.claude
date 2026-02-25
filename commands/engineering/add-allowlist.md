# Add to Global Allowlist

You are tasked with adding command patterns to the permission hook at `~/.claude/hooks/permission-manager.sh`.

## Arguments

The user may provide patterns in various formats:

- Single pattern: `/add-allowlist sbt`
- Multiple patterns: `/add-allowlist sbt, pytest, tox`
- Bash patterns with subcommands: `/add-allowlist "git revert"`
- MCP tools: `/add-allowlist mcp__some-tool__*`

## Process:

1. **Read the current hook:**
   - Read `~/.claude/hooks/permission-manager.sh`
   - Understand the existing sections and patterns

2. **Parse the user's request and determine where each pattern belongs:**

   | User Input     | Section           | What to add                                                |
   | -------------- | ----------------- | ---------------------------------------------------------- |
   | `sbt`          | Bash → Common CLI | Add `sbt` to the CLI tools regex group                     |
   | `git revert`   | Bash → Git        | Add `revert` to the git subcommands regex                  |
   | `mvn deploy`   | Bash → Maven      | Add `deploy` to the maven goals regex                      |
   | `gh pr merge`  | Bash → GitHub CLI | Add `merge` to the gh pr subcommands regex                 |
   | `bazel info`   | Bash → Bazel      | Add `info` to the bazel subcommands regex                  |
   | `mcp__foo__*`  | MCP tools         | Add new `[[ "$TOOL" =~ ^mcp__foo__ ]] && allow "Foo"` line |
   | `SomeToolName` | Core tools        | Add to appropriate core tools regex group                  |

3. **Check for duplicates:**
   - Grep the hook script for patterns that already match the requested command
   - Report any that already exist (skip them)

4. **Present the plan:**

   ```
   I'll update permission-manager.sh:

   Adding to Git subcommands regex:
     revert  (line will become: ^git\ (status|log|...|revert))

   Adding new CLI tool:
     sbt  (line will become: ^(python3|find|...|sbt)( |$))

   Already covered (skipping):
     git status  (matched by existing Git regex)

   Shall I proceed?
   ```

5. **Upon confirmation:**
   - Edit `~/.claude/hooks/permission-manager.sh` using the Edit tool
   - Add the pattern to the correct regex group or add a new line in the right section
   - Report success

## Important:

- Always show the user what will change before editing
- Preserve the existing structure and section organization
- When adding to a regex group like `(a|b|c)`, add the new entry at the end: `(a|b|c|new)`
- When adding a brand new Bash command group, add it before the `# Common CLI` section
- When adding a new MCP tool, add it in alphabetical order within the MCP section
- Changes take effect in the current session (no restart needed)

## Pattern Matching Tips:

- Bash subcommands use `\` (escaped space) in regex: `^git\ (status|log|new)`
- CLI tools use `( |$)` suffix to match "command" or "command with args"
- MCP tools use `^mcp__prefix__` to match all operations from that server
