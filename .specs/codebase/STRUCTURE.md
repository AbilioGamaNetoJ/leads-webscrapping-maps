# {PROJECT_NAME} — Directory Structure

<!-- Navigable map of the project for AI agents. -->

| Field | Value |
|---|---|
| **Root** | `src/` |
| **Last updated** | {DATE} |

## Directory Tree

<!-- CUSTOMIZE: Adapt the structure to your project -->

```
{PROJECT_NAME}/
├── src/
│   ├── app/                          # Main router
│   │   ├── (public)/                 # Public routes
│   │   │   ├── page.tsx              # Home page
│   │   │   └── layout.tsx            # Public layout
│   │   ├── (dashboard)/              # Authenticated routes
│   │   │   ├── page.tsx              # Dashboard
│   │   │   └── layout.tsx            # Admin layout
│   │   ├── api/                      # API Routes
│   │   │   ├── webhooks/             # Webhooks
│   │   │   └── {resource}/           # REST endpoints
│   │   ├── layout.tsx                # Root layout
│   │   └── globals.css               # Global styles
│   ├── components/                   # Components
│   │   ├── ui/                       # Base components (design system)
│   │   ├── {domain}/                 # Domain-specific components
│   │   └── shared/                   # Shared components
│   ├── db/                           # Database
│   │   ├── index.ts                  # Connection
│   │   ├── schema.ts                 # Schema / tables
│   │   └── seed.ts                   # Seed data
│   ├── lib/                          # Utilities and integrations
│   ├── stores/                       # State management
│   └── types/                        # TypeScript types
├── .specs/                           # AI agent documentation
│   ├── project/                      # Vision, roadmap, state
│   ├── codebase/                     # Stack, architecture, conventions
│   ├── features/                     # Feature specs
│   └── quick/                        # Ad-hoc tasks
├── .agent/                           # AI agent kit
│   ├── agents/                       # 15 specialist agents
│   ├── skills/                       # 30 modular skills
│   ├── workflows/                    # 12 slash commands
│   ├── tools/                        # Shared MCP tools
│   ├── rules/                        # Global rules
│   ├── scripts/                      # Validation scripts
│   └── ARCHITECTURE.md               # Kit architecture docs
├── .env.example                      # Environment variables
├── README.md                         # Documentation for human devs
├── IMPLEMENTATION_PLAN.md            # Implementation plan
├── GEMINI.md                         # Global AI behavior rules
├── CLAUDE.md                         # Claude Code instructions
├── AGENTS.md                         # Agent system inventory
└── package.json
```

## Where to Find

| What | Where |
|---|---|
| Pages & routes | `src/app/` |
| Reusable components | `src/components/` |
| Business logic | `src/lib/` |
| DB schema | `src/db/schema.ts` |
| Shared types | `src/types/` |
| Global state | `src/stores/` |
| API endpoints | `src/app/api/` |
| AI agent resources | `.agent/` |
| AI project context | `.specs/` |

---

> **Note for AIs:** Use this map to navigate the code. For architectural details, see [ARCHITECTURE.md](./ARCHITECTURE.md). For agent kit details, see [AGENTS.md](../../AGENTS.md).
