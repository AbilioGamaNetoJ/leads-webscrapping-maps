# {PROJECT_NAME} — Current State (Memory)

<!--
  LIVING FILE — updated CONSTANTLY by the AI during development.

  Purpose: maintain context between sessions. The AI must read this file
  at the start of each session and update it at the end.

  This is NOT documentation — it's working memory.
-->

| Field | Value |
|---|---|
| **Last session** | 2026-08-24 |
| **Last agent** | Claude Code |
| **Current branch** | main |

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
| 2026-08-24 | Busca de até 1000 leads é feita em lotes com cursor no cliente | Uma request única não cabe nos 10s da Vercel Hobby, e um job assíncrono exigiria tabela de jobs em serverless | `POST /search` roda um lote e devolve o `cursor` do próximo; o `app.js` repete até o alvo, `cursor: null`, ou 3 lotes seguidos sem novidade |
| 2026-08-24 | Cada termo do plano é esgotado dentro do lote | Mantém o cursor como um simples índice, sem trafegar `pageToken` do Google pelo navegador | A onda é dimensionada por `remaining / PAGE_SIZE`: larga o bastante para misturar nichos, estreita o bastante para não pagar por resultados descartados (~4% de desperdício medido) |
| 2026-08-24 | Modo "Todos os tipos" faz fan-out completo do catálogo | Decisão do usuário: cobertura máxima, já que é a única forma de volumes altos serem alcançáveis | 566 consultas textuais distintas (após deduplicar termos repetidos entre nichos); é a opção mais cara em chamadas à Places API |
| 2026-08-24 | Ordem das categorias no modo "todos" é embaralhada com semente fixa | O catálogo é agrupado por tema, então a ordem natural encheria o primeiro lote só de restaurantes | Determinismo é requisito do cursor; 5 nichos distintos já nas 14 primeiras linhas |
| 2026-08-24 | Redesign mobile-first com barra de navegação inferior + folha de perfil | Layout original era desktop-first (tabelas largas, cabeçalho com todos os controles); a referência pedida usa navegação inferior com item ativo elevado, padrão de app nativo | Cabeçalho de topo e sidebar de filtros viram `lg:`-only; mobile ganha `_bottom_nav.html` + `_profile_sheet.html` incluídos por `base.html` |
| 2026-08-24 | Tailwind compilado com o CLI (`static/app.css`) no lugar do `cdn.tailwindcss.com` | O CDN é o compilador de desenvolvimento (JIT no navegador, ~400KB, sem cache offline garantido); um PWA precisa de CSS estático para o service worker pré-cachear | `package.json`/`tailwind.config.js` novos na raiz; `npm run css` gera o arquivo comitado, `content` escaneia `templates/**` e `static/**/*.js` (classes montadas em template string no `app.js`) |
| 2026-08-24 | Service worker nunca cacheia `/search`, `/historico`, `/export`, `/admin`, `/auth`, `/login`, `/autocomplete` | O banco de leads é compartilhado entre a equipe; uma resposta cacheada no disco do aparelho vazaria dados de um usuário para o próximo que abrir o app naquele dispositivo | `static/sw.js` deixa esses prefixos passarem direto pra rede sem tocar no Cache Storage; só o shell estático (CSS/JS/ícones) e `/offline` são pré-cacheados |
| 2026-08-24 | `/sw.js` é servido pela raiz da aplicação (rota em `main.py`), não por `/static/sw.js` | O escopo de um service worker é limitado ao diretório onde o arquivo é servido; em `/static/` ele não controlaria navegações em `/`, `/historico` etc. | Rota dedicada com `FileResponse` e `Cache-Control: no-cache`; mesma razão para `/manifest.webmanifest` fora de `/static` (o `StaticFiles` não reconhece a extensão e serviria o content-type errado) |
| 2026-08-24 | Ícone do PWA é só o símbolo (chevron), sem o "C" interligado nem o wordmark | O logo fonte (`logotipo-fundo-dark.png`) é um lockup 4000×4000 com muito espaço vazio; testado no ícone de 48–192px, chevron sozinho é o que continua legível | Gerado via `sharp`: recorte da região do símbolo, máscara por cor (mantém só os tons de roxo, remove pixels brancos do "C"/texto), `trim`, padding quadrado e composição sobre fundo `#1E0E3A` |
| 2026-08-24 | Links de Maps/WhatsApp/Exportar deixaram de usar `target="_blank"` | Usuário reportou ficar "preso" fora do PWA instalado depois de abrir Maps/WhatsApp, precisando fechar e reabrir o app. Com o app em `display: standalone`, uma nova aba/janela sai do contexto do PWA sem affordance de volta; navegação na mesma janela deixa o Android mostrar a barra de retorno ao app | `static/app.js` (`buildMapsLink`/`buildWhatsAppButton`) e `templates/historico.html`/`_bottom_nav.html`/`index.html` tiveram o `target="_blank"` removido; `rel="noopener noreferrer"` virou só `rel="noreferrer"` (sem `target`, `noopener` não se aplica) |
| 2026-08-24 | Investigado (sem bug reproduzido) relato de XLSX exportado "só com números" | Gerei um arquivo real com `generate_xlsx` e inspecionei célula a célula: todas as 8 colunas vêm corretas: nome/endereço/telefone sempre têm fallback "Não informado", nunca ficam vazios | Trocado `StreamingResponse(BytesIO)` por `Response(content=xlsx.getvalue())` em `routers/export.py` (elimina a iteração implícita por linha do `BytesIO`); testes de `xlsx_generator` e `GET /export` passaram a checar todas as colunas linha a linha, não só cabeçalho/nome |

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
