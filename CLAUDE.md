# CLAUDE.md — Instructions for Claude Code

> This file is automatically read by **Claude Code** when starting a session in this project.
> It defines the expected behavior and points to available agent resources.

---

## Project Context

<!-- CUSTOMIZE: Describe YOUR project below -->
<!-- Example: This is **Project Name** — a brief description of what the project does. -->

Read the [README.md](./README.md) for human-oriented project documentation.

For agent-oriented context, consult `.specs/`:
- [.specs/project/PROJECT.md](./.specs/project/PROJECT.md) — Vision, goals, constraints
- [.specs/project/STATE.md](./.specs/project/STATE.md) — Memory: decisions, blockers, lessons
- [.specs/project/ROADMAP.md](./.specs/project/ROADMAP.md) — Features & milestones
- [.specs/codebase/](./.specs/codebase/) — Stack, architecture, conventions, integrations

---

## Required Reading

Before any action, read these files in order:

| Priority | File | What it contains |
|---|---|---|
| P0 | `CLAUDE.md` (this file) | Claude-specific behavior rules |
| P0 | `GEMINI.md` | Global rules for all AI tools |
| P1 | `AGENTS.md` | Agent, skill, and workflow inventory |
| P1 | `IMPLEMENTATION_GUIDE.md` | Standard implementation workflow |
| P1 | `.specs/project/PROJECT.md` | Vision, goals, constraints (AI context) |
| P1 | `.specs/project/STATE.md` | Memory: decisions, blockers, lessons |
| P2 | `README.md` | Complete project documentation (human devs) |
| P2 | `.specs/codebase/` | Stack, architecture, conventions |
| P2 | `.agent/ARCHITECTURE.md` | Agent kit architecture |

---

## Agent System

This project has a **complete AI agent kit** in the `.agent/` folder. See [AGENTS.md](./AGENTS.md) for the detailed inventory.

### Available Resources

| Resource | Location | Quantity |
|---|---|---|
| Specialist Agents | `.agent/agents/` | 15 |
| Modular Skills | `.agent/skills/` | 30 |
| Workflows (slash commands) | `.agent/workflows/` | 12 |
| Shared MCP Tools | `.agent/tools/` | PageSpeed, etc. |
| Validation Scripts | `.agent/scripts/` | 2 master + skill-level |

### Most Relevant Agents

<!-- CUSTOMIZE: List the agents most relevant to YOUR project -->
- `frontend-specialist` -> UI/UX, React, styling
- `backend-specialist` -> API Routes, business logic
- `database-architect` -> Schema, queries
- `debugger` -> Bug investigation
- `orchestrator` -> Complex multi-domain tasks
- `project-planner` -> Feature planning

---

## MCP Servers

This project uses MCP servers defined in [.mcp.json](./.mcp.json):

- **context7** — Documentation lookup for libraries
- **chrome-devtools-mcp** — Browser DevTools inspection
- **pagespeed** — PageSpeed Insights analysis (shared in `.agent/tools/`)
- **tavily** — Web search for research

API keys for MCP servers are stored in `.env` (see [.env.example](./.env.example)).

---

## Behavior Rules

### Language

<!-- CUSTOMIZE: Set YOUR project's language preferences -->
- Responses: **Brazilian Portuguese**
- Code (variables, functions): **English**

### Code Standards

- TypeScript strict, no `any` without justification
- Imports with `@/` alias
- Follow existing patterns in the codebase
- Use the project's ORM (no raw SQL when ORM works)
- Sensitive variables only via `process.env`

### Before Editing Any File

1. Read the file and understand the context
2. Check dependencies and impact on other files
3. Preserve existing patterns (imports, naming, style)
4. Never expose secrets in code

### Before Committing

Antes de qualquer commit com mudança importante (visual, arquitetural, nova feature, performance, SEO), preencha a seção `[Não lançado]` do [`CHANGELOG.md`](./CHANGELOG.md). Veja as regras completas em [`.specs/codebase/CONVENTIONS.md`](./.specs/codebase/CONVENTIONS.md#changelog).

### Never Do

- Commit `.env`
- Use `any` without justification
- Write raw SQL when ORM works
- Ignore TypeScript typing
- Expose API keys on client-side
- Skip reading `README.md` and `.agent/` before starting work
- Commitar mudanças importantes sem atualizar o `CHANGELOG.md`

---

## References

| File | Purpose |
|---|---|
| [README.md](./README.md) | Complete project documentation |
| [AGENTS.md](./AGENTS.md) | Agent, skill, and workflow inventory |
| [GEMINI.md](./GEMINI.md) | Global rules for all AI tools |
| [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) | Standard AI workflow |
| [.agent/ARCHITECTURE.md](./.agent/ARCHITECTURE.md) | Agent kit architecture |
| [.env.example](./.env.example) | Required environment variables |
