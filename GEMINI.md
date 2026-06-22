---
trigger: always_on
---

# GEMINI.md — AI Rules

> This file defines how **any AI tool** should behave in this workspace.
> Read the [README.md](./README.md) to understand the project before making any changes.

---

## REQUIRED READING (BEFORE ANY ACTION)

Before writing code, answering questions, or modifying files, the AI **MUST** read:

| Priority | File | What it contains |
|---|---|---|
| P0 | `GEMINI.md` (this file) | Global behavior rules |
| P0 | `CLAUDE.md` | Rules for Claude Code (points to AGENTS.md) |
| P1 | `AGENTS.md` | Agent, skill, and workflow inventory |
| P1 | `IMPLEMENTATION_GUIDE.md` | Standard implementation workflow |
| P1 | `.specs/project/PROJECT.md` | Vision, goals, constraints (AI context) |
| P1 | `.specs/project/STATE.md` | Memory: decisions, blockers, lessons |
| P2 | `README.md` | Complete project documentation (human devs) |
| P2 | `.specs/codebase/` | Stack, architecture, conventions |
| P2 | `.agent/ARCHITECTURE.md` | Agent kit architecture |

---

## ABOUT THIS PROJECT

<!-- CUSTOMIZE: Replace the placeholder below with YOUR project details -->

**{PROJECT_NAME}** is a {PROJECT_TYPE} built with:

<!-- CUSTOMIZE: List YOUR tech stack below -->
- **Framework:** <!-- e.g. Next.js 16 (App Router + Turbopack) -->
- **Language:** <!-- e.g. TypeScript 5, React 19 -->
- **Styling:** <!-- e.g. Tailwind CSS v4 -->
- **ORM:** <!-- e.g. Drizzle ORM with PostgreSQL (Neon) -->
- **Auth:** <!-- e.g. Clerk (webhook sync) -->
- **Payments:** <!-- e.g. Stripe / Asaas -->
- **State:** <!-- e.g. Zustand -->
- **UI:** <!-- e.g. shadcn/ui + Lucide Icons -->
- **Forms:** <!-- e.g. React Hook Form + Zod -->

### App Areas

<!-- CUSTOMIZE: Define YOUR application's main areas/routes -->

| Area | Route | Description |
|---|---|---|
| <!-- e.g. Store --> | <!-- e.g. src/app/(store)/ --> | <!-- e.g. Public storefront --> |
| <!-- e.g. Dashboard --> | <!-- e.g. src/app/(dashboard)/ --> | <!-- e.g. Admin panel --> |
| <!-- e.g. API --> | <!-- e.g. src/app/api/ --> | <!-- e.g. REST endpoints --> |

> For full details, see the [README.md](./README.md).

---

## AGENT SYSTEM (.agent/)

This project has an **AI agent kit** in the `.agent/` folder with:

- **15 Specialist Agents** in `.agent/agents/`
- **30 Skills** in `.agent/skills/`
- **12 Workflows** in `.agent/workflows/`
- **Shared MCP Tools** in `.agent/tools/`
- **Validation scripts** in `.agent/scripts/`

### Kit Structure

```
.agent/
├── ARCHITECTURE.md          # Agent kit documentation
├── agents/                  # 15 specialist agents
│   ├── frontend-specialist.md
│   ├── backend-specialist.md
│   ├── database-architect.md
│   ├── orchestrator.md
│   ├── debugger.md
│   └── ... (10 more)
├── skills/                  # 30 modular skills
│   ├── clean-code/
│   ├── frontend-design/
│   ├── tailwind-patterns/
│   ├── nextjs-react-expert/
│   ├── database-design/
│   └── ... (25 more)
├── workflows/               # 12 slash commands
│   ├── create.md            # /create
│   ├── enhance.md           # /enhance
│   ├── debug.md             # /debug
│   ├── deploy.md            # /deploy
│   ├── plan.md              # /plan
│   └── ... (7 more)
├── tools/                   # Shared MCP tools
│   └── pagespeed-mcp.mjs
├── rules/                   # Global rules
└── scripts/                 # Validation scripts
```

### Loading Protocol

```
User request
    ↓
Classify task type
    ↓
Select relevant agent(s)
    ↓
Read corresponding SKILL.md
    ↓
Apply rules → Execute task
```

### Most Relevant Agents for This Project

<!-- CUSTOMIZE: List the agents most relevant to YOUR project -->

| Agent | When to Use |
|---|---|
| `frontend-specialist` | UI/UX, React components, styling, pages |
| `backend-specialist` | API Routes, business logic, integrations |
| `database-architect` | Schema design, queries, migrations |
| `debugger` | Bugs, errors, unexpected behaviors |
| `orchestrator` | Complex multi-domain tasks |
| `project-planner` | Feature planning, task breakdown |

---

## GLOBAL BEHAVIOR RULES

> These are the **canonical global rules** (single source of truth). The operational behavior engine — request classifier, intelligent agent routing, TIER protocol, Socratic Gate and the script checklist — lives in [`.agent/rules/GEMINI.md`](./.agent/rules/GEMINI.md) and defers to the rules below for language and clean code.

### Language

<!-- CUSTOMIZE: Set YOUR language preferences -->
- The project's primary language is **Brazilian Portuguese (pt-BR)**
- Responses to the user: **in Portuguese**
- Code (variables, functions, comments): **in English**
- Table/column names in DB: **in English**

### Clean Code

- Concise, self-documenting code
- No over-engineering or unnecessary abstractions
- Follow patterns already established in the codebase
- Strong TypeScript typing (no `any` except when justified)
- Imports with `@/` alias (configured in tsconfig)

### Before Modifying Any File

1. **Read** the file before editing
2. **Understand** the context and dependencies
3. **Preserve** existing patterns (imports, naming, style)
4. **Mentally test** the impact on other files

### Environment Variables

- **NEVER** expose secrets/keys in code
- **NEVER** commit the `.env` file
- Use `process.env.VARIABLE` on the server
- Use `NEXT_PUBLIC_` prefix only for client-side variables
- All required variables documented in `.env.example`

### Database

<!-- CUSTOMIZE: Update with YOUR database setup -->
- Schema defined in `src/db/schema.ts` (using project ORM)
- Use the project's ORM for all queries (no raw SQL)
- Use migration tools for schema changes

### Authentication

<!-- CUSTOMIZE: Update with YOUR auth setup -->
- Auth provider manages user sessions
- Webhooks sync external users with local database
- Check permissions via role-based access control

---

## HOW EACH TOOL SHOULD USE THIS FILE

### Gemini CLI / Gemini Code Assist

The **Gemini CLI** (`gemini`) and **Gemini Code Assist** automatically read the `GEMINI.md` in the project root as context instructions.

**Expected behavior:**
1. Read this file at the start of each session
2. Apply the global rules defined above
3. Consult `.agent/agents/` to use specialist agents
4. Consult `.agent/workflows/` for workflows via `/command`
5. Respond in the project's primary language

### Claude Code

**Claude Code** reads the `CLAUDE.md` in the project root. The `CLAUDE.md` file references `AGENTS.md` which in turn documents the entire agent system.

**Expected behavior:**
1. Read `CLAUDE.md` -> follows to `AGENTS.md`
2. `AGENTS.md` documents agents, skills, and workflows in `.agent/`
3. Apply the same global rules from this `GEMINI.md`
4. Use specialist agents from `.agent/agents/` when relevant
5. Respond in the project's primary language

### Antigravity Chat (Google)

**Antigravity** reads `GEMINI.md` as a user rule. It also has access to the skill system in `.agent/`.

**Expected behavior:**
1. This file is loaded as `user_rules`
2. Must follow the intelligent agent routing protocol
3. Available skills are listed automatically
4. Available workflows are listed automatically
5. Respond in the project's primary language

### OpenCode

**OpenCode** (`opencode`) reads instructions from `opencode.jsonc` for MCPs, but also respects `AGENTS.md` and `GEMINI.md` when mentioned by the user.

**Expected behavior:**
1. Read `AGENTS.md` when mentioned via `@AGENTS.md`
2. Use MCPs configured in `opencode.jsonc` or `.mcp.json`
3. Apply the same global rules from this `GEMINI.md`
4. Respond in the project's primary language

### Cursor / Windsurf / Others

Any other AI IDE should:
1. Read this `GEMINI.md` as project rules
2. Read `AGENTS.md` to understand the agent system
3. Consult `README.md` for project context
4. Follow the same rules defined above

---

## AVAILABLE WORKFLOWS

Slash commands that can be invoked by the user:

| Command | File | Description |
|---|---|---|
| `/brainstorm` | `.agent/workflows/brainstorm.md` | Socratic Discovery |
| `/create` | `.agent/workflows/create.md` | Create new feature |
| `/debug` | `.agent/workflows/debug.md` | Debug issues |
| `/deploy` | `.agent/workflows/deploy.md` | Deploy to production |
| `/enhance` | `.agent/workflows/enhance.md` | Improve existing code |
| `/orchestrate` | `.agent/workflows/orchestrate.md` | Coordinate multiple agents |
| `/plan` | `.agent/workflows/plan.md` | Plan tasks |
| `/preview` | `.agent/workflows/preview.md` | Preview server |
| `/status` | `.agent/workflows/status.md` | Project status |
| `/test` | `.agent/workflows/test.md` | Run tests |
| `/ui-ux-pro-max` | `.agent/workflows/ui-ux-pro-max.md` | Advanced design |
| `/caveman` | `.agent/workflows/caveman.md` | Concise mode |

---

## FINAL CHECKLIST

Before considering a task complete:

- [ ] Code compiles without errors (`npm run build`)
- [ ] TypeScript has no type errors
- [ ] Project patterns maintained
- [ ] Sensitive variables not exposed
- [ ] Response in the project's primary language

---

> **References:**
> - Project documentation (human devs): [README.md](./README.md)
> - Project vision (AI context): [.specs/project/PROJECT.md](./.specs/project/PROJECT.md)
> - Memory & state: [.specs/project/STATE.md](./.specs/project/STATE.md)
> - Roadmap: [.specs/project/ROADMAP.md](./.specs/project/ROADMAP.md)
> - Codebase docs: [.specs/codebase/](./.specs/codebase/)
> - Agent system: [AGENTS.md](./AGENTS.md)
> - Claude Code instructions: [CLAUDE.md](./CLAUDE.md)
> - Implementation guide: [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
> - Behavior engine (routing, TIERs, gates): [.agent/rules/GEMINI.md](./.agent/rules/GEMINI.md)
> - Kit architecture: [.agent/ARCHITECTURE.md](./.agent/ARCHITECTURE.md)
