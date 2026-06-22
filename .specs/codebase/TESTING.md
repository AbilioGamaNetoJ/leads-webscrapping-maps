# {PROJECT_NAME} — Testing

<!-- Testing strategy and coverage for AI agents. -->

| Field | Value |
|---|---|
| **Framework** | {TEST_FRAMEWORK} |
| **Last updated** | {DATE} |

## Strategy

| Type | Scope | Location | Command |
|---|---|---|---|
| Unit | Functions, hooks, utils | `__tests__/` or co-located | `{COMMAND}` |
| Integration | API Routes, flows | `__tests__/integration/` | `{COMMAND}` |
| E2E | Critical flows | `e2e/` | `{COMMAND}` |

## Test Conventions

- Test files: `{NAME}.test.{EXT}` or `{NAME}.spec.{EXT}`
- Standard describe/context/it pattern
- Mock external APIs (do not call real services)
- Isolated seed data per test

## What to test

| Priority | What |
|---|---|
| Critical | Payment flows, authentication, permissions |
| High | Core business logic, validations |
| Medium | Components with complex state |
| Low | Pure rendering, styling |

## Target Coverage

<!-- CUSTOMIZE: Define coverage targets -->

| Metric | Target |
|---|---|
| Lines | {X}% |
| Functions | {X}% |
| Branches | {X}% |

---

> **Note for AIs:** Generate tests following these conventions. New feature tests in [../features/[feature]/](../features/).
