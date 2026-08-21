# {PROJECT_NAME} — Current State (Memory)

<!--
  LIVING FILE — updated CONSTANTLY by the AI during development.

  Purpose: maintain context between sessions. The AI must read this file
  at the start of each session and update it at the end.

  This is NOT documentation — it's working memory.
-->

| Field | Value |
|---|---|
| **Last session** | 2026-08-21 |
| **Last agent** | Codex |
| **Current branch** | Current worktree |

---

## Recorded Decisions

<!--
  Record important technical decisions with rationale.
  Format: [DATE] Decision → Rationale
-->

| Date | Decision | Rationale | Impact |
|---|---|---|---|
| 2026-08-20 | Tipo de negócio virou combobox filtrável no cliente | Reutiliza o padrão de autocomplete de cidade/bairro e o catálogo de `includedType` da Places API | Usuário busca por nome em PT-BR; o valor enviado continua sendo o type da API |
| 2026-08-20 | Nichos comerciais usam catálogo interno e consultas textuais | A maioria não é um `includedType` aceito pela Places API | Os 92 nichos e 387 termos ficam disponíveis sem causar requisições inválidas; o tipo fica salvo no lead |
| 2026-08-20 | Botão WhatsApp nas listas de busca e histórico | O telefone internacional do Maps vira `https://wa.me/{dígitos}` | Contato direto com o lead sem copiar o número |
| 2026-08-21 | Clerk e a fonte de identidade; Neon guarda perfil e autorização | Evita uma segunda stack ORM e permite desativação imediata consultando `app_users` a cada requisição | Login fechado por convite; papéis `admin` e `member` no banco |
| 2026-08-21 | Sessão Clerk é trocada por cookie local HTTP-only | Protege navegações Jinja e APIs com o mesmo fluxo, sem expor segredos ao navegador | Páginas anônimas redirecionam para `/login`; APIs retornam 401 |
| 2026-08-21 | Login usa logo escuro dedicado e contêiner responsivo | Evita baixo contraste no fundo claro e mantém o Clerk centralizado em mobile e desktop | SVG servido em `/static/Logotipo_login-clerk.svg`; falhas do SDK aparecem na tela |
| 2026-08-21 | Migrações do legado `businesses` são idempotentes | Um Neon novo não tinha a tabela criada pela revisão-base e a aplicação pode iniciar antes do Alembic | A revisão-base cria a tabela somente quando ausente; a revisão de ratings verifica colunas antes de adicioná-las |
| 2026-08-21 | Resposta de convites do Clerk é normalizada | O Backend API retornou uma lista JSON em `GET /v1/invitations`, enquanto o código esperava sempre um envelope `data` | A tela administrativa aceita lista direta e envelope paginado |
| 2026-08-21 | Perfil é enriquecido no primeiro login | O JWT de sessão pode conter apenas o identificador; o usuário aparecia como `user_...` até o webhook chegar | `POST /auth/session` consulta o usuário no Clerk e grava nome, e-mail e imagem; falhas de enriquecimento não bloqueiam o login |

---

## Active Blockers

<!--
  Blockers preventing progress.
  Remove when resolved.
-->

| # | Blocker | Severity | Details |
|---|---|---|---|
| Nenhum | - | - | Configurar credenciais Clerk e aplicar Alembic antes do primeiro deploy autenticado |

---

## Lessons Learned

<!--
  Technical learnings worth keeping. Do not remove — this is useful history.
-->

| Date | Lesson | Context |
|---|---|---|
| {DATE} | {LESSON} | {CONTEXT} |
| 2026-08-21 | A tabela `businesses` já existia sem Alembic | A revisão `20260821_00` é uma baseline sem DDL; `20260821_01` cria apenas `app_users` |
| 2026-08-21 | A baseline precisa cobrir banco Neon vazio | A revisão de ratings falhava com `no such table: businesses` quando o Alembic era executado antes do primeiro start | A baseline passou a criar a tabela apenas quando ela não existe |
| 2026-08-21 | APIs externas podem variar o envelope da coleção | `/admin/users` falhava em `.get()` ao receber a lista direta do Clerk | O adaptador `list_pending_invitations` filtra e normaliza os dois formatos |
| 2026-08-21 | JWT não é fonte suficiente para o perfil visual | O token usado na sessão identifica o usuário, mas não garante `first_name` e e-mail | O Backend API do Clerk é consultado no login; o webhook continua sincronizando alterações posteriores |

---

## Tasks In Progress

<!--
  What is actively being worked on RIGHT NOW.
  Update status throughout the session.
-->

| # | Task | Status | Started |
|---|---|---|---|
| 1 | Autenticação Clerk e gestão de usuários | Concluída | 2026-08-21 |
| 2 | Expansão do catálogo de tipos de negócio | Concluída | 2026-08-20 |

---

## Deferred Ideas (Parking Lot)

<!--
  Good ideas that don't fit the current moment.
  Review periodically — some mature over time.
-->

| # | Idea | Deferred on | Reason |
|---|---|---|---|
| 1 | {IDEA} | {DATE} | {REASON} |

---

## Pre-Session Checklist (for AI)

Before starting work:

- [ ] Read [PROJECT.md](./PROJECT.md) — vision & goals
- [ ] Read [ROADMAP.md](./ROADMAP.md) — features & milestones
- [ ] Read this file — decisions, blockers, live context
- [ ] Check [codebase/](../codebase/) — stack, architecture, conventions
- [ ] Check [codebase/CONCERNS.md](../codebase/CONCERNS.md) — known risks & fragilities
- [ ] Check [features/](../features/) — active specs
- [ ] Consultant `.agent/` agents and skills as needed

---

> **Updated by AI automatically.** Do not edit manually unless you know what you're doing.
