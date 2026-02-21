---
name: generate-completions
description: Generate the ~/.claude/completions.json file for claudit autocomplete. Use this skill to enable skill/agent autocomplete in claudit comment inputs.
---

# Generate Completions

Generate the `~/.claude/completions.json` file for claudit autocomplete.

## Usage

Run `/generate-completions` to create the completions file that enables autocomplete in claudit.

## What This Skill Does

1. Extracts all available skills from the Skill tool description
2. Extracts all available agents from the Task tool description
3. Writes them to `~/.claude/completions.json`
4. Enables autocomplete when typing `/` (skills) or `@` (agents) in claudit comments

## Instructions

Extract all available skills and agents from your current context and write them to `~/.claude/completions.json`.

### Step 1: Gather Skills

Look at your Skill tool description to find all available skills. Extract:
- `name`: The skill name (e.g., "commit", "review-pr", "portal-plugin-toolkit:stand-up")
- `description`: A short description of what the skill does

### Step 2: Gather Agents

Look at your Task tool description to find all available agent types. Extract:
- `name`: The agent name (e.g., "Explore", "Plan", "code-reviewer")
- `description`: A short description of what the agent does

### Step 3: Write the File

Write the JSON to `~/.claude/completions.json` with this structure:

```json
{
  "skills": [
    { "name": "skill-name", "description": "What it does" }
  ],
  "agents": [
    { "name": "agent-name", "description": "What it does" }
  ]
}
```

### Step 4: Confirm

Tell the user the file was written and how many skills/agents were found.

## Example Output

```
Wrote ~/.claude/completions.json
- 27 skills
- 20 agents

Claudit will now show autocomplete suggestions when you type / or @ in comments.
```
