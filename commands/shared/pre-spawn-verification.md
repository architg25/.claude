# Pre-Spawn Verification

A verification checklist to run before spawning agents, ensuring the planned agent types match what you are about to execute. This is Phase 2 of the agent verification pattern (see `commands/shared/agent-verification-pattern.md`).

## Verification Table Template

Before making ANY Task tool calls, output this table:

```
## Pre-Spawn Verification (Batch N)

Cross-checking Agent Type Verification contract against Task tool calls I'm about to make:

| Question/Step | Planned Agent (from Contract) | Agent I Will Spawn | Match? |
|---------------|-------------------------------|-------------------|--------|
| [Q1/Step X]   | [agent-type-from-contract]    | [agent-type-in-task-call] | Yes/No |
| [Q2/Step Y]   | [agent-type-from-contract]    | [agent-type-in-task-call] | Yes/No |
...

**All rows match? Proceed with spawning.**
**Any row does NOT match? STOP. Correct the agent type before spawning.**
```

## Rules

1. **Copy, don't retype**: When writing the `subagent_type` parameter in Task tool calls, COPY the exact agent type string from your Agent Type Verification contract. Do NOT type it from memory.
2. **BLOCKER on mismatch**: If any row shows a mismatch, do not proceed. Fix the agent type first.
3. **Inform user on skip**: If any contracted agent is being skipped, provide the reason and inform the user before continuing.
4. **Run per batch**: If spawning agents in multiple batches, run this verification before each batch.
