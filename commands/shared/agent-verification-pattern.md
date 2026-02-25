# Agent Verification Pattern

A three-phase pattern to ensure all committed agents are actually spawned and completed before synthesis. Apply all three phases in order during any workflow that spawns multiple agents.

## Phase 1: Agent Type Verification (Contract Creation)

After detecting domains and identifying research needs, create an explicit agent contract:

```
## Agent Type Verification

Based on the analysis above, I will spawn the following agents:

**Standard agents** (always included):
- [agent-1]
- [agent-2]

**Domain-based agents** (added based on detection):
- [For each detected domain: [Domain] -> [agent-name]]

**Full agent list:**
1. [agent-1]
2. [agent-2]
3. [domain-agent-1]
...

Total agents to spawn: [N]

WARNING: This list is my CONTRACT. All agents listed here MUST be spawned.
```

This contract becomes the source of truth for Phases 2 and 3.

## Phase 2: Pre-Spawn Verification

Before making ANY Task tool calls to spawn agents, output a verification table that cross-checks the contract against what you are about to spawn:

```
## Pre-Spawn Verification

Cross-checking Agent Type Verification contract against Task tool calls:

| # | Agent Type (from Contract) | Will Spawn? | Reason if Skipping |
|---|---------------------------|-------------|-------------------|
| 1 | [agent-1] | Yes | - |
| 2 | [agent-2] | Yes | - |
| 3 | [domain-agent-1] | Yes | - |
...

**Verification Result:**
- Agents in contract: [N]
- Agents to spawn: [M]

All agents will be spawned? [YES/NO]
```

**BLOCKER**: If any agent is skipped, provide reason AND inform user. Do NOT proceed if skipping without acknowledgment.

**CRITICAL**: When writing the `subagent_type` parameter in Task tool calls, COPY the exact agent type string from your contract. Do NOT type it from memory.

## Phase 3: Pre-Synthesis Verification

Before synthesizing results from all agents, verify that every committed agent was actually spawned and completed:

```
## Pre-Synthesis Agent Verification

From Agent Type Verification contract:
- Total agents contracted: [N]
- Agents actually spawned: [M]

Verification: N = M? [YES/NO]
```

**BLOCKER**: Do not proceed with synthesis if N != M without user acknowledgment. If counts do not match, identify missing agents and spawn them before continuing.
