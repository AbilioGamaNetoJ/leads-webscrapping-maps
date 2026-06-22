# Feature: {FEATURE_NAME}

<!--
  Feature specification with traceable IDs.
  Copy this folder, rename to the feature slug, and fill in.
  Use unique IDs in format: {SLUG}-{NUMBER}
-->

| Field | Value |
|---|---|
| **ID** | `{SLUG}` |
| **Status** | Draft / In spec / In dev / In test / Done |
| **Priority** | High / Medium / Low |
| **Effort** | S / M / L |
| **Depends on** | — / `{OTHER_SLUG}` |
| **Created** | {DATE} |

## Summary

<!-- 1-2 sentences describing the feature -->

{SHORT_DESCRIPTION}

## Requirements

### R1 — {TITLE}

| Field | Value |
|---|---|
| **ID** | `{SLUG}-R1` |
| **Type** | Functional / Non-functional / UX / Security |
| **Source** | {STAKEHOLDER} |

**Description:** {DETAILED_DESCRIPTION}

**Acceptance criteria:**

- [ ] {CRITERION_1}
- [ ] {CRITERION_2}
- [ ] {CRITERION_3}

### R2 — {TITLE}

| Field | Value |
|---|---|
| **ID** | `{SLUG}-R2` |
| **Type** | Functional / Non-functional / UX / Security |
| **Source** | {STAKEHOLDER} |

**Description:** {DETAILED_DESCRIPTION}

**Acceptance criteria:**

- [ ] {CRITERION_1}
- [ ] {CRITERION_2}

### R3 — {TITLE}

| Field | Value |
|---|---|
| **ID** | `{SLUG}-R3` |
| **Type** | Functional / Non-functional / UX / Security |
| **Source** | {STAKEHOLDER} |

**Description:** {DETAILED_DESCRIPTION}

**Acceptance criteria:**

- [ ] {CRITERION_1}
- [ ] {CRITERION_2}

## Out of Scope

- {ITEM_1}
- {ITEM_2}

## Success Metrics

| Metric | Target |
|---|---|
| {METRIC_1} | {TARGET} |
| {METRIC_2} | {TARGET} |

---

> **Note for AIs:** Use IDs (`{SLUG}-R1`, etc.) to track implementation in commits and PRs. Gray area decisions in [context.md](./context.md). Architecture in [design.md](./design.md). Tasks in [tasks.md](./tasks.md).
