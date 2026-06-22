# Feature: {FEATURE_NAME} — Design

<!--
  ONLY create for Large or Complex features.
  For Small/Medium features, spec.md + tasks.md are enough.
-->

| Field | Value |
|---|---|
| **Feature ID** | `{SLUG}` |
| **Complexity** | Large / Complex |
| **Created** | {DATE} |

## Feature Architecture

<!-- CUSTOMIZE: Diagram or description of the architecture -->

```
{COMPONENT_A}
    ↓
{COMPONENT_B}
    ↓
{COMPONENT_C}
```

## Components

### {COMPONENT_A}

- **Responsibility:** {RESP}
- **Props:** `{PROPS}`
- **State:** `{STATE}`
- **Renders when:** {CONDITION}

### {COMPONENT_B}

- **Responsibility:** {RESP}
- **Props:** `{PROPS}`
- **State:** `{STATE}`
- **Renders when:** {CONDITION}

### {COMPONENT_C}

- **Responsibility:** {RESP}
- **Props:** `{PROPS}`
- **State:** `{STATE}`
- **Renders when:** {CONDITION}

## Routes & Endpoints

| Method | Route | Purpose |
|---|---|---|
| {GET} | `/{ROUTE}` | {PURPOSE} |
| {POST} | `/api/{ENDPOINT}` | {PURPOSE} |

## Data Model

```sql
-- {TABLE}
CREATE TABLE {TABLE} (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- {COLUMNS}
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Flows

### Main Flow

1. {STEP_1}
2. {STEP_2}
3. {STEP_3}

### Error States

| Error | Handling |
|---|---|
| {ERROR_1} | {HANDLING} |
| {ERROR_2} | {HANDLING} |

### Loading / Empty States

| State | Behavior |
|---|---|
| Loading | {SKELETON/SPINNER} |
| Empty | {MESSAGE/CTA} |
| Error | {RETRY/FALLBACK} |

---

> **Note for AIs:** This design guides implementation in [tasks.md](./tasks.md). See [spec.md](./spec.md) for requirements.
