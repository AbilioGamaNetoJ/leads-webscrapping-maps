# AGENTS.md — AI Agent System

> Complete inventory of specialist agents, skills, and workflows available in this project.
> Read the [README.md](./README.md) for project context.
> See [GEMINI.md](./GEMINI.md) for global AI behavior rules.

---

## How to Use This File

This file is the **entry point** for AI tools interacting with the project. It maps:

1. **Agents** -> Specialists the AI can "assume" for specific tasks
2. **Skills** -> Knowledge modules the agents load
3. **Workflows** -> Slash commands (`/create`, `/debug`, etc.) for structured procedures

### Which Tool Reads This File?

| Tool | How It Accesses | Entry File |
|---|---|---|
| **Claude Code** | Reads `CLAUDE.md` -> references this file | `CLAUDE.md` |
| **Gemini CLI** | Reads `GEMINI.md` -> references this file | `GEMINI.md` |
| **Antigravity** | Loads `GEMINI.md` as user rules | `GEMINI.md` |
| **OpenCode** | Via `@AGENTS.md` mention by user | `opencode.jsonc` + this file |
| **Cursor/Windsurf** | Via project rules or mention | This file |

---

## How to Customize This File

When starting a new project, update these sections:

1. **Project-Specific Agents** — List the agents most relevant to YOUR project
2. **Relevant Skills** — List skills that match your tech stack
3. **References** — Update project name and links
4. **.specs/** — Preencha os templates em `.specs/` com os dados do seu projeto

> Everything else (complete agent list, skill list, workflows) is universal and should NOT be changed.

---

## Agent Kit Structure

All resources are in the `.agent/` folder in the project root:

```
.agent/
├── ARCHITECTURE.md           # Complete kit documentation
├── agents/                   # 15 specialist agents (.md)
├── skills/                   # 30 modular skills (folders)
├── workflows/                # 12 workflows/slash commands (.md)
├── tools/                    # Shared MCP tools (pagespeed, etc.)
├── rules/                    # Global rules
├── scripts/                  # Validation scripts (Python)
└── mcp_config.json           # MCP configuration
```

---

## Project Documentation (`.specs/`)

> **`.specs/` is the canonical source of truth for AI agents.**
> `README.md` is the entry point for human developers.
> Keep `.specs/` updated — the AI depends on it for context between sessions.

```
.specs/
├── project/
│   ├── PROJECT.md            # Vision, goals, constraints
│   ├── ROADMAP.md            # Features & milestones
│   └── STATE.md              # Memory: decisions, blockers, lessons, todos
├── codebase/                 # Brownfield analysis (existing projects)
│   ├── STACK.md              # Tech stack (canonical)
│   ├── ARCHITECTURE.md       # Architecture decisions (ADR)
│   ├── CONVENTIONS.md        # Code conventions
│   ├── STRUCTURE.md          # Directory map
│   ├── TESTING.md            # Testing strategy
│   ├── INTEGRATIONS.md       # External APIs & services
│   └── CONCERNS.md           # Tech debt, risks, fragilities
├── features/                 # Feature specifications
│   └── [feature]/
│       ├── spec.md           # Requirements with traceable IDs
│       ├── context.md        # User decisions for gray areas
│       ├── design.md         # Architecture & components (Large/Complex only)
│       └── tasks.md          # Atomic tasks with verification (Large/Complex only)
└── quick/                    # Ad-hoc tasks (quick mode)
    └── NNN-slug/
        ├── TASK.md           # Task description & steps
        └── SUMMARY.md        # Completion summary
```

### `.specs/` Reading Protocol (for AI)

Before any task, the AI **MUST**:

1. Read `.specs/project/PROJECT.md` — understand vision and constraints
2. Read `.specs/project/STATE.md` — decisions, active blockers, lessons
3. Check `.specs/features/` — is there an active spec for this task?
4. Consult `.specs/codebase/` as needed (CONVENTIONS.md before coding)

After completing a task, the AI **MUST**:

1. Update `.specs/project/STATE.md` — new decisions, blockers resolved, lessons learned
2. Update `.specs/project/ROADMAP.md` — feature status changes
3. If feature work: update `.specs/features/[feature]/tasks.md`

---

## Specialist Agents (15)

Each agent is a `.md` file in `.agent/agents/` with persona, rules, and associated skills.

<!-- CUSTOMIZE: List the agents most relevant to YOUR project below -->
### Project-Specific Agents

| Agent | File | When to Use |
|---|---|---|
| `frontend-specialist` | `.agent/agents/frontend-specialist.md` | UI/UX, React components, styling, pages |
| `backend-specialist` | `.agent/agents/backend-specialist.md` | API Routes, business logic, integrations |
| `database-architect` | `.agent/agents/database-architect.md` | Schema design, queries, migrations |
| `debugger` | `.agent/agents/debugger.md` | Bugs, errors, unexpected behaviors |
| `orchestrator` | `.agent/agents/orchestrator.md` | Complex multi-domain tasks |
| `project-planner` | `.agent/agents/project-planner.md` | Planning, feature breakdown |

### Complete Agent List

| # | Agent | Focus |
|---|---|---|
| 1 | `orchestrator` | Multi-agent coordination |
| 2 | `project-planner` | Discovery and planning |
| 3 | `frontend-specialist` | Web UI/UX |
| 4 | `backend-specialist` | API and business logic |
| 5 | `database-architect` | Schema and SQL |
| 6 | `mobile-developer` | iOS, Android, React Native |
| 7 | `devops-engineer` | CI/CD, Docker, infrastructure |
| 8 | `security-auditor` | Security compliance |
| 9 | `test-engineer` | Testing strategies |
| 10 | `debugger` | Root cause analysis |
| 11 | `performance-optimizer` | Performance, Web Vitals |
| 12 | `seo-specialist` | SEO, ranking |
| 13 | `documentation-writer` | Documentation |
| 14 | `qa-automation-engineer` | E2E tests, CI |
| 15 | `explorer-agent` | Codebase analysis |

---

## Skills (30)

Skills are knowledge modules in `.agent/skills/`. Each skill has a `SKILL.md` with instructions.

<!-- CUSTOMIZE: List the skills that match YOUR tech stack below -->
### Project-Relevant Skills

| Skill | Folder | Relevance |
|---|---|---|
| `nextjs-react-expert` | `.agent/skills/nextjs-react-expert/` | <!-- e.g. Project core --> |
| `tailwind-patterns` | `.agent/skills/tailwind-patterns/` | <!-- e.g. Styling --> |
| `frontend-design` | `.agent/skills/frontend-design/` | <!-- e.g. UI/UX --> |
| `database-design` | `.agent/skills/database-design/` | <!-- e.g. ORM schema --> |
| `api-patterns` | `.agent/skills/api-patterns/` | <!-- e.g. API Routes --> |
| `clean-code` | `.agent/skills/clean-code/` | <!-- e.g. Global patterns --> |
| `testing-patterns` | `.agent/skills/testing-patterns/` | <!-- e.g. Testing --> |
| `vulnerability-scanner` | `.agent/skills/vulnerability-scanner/` | <!-- e.g. Security --> |
| `seo-fundamentals` | `.agent/skills/seo-fundamentals/` | <!-- e.g. SEO --> |

### Complete Skill List by Category

**Frontend & UI:** `nextjs-react-expert`, `tailwind-patterns`, `frontend-design`, `web-design-guidelines`
**Backend & API:** `api-patterns`, `nodejs-best-practices`
**Database:** `database-design`
**Testing:** `testing-patterns`, `webapp-testing`, `code-review-checklist`, `lint-and-validate`
**Security:** `vulnerability-scanner`
**Architecture:** `app-builder`, `architecture`, `plan-writing`, `brainstorming`
**SEO & Growth:** `seo-fundamentals`, `geo-fundamentals`
**Mobile:** `mobile-design`
**DevOps:** `deployment-procedures`, `performance-profiling`
**Shell/CLI:** `bash-linux`
**Other:** `clean-code`, `behavioral-modes`, `parallel-agents`, `intelligent-routing`, `mcp-builder`, `documentation-templates`, `i18n-localization`, `systematic-debugging`

---

## Workflows / Slash Commands (12)

Workflows in `.agent/workflows/`. Invoked via `/command`.

| Command | File | Description |
|---|---|---|
| `/brainstorm` | `brainstorm.md` | Socratic Discovery -- explore options before implementing |
| `/create` | `create.md` | Create new application or feature |
| `/debug` | `debug.md` | Systematic bug investigation |
| `/deploy` | `deploy.md` | Deploy to production with pre-flight checks |
| `/enhance` | `enhance.md` | Add/improve existing features |
| `/orchestrate` | `orchestrate.md` | Coordinate multiple agents for complex tasks |
| `/plan` | `plan.md` | Create implementation plan (no code) |
| `/preview` | `preview.md` | Start/stop preview server |
| `/status` | `status.md` | Check project status and progress |
| `/test` | `test.md` | Generate and run tests |
| `/ui-ux-pro-max` | `ui-ux-pro-max.md` | Advanced design with 50 styles |
| `/caveman` | `caveman.md` | Concise mode, save tokens |

---

## Validation Scripts

Scripts in `.agent/scripts/` for auditing and validation:

```bash
# Quick audit during development
python .agent/scripts/checklist.py .

# Full verification before deploy
python .agent/scripts/verify_all.py . --url http://localhost:3000
```

---

## References

<!-- CUSTOMIZE: Update project name and links below -->
- **Project (human):** [README.md](./README.md) -- Project documentation for developers
- **Project (AI):** [.specs/project/PROJECT.md](./.specs/project/PROJECT.md) -- Vision & goals
- **Memory:** [.specs/project/STATE.md](./.specs/project/STATE.md) -- Decisions, blockers, lessons
- **Roadmap:** [.specs/project/ROADMAP.md](./.specs/project/ROADMAP.md) -- Features & milestones
- **Codebase:** [.specs/codebase/](./.specs/codebase/) -- Stack, architecture, conventions
- **AI Rules:** [GEMINI.md](./GEMINI.md) -- Global rules for all AI tools
- **Claude Code:** [CLAUDE.md](./CLAUDE.md) -- Specific instructions for Claude Code
- **Implementation Guide:** [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) -- Standard AI workflow
- **Kit Architecture:** [.agent/ARCHITECTURE.md](./.agent/ARCHITECTURE.md) -- Internal agent kit documentation
