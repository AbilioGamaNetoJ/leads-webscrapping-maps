# {PROJECT_NAME} — Architecture

<!-- Architectural overview of the project for AI agents. -->

| Field | Value |
|---|---|
| **Last updated** | {DATE} |
| **Architectural pattern** | {PATTERN} (e.g. App Router, MVC, Microservices) |

## Conceptual Diagram

<!-- CUSTOMIZE: Describe the architecture at a high level -->

```
{LAYER_1}  →  {LAYER_2}  →  {LAYER_3}  →  {LAYER_4}
  (explanation)   (explanation)   (explanation)   (explanation)
```

## Layers

### {LAYER_NAME_1}

- **Responsibility:** {RESP}
- **Location:** `src/{PATH}`
- **Depends on:** {DEPENDENCY}

### {LAYER_NAME_2}

- **Responsibility:** {RESP}
- **Location:** `src/{PATH}`
- **Depends on:** {DEPENDENCY}

### {LAYER_NAME_3}

- **Responsibility:** {RESP}
- **Location:** `src/{PATH}`
- **Depends on:** {DEPENDENCY}

## Data Flow

<!-- CUSTOMIZE: Describe how data flows through layers -->

```
User → {FRONTEND} → {API} → {SERVICE} → {DATABASE}
                    ↑                    ↓
               {CACHE}             {EXTERNAL_API}
```

## Routes (if applicable)

| Route group | URL pattern | Auth | Purpose |
|---|---|---|---|
| {PUBLIC} | `/` | No | {PURPOSE} |
| {DASHBOARD} | `/dashboard/*` | Yes | {PURPOSE} |
| {API} | `/api/*` | Partial | {PURPOSE} |

## Architecture Decisions (ADR)

<!-- CUSTOMIZE: Record important architectural decisions -->

| ADR | Decision | Rationale | Date |
|---|---|---|---|
| 1 | {DECISION} | {RATIONALE} | {DATE} |

## AI Agent Architecture

This project uses an [Agent Kit](../../.agent/) for AI-assisted development:

- **15 Specialist Agents** in `.agent/agents/` — domain-specific personas (frontend, backend, database, etc.)
- **30 Skills** in `.agent/skills/` — reusable knowledge modules
- **12 Workflows** in `.agent/workflows/` — slash-command procedures (`/create`, `/debug`, etc.)
- See [AGENTS.md](../../AGENTS.md) for full inventory and [.agent/ARCHITECTURE.md](../../.agent/ARCHITECTURE.md) for kit internals.

---

> **Note for AIs:** For folder structure, see [STRUCTURE.md](./STRUCTURE.md). For recent decisions, see [../project/STATE.md](../project/STATE.md).
