# Multi-Agent Operations Guide (No-Code Owner)

This file defines a practical 3-agent workflow for this project.

## What this setup does

- Lets you run the project as product owner/playtester.
- Splits work into Builder, Reviewer, and QA/Balance roles.
- Reduces regressions by forcing structured handoffs.

## Important limitation

The editor does not keep always-on named agents by itself. You create each agent run by pasting a task prompt.
This guide gives you copy/paste prompts and rules so it behaves like a persistent team.

## Agent Roles

### Agent A: Builder

Mission: Implement the requested feature end-to-end.

Responsibilities:
- Make code changes in scope only.
- Keep style consistent with the repo.
- Run focused validation after changes.
- Produce concise implementation handoff.

Must not:
- Expand scope without request.
- Touch unrelated systems.

### Agent B: Reviewer

Mission: Verify requirements, UX behavior, and regression risk.

Responsibilities:
- Compare task card vs implementation.
- Check edge cases and failure states.
- Flag missing acceptance criteria.
- Suggest minimal fixes.

Must not:
- Rewrite architecture unless required.
- Approve without evidence.

### Agent C: QA/Balance

Mission: Validate game feel, usability, and tuning issues.

Responsibilities:
- Run a short manual test checklist.
- Report balancing/usability pain points.
- Propose numerical tuning changes separately.

Must not:
- Mix balance edits into unrelated feature tasks.

## Universal Rules (All Agents)

1. One owner per file area at a time.
2. No parallel edits on the same file.
3. Keep changes minimal and reversible.
4. Always include: what changed, how validated, known risks.
5. Use explicit assumptions when data is missing.
6. If blocked, provide a next-best actionable alternative.

## Task Intake Template

Copy this into chat when starting a task:

- Goal:
- Scope In:
- Scope Out:
- Acceptance Criteria:
- Priority: (P0/P1/P2)
- Owner Agent: (A/B/C)
- Reviewer Agent: (A/B/C)
- Notes/Constraints:

## Handoff Template

Every completed task must end with:

- Summary:
- Files touched:
- Behavior changes:
- Validation performed:
- Known risks:
- Follow-up suggestions:

## Standard Session Cadence

1. Builder run (20-40 min target)
2. Reviewer run (10-15 min)
3. Builder fix pass (10-20 min)
4. QA/Balance run (optional, 10-20 min)
5. Merge/accept

## Conflict Rules

If two tasks conflict:
- Keep the higher-priority task only.
- Defer the other to backlog.
- Never merge mixed-purpose edits.

## Suggested Backlog Columns

- Now
- Next
- Later
- Blocked

## Definition of Done (DoD)

A task is Done only if:
- Acceptance criteria are met.
- No new editor errors in changed files.
- Basic run/test validation completed.
- Handoff template is complete.
