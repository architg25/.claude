# Implement Plan

You are tasked with implementing an approved technical plan from `~/.claude/thoughts/shared/plans/`. These plans contain phases with specific changes and success criteria.

## Getting Started

When given a plan path:
- Read the plan completely and check for any existing checkmarks (- [x])
- Read the original ticket and all files mentioned in the plan
- **Read files fully** - never use limit/offset parameters (unless explicitly advised otherwise), you need complete context
- Think deeply about how the pieces fit together
- Create a todo list to track your progress
- **Detect domains in the plan for proactive guidance:**
  - Scan the plan for domain-specific patterns (reference `commands/shared/domain-agent-registry.md`)
  - Identified domains can be consulted proactively if implementation questions arise
  - **Output for user:**
    ```
    ## Domains Detected in Plan
    - ✓ [Domain]: Found "[pattern]" → [agent-name] available for guidance
    - ✗ [Domain]: Not detected
    ```
- Start implementing if you understand what needs to be done

If no plan path provided, ask for one.

## Implementation Philosophy

Plans are carefully designed and represent agreed-upon specifications. Your job is to:
- **Implement what the plan specifies** - not a simplified version, not your interpretation
- Implement each phase fully before moving to the next
- Verify your work makes sense in the broader codebase context
- Update checkboxes in the plan as you complete sections

### Code Specifications Are Binding

When the plan includes full code implementations (classes, methods, etc.), treat these as **specifications that MUST be implemented exactly as written**. You may:
- Fix obvious typos or syntax errors
- Adjust import statements to match actual package locations
- Add missing annotations required by the framework

You may NOT:
- Simplify the implementation
- Remove features or functionality
- Replace the design with a "simpler" approach
- Skip implementing parts you find complex

### Handling Mismatches (MANDATORY)

If you encounter ANY situation where the plan cannot be implemented as written:

**STOP IMMEDIATELY. Do not continue implementing.**

Present the issue clearly to the user:
```
IMPLEMENTATION BLOCKED - Mismatch Detected

Phase: [N]
Plan specifies: [what the plan says - be specific]
Actual situation: [what you found in the codebase]
Impact: [what cannot be implemented as a result]

Options I see:
1. [option 1]
2. [option 2]

Which approach should I take?
```

**WAIT for user response before continuing.**

Examples of mismatches that MUST block implementation:
- A method/field the plan references doesn't exist
- A class has a different signature than expected
- A dependency is not available
- The architecture differs from what the plan assumes

Do NOT rationalize, simplify, or "adapt" your way around mismatches. The plan represents an agreed design - if it can't be implemented, that's information the user needs.

## Verification Approach

After implementing a phase:
- Run the success criteria checks
- Fix any issues before proceeding
- Update your progress in both the plan and your todos
- Check off completed items in the plan file itself using Edit

Don't let verification interrupt your flow - batch it at natural stopping points.

## If You Get Stuck

When something isn't working as expected:
- First, make sure you've read and understood all the relevant code
- Consider if the codebase has evolved since the plan was written
- Use the spotify-tool-researcher subagent to determine if there is any Spotify specific information that can help.
- If the code is scio/scala then additionally use the web-search-researcher subagent to search through the scio docs for any guidelines: https://spotify.github.io/scio/
- **Spawn detected domain experts proactively** (from domains identified in "Getting Started"):
  - For Scio issues → spawn `scio-pipeline-optimization-analyzer`
  - For Hendrix/ML issues → spawn `hendrix-expert`
  - For Vespa/search issues → spawn `search-indexing-expert`
  - For infrastructure issues → spawn `backend-infrastructure-expert`
  - Domain experts may identify patterns or constraints that explain the issue
- **STOP and present the mismatch clearly - ask for guidance before continuing**

Use sub-tasks sparingly - mainly for targeted debugging or exploring unfamiliar territory.

**CRITICAL: Never "work around" a problem by implementing something different than the plan specifies. If you can't implement what's in the plan, STOP and ask.**

## Resuming Work

If the plan has existing checkmarks:
- Trust that completed work is done
- Pick up from the first unchecked item
- Verify previous work only if something seems off

Remember: You're implementing a solution, not just checking boxes. Keep the end goal in mind and maintain forward momentum.

## After implementation

Once you've finished the implementation we need to make sure that the changes adhere to any existing coding guidelines/standards/agent rules defined in the repository:
- Use the **codebase-locator** agent to find any coding standards/guidelines files or files related to contributing to the codebase
- Use the **codebase-analyzer** agent to understand the guidelines
- Compare the implemented code changes with the guidelines and identify any areas where they conflict
- If there are any conflicts the present the conflicts to the user as well as the proposed changes to adhere to the guidelines.
- WAIT for user approval before making changes to the implementation.
- If any changes are made then run all of the automated success criteria from the implementation plan to ensure that the core implementation logic has not been impacted.


