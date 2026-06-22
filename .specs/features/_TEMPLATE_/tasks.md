# Feature: {FEATURE_NAME} — Tasks

<!--
  ONLY create for Large or Complex features.
  Atomic tasks with verification. Each task = 1 commit ideally.
-->

| Field | Value |
|---|---|
| **Feature ID** | `{SLUG}` |
| **Total tasks** | {N} |
| **Progress** | 0/{N} |

## Tasks

### 1. {TASK_TITLE}

| Field | Value |
|---|---|
| **ID** | `{SLUG}-T1` |
| **Status** | ⬜ pending / 🟡 in progress / ✅ done |
| **Effort** | S / M / L |
| **Depends on** | — |
| **Files** | `{AFFECTED_FILES}` |

**Description:** {WHAT_TO_DO}

**Verification:**

- [ ] {CRITERION_1}
- [ ] {CRITERION_2}
- [ ] {CRITERION_3}

---

### 2. {TASK_TITLE}

| Field | Value |
|---|---|
| **ID** | `{SLUG}-T2` |
| **Status** | ⬜ pending / 🟡 in progress / ✅ done |
| **Effort** | S / M / L |
| **Depends on** | `{SLUG}-T1` |
| **Files** | `{AFFECTED_FILES}` |

**Description:** {WHAT_TO_DO}

**Verification:**

- [ ] {CRITERION_1}
- [ ] {CRITERION_2}

---

### 3. {TASK_TITLE}

| Field | Value |
|---|---|
| **ID** | `{SLUG}-T3` |
| **Status** | ⬜ pending / 🟡 in progress / ✅ done |
| **Effort** | S / M / L |
| **Depends on** | `{SLUG}-T1`, `{SLUG}-T2` |
| **Files** | `{AFFECTED_FILES}` |

**Description:** {WHAT_TO_DO}

**Verification:**

- [ ] {CRITERION_1}
- [ ] {CRITERION_2}

---

> **Note for AIs:** Execute tasks in order. Update status after each one. Use IDs in commits: `feat({SLUG}): T1 - {description}`.
