# {PROJECT_NAME} — External Integrations

<!-- External APIs and services consumed by the project. -->

| Field | Value |
|---|---|
| **Last updated** | {DATE} |

## External Services

<!-- CUSTOMIZE: List each integration -->

### {SERVICE_NAME_1}

| Field | Value |
|---|---|
| Purpose | {PURPOSE} |
| Type | REST API / GraphQL / Webhook / SDK |
| Auth | {AUTH_TYPE} |
| Env var | `{VAR_NAME}` |
| Location | `src/lib/{SERVICE}.ts` |
| Docs | {URL} |

**Used endpoints:**

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /{ENDPOINT} | {PURPOSE} |

---

### {SERVICE_NAME_2}

| Field | Value |
|---|---|
| Purpose | {PURPOSE} |
| Type | REST API / GraphQL / Webhook / SDK |
| Auth | {AUTH_TYPE} |
| Env var | `{VAR_NAME}` |
| Location | `src/lib/{SERVICE}.ts` |
| Docs | {URL} |

**Used endpoints:**

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /webhooks/{SERVICE} | {PURPOSE} |

---

## Webhooks (incoming)

| Origin | Local route | Purpose |
|---|---|---|
| {SERVICE} | `/api/webhooks/{SERVICE}` | {PURPOSE} |

## Agent Kit Integration

The `.agent/` folder provides AI-assisted development tooling (agents, skills, workflows). It is not a runtime dependency — it serves as development infrastructure. See [AGENTS.md](../../AGENTS.md) and [.agent/ARCHITECTURE.md](../../.agent/ARCHITECTURE.md).

---

> **Note for AIs:** API keys in `.env.example`. Never hard-code secrets. Always handle integration errors with graceful fallback.
