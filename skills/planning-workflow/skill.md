# Planning Workflow

## Plan Mode Default

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, go back to re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add summary to end section in `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## TodoWrite Usage

Use the TodoWrite tool for tracking multi-step tasks:
- Create todos at the start of complex work
- Mark tasks `in_progress` BEFORE starting work
- Complete tasks IMMEDIATELY after finishing (no batching)
- Keep exactly ONE task in_progress at a time

## When to Stop Planning and Start Coding

- **<50 line changes**: Skip planning, just do it
- **50-200 lines**: Quick todo list (3-5 items max)
- **>200 lines or multi-file**: Detailed todo list with clear deliverables
- **Complex features**: Break into stages with testable milestones

**If you're spending more time planning than coding, you're overthinking it.**

## Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own design before presenting it

## Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then propose fix
- Zero context switching required from the user
- Go fix failing CI tests yourself — then cold merge
