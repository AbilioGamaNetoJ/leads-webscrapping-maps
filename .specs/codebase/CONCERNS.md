# {PROJECT_NAME} — Concerns

<!-- Tech debt, known risks, fragilities. -->

| Field | Value |
|---|---|
| **Last updated** | {DATE} |

## Tech Debt

<!-- CUSTOMIZE: Accumulated tech debt items -->

| # | Item | Severity | Estimated effort |
|---|---|---|---|
| 1 | {ITEM} | Low / Medium / High / Critical | {S/M/L} |

## Known Risks

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| {RISK_1} | High / Medium / Low | High / Medium / Low | {MITIGATION} |

## Fragilities

<!-- Parts of the code that require extra care when modifying -->

| Area | File | Reason |
|---|---|---|
| {AREA} | `{FILE}` | {REASON} |

## Known Limitations

- {LIMITATION_1}
- {LIMITATION_2}

## Security

<!-- CUSTOMIZE: Security checklist -->

- [ ] Secrets out of code (`.env` only)
- [ ] Input validated server-side (Zod or similar)
- [ ] Auth on all protected routes
- [ ] CSRF protection active
- [ ] Rate limiting on critical endpoints
- [ ] Dependencies up to date (`npm audit`)

## Agent Kit Health

- [ ] `.agent/` agents and skills up to date
- [ ] No orphaned references to non-existent skills/agents
- [ ] `GEMINI.md` and `CLAUDE.md` aligned with `.agent/rules/GEMINI.md`

---

> **Note for AIs:** Consult this file BEFORE modifying sensitive areas. Report new concerns at the end of the session. Update `.agent/` references if agents/skills change.
