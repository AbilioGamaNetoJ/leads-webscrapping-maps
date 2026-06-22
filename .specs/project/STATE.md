# {PROJECT_NAME} — Current State (Memory)

<!--
  LIVING FILE — updated CONSTANTLY by the AI during development.

  Purpose: maintain context between sessions. The AI must read this file
  at the start of each session and update it at the end.

  This is NOT documentation — it's working memory.
-->

| Field | Value |
|---|---|
| **Last session** | {DATETIME} |
| **Last agent** | {AGENT_NAME} |
| **Current branch** | {BRANCH} |

---

## Recorded Decisions

<!--
  Record important technical decisions with rationale.
  Format: [DATE] Decision → Rationale
-->

| Date | Decision | Rationale | Impact |
|---|---|---|---|
| {DATE} | {DECISION} | {RATIONALE} | {IMPACT} |

---

## Active Blockers

<!--
  Blockers preventing progress.
  Remove when resolved.
-->

| # | Blocker | Severity | Details |
|---|---|---|---|
| 1 | {BLOCKER} | Critical / High / Medium | {DETAILS} |

---

## Lessons Learned

<!--
  Technical learnings worth keeping. Do not remove — this is useful history.
-->

| Date | Lesson | Context |
|---|---|---|
| {DATE} | {LESSON} | {CONTEXT} |

---

## Tasks In Progress

<!--
  What is actively being worked on RIGHT NOW.
  Update status throughout the session.
-->

| # | Task | Status | Started |
|---|---|---|---|
| 1 | {TASK} | {STATUS} | {DATE} |

---

## Deferred Ideas (Parking Lot)

<!--
  Good ideas that don't fit the current moment.
  Review periodically — some mature over time.
-->

| # | Idea | Deferred on | Reason |
|---|---|---|---|
| 1 | {IDEA} | {DATE} | {REASON} |

---

## Pre-Session Checklist (for AI)

Before starting work:

- [ ] Read [PROJECT.md](./PROJECT.md) — vision & goals
- [ ] Read [ROADMAP.md](./ROADMAP.md) — features & milestones
- [ ] Read this file — decisions, blockers, live context
- [ ] Check [codebase/](../codebase/) — stack, architecture, conventions
- [ ] Check [codebase/CONCERNS.md](../codebase/CONCERNS.md) — known risks & fragilities
- [ ] Check [features/](../features/) — active specs
- [ ] Consultant `.agent/` agents and skills as needed

---

> **Updated by AI automatically.** Do not edit manually unless you know what you're doing.
