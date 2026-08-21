# 🚀 Prospector de Negócios Locais

Ferramenta interna da **Codex Create** 🏢 para prospecção de negócios locais via Google Places API. Permite filtrar empresas por cidade 📍, bairro 🏘️ e tipo de negócio 🏪, identificar leads sem site cadastrado 🔍 e exportar os resultados em planilha `.xlsx` 📊 para o time comercial.

---

## ✨ Funcionalidades

- 🔎 Busca por cidade + bairro com conversão automática de endereço em coordenadas (Geocoding API)
- 🏷️ Filtro por tipo de negócio (restaurante, barbearia, salão de beleza, farmácia, etc.)
- 🎯 Toggle **"Somente sem site"** para focar nos leads com maior potencial de conversão
- 🚫 Deduplicação automática — negócios já vistos nunca são salvos duas vezes
- 📋 Resumo pós-busca: novos encontrados · sem site · já vistos antes
- 📥 Exportação XLSX com todas as colunas necessárias para abordagem comercial
- 📜 Histórico paginado com filtro por nome e por presença de site
- 🔐 Login por e-mail e senha, com convites administrados pelo proprietário
- 👤 Perfis locais, papéis `admin`/`member` e bloqueio imediato de acesso

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| ⚙️ Backend | Python 3.12 + FastAPI |
| 🎨 Templates | Jinja2 |
| 💅 Estilização | Tailwind CSS (CDN) |
| 🗄️ Banco de dados | Neon (PostgreSQL serverless) |
| 📦 ORM | SQLAlchemy (síncrono) |
| 🌐 HTTP client | httpx |
| 📑 Exportação | openpyxl |
| 🔐 Autenticação | Clerk + JWT de sessão + cookie HTTP-only |
| 🔗 API externa | Google Places API (New) + Geocoding API |

---

## ✅ Pré-requisitos

- 🐍 Python 3.12+
- ☁️ Conta no [Neon](https://neon.tech) (free tier disponível)
- ☁️ Projeto no Google Cloud com **Places API (New)** e **Geocoding API** habilitadas
- 🔐 Aplicação no [Clerk](https://clerk.com) com login por e-mail e senha

---

## ⚙️ Configuração

### 1️⃣ Variáveis de ambiente

Copie o arquivo de exemplo e preencha as chaves:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
GOOGLE_MAPS_API_KEY=sua_chave_aqui
DATABASE_URL=postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require
APP_ENV=development
APP_URL=http://localhost:8000
SESSION_SECRET_KEY=gere_uma_chave_longa_e_aleatoria
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_FRONTEND_API_URL=https://seu-frontend-api.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_...
CLERK_JWT_KEY=chave_publica_jwt_do_clerk
CLERK_WEBHOOK_SIGNING_SECRET=whsec_...
CLERK_ADMIN_USER_ID=user_...
```

### 2️⃣ Criar o ambiente virtual

Debian/Ubuntu modernos bloqueiam instalação de pacotes Python fora de um virtualenv. Crie e ative antes de instalar qualquer dependência:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> No Windows: `.venv\Scripts\activate`

O prompt do terminal vai mostrar `(.venv)` quando o ambiente estiver ativo. Para sair: `deactivate`.

### 3️⃣ Instalar dependências

Com o venv ativo:

```bash
pip install -r requirements.txt
```

### 4️⃣ Aplicar a migração

```bash
alembic upgrade head
```

Ela preserva (ou cria, se o Neon estiver vazio) a tabela legada `businesses`,
cria `app_users` e garante as colunas de avaliação dos leads. Execute-a uma vez
para cada banco Neon antes do deploy.

### 5️⃣ Iniciar o servidor

```bash
uvicorn main:app --reload
```

A aplicação ficará disponível em `http://localhost:8000`.

> 💡 A tabela `businesses` continua sendo criada automaticamente no banco na primeira execução.

> ⚠️ **Atenção:** sempre ative o venv (`source .venv/bin/activate`) antes de rodar o servidor em uma nova sessão do terminal.

### 6️⃣ Testes

Instale as dependências de desenvolvimento e rode a suíte (SQLite em arquivo temporário; Google e Neon não são chamados):

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## 🔐 Configuração do Clerk

O passo a passo completo para criar a instância, preparar o primeiro
administrador, configurar o webhook e publicar na Vercel está em
[`SETUP_AUTENTICACAO.md`](./SETUP_AUTENTICACAO.md).

1. Em **User & Authentication**, habilite entrada por **e-mail e senha** e
   exija a verificação de e-mail.
2. Em **Access mode**, selecione **Invite-only**. Mantenha a capacidade de
   cadastro por e-mail habilitada, pois ela é usada para concluir convites;
   esse modo impede cadastros sem convite.
3. Crie manualmente no Dashboard a conta inicial do administrador. Copie o
   `user_id` dela para `CLERK_ADMIN_USER_ID`.
4. No painel de chaves da API, copie a chave pública JWT de verificação para
   `CLERK_JWT_KEY`. Em **Allowed origins**, inclua exatamente o valor de
   `APP_URL` para desenvolvimento e produção.
5. Crie um webhook para `https://seu-dominio/webhooks/clerk`, assine os
   eventos `user.created`, `user.updated` e `user.deleted`, e salve o segredo
   em `CLERK_WEBHOOK_SIGNING_SECRET`.

O administrador convida novos integrantes em `/admin/users`. O Clerk envia o
link para definição de senha; não existe rota de cadastro público. Os perfis
novos entram como `member`. Membros podem buscar, consultar o histórico e
exportar leads; apenas o administrador pode gerir usuários ou excluir leads.

---

## 🚢 Deploy na Vercel

O projeto já inclui o `vercel.json` configurado. O banco Neon é serverless e compatível nativamente com a Vercel.

### 1️⃣ Subir para o GitHub

Crie um repositório e suba o conteúdo desta pasta (não a pasta pai):

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

> 🔒 O `.env` está no `.gitignore` e **não será enviado**. As variáveis serão configuradas direto na Vercel.

### 2️⃣ Conectar na Vercel

1. Acesse [vercel.com](https://vercel.com) → **Add New Project**
2. Importe o repositório do GitHub
3. Em **Framework Preset**, selecione **Other**
4. Clique em **Deploy** (o `vercel.json` já configura tudo automaticamente)

> 📁 Se o repositório contiver a pasta `prospector/` como subdiretório (e não na raiz), configure o campo **Root Directory** para `prospector` nas opções do projeto antes de fazer o deploy.

### 3️⃣ Configurar variáveis de ambiente

No painel do projeto na Vercel: **Settings → Environment Variables**

| Nome | Valor |
|---|---|
| `GOOGLE_MAPS_API_KEY` | Sua chave do Google Cloud |
| `DATABASE_URL` | String de conexão do Neon |
| `APP_ENV` | `production` na Vercel |
| `APP_URL` | URL publica exata da aplicacao, sem barra final |
| `SESSION_SECRET_KEY` | Segredo aleatorio para o cookie local |
| `CLERK_PUBLISHABLE_KEY` | Chave publica do Clerk |
| `CLERK_FRONTEND_API_URL` | Frontend API URL da instancia Clerk |
| `CLERK_SECRET_KEY` | Chave secreta do Backend API do Clerk |
| `CLERK_JWT_KEY` | Chave publica para validar JWTs de sessao |
| `CLERK_WEBHOOK_SIGNING_SECRET` | Segredo Svix do webhook Clerk |
| `CLERK_ADMIN_USER_ID` | ID Clerk da conta inicial de administrador |

Rode `alembic upgrade head` com o mesmo `DATABASE_URL` antes do primeiro
deploy. Após adicionar as variáveis, clique em **Redeploy** para aplicar.

### 📌 Observações sobre a Vercel

- ⏱️ O plano **Hobby** (gratuito) tem timeout de **10 segundos** por requisição. As chamadas ao Place Details são feitas em paralelo (`asyncio.gather`), então buscas de até 100 resultados tipicamente completam em 2–5 segundos. O gargalo real é a paginação do Nearby Search (sequencial por limitação da API), que adiciona ~200ms por página de 20 resultados.
- 🗄️ A tabela `businesses` é criada automaticamente no primeiro acesso (via `create_all` no startup).
- 📂 Arquivos estáticos (`app.js`) são servidos pelo próprio FastAPI — sem necessidade de configuração extra.

---

## 📁 Estrutura de Pastas

```
prospector/
├── main.py                   # 🚀 Instância do FastAPI e routers
├── .env                      # 🔒 Variáveis de ambiente (não commitado)
├── .env.example              # 📄 Template do .env
├── requirements.txt          # 📦 Dependências
├── database/
│   ├── connection.py         # 🔌 Engine e SessionLocal
│   └── models.py             # 📊 Modelo ORM da tabela businesses
├── alembic/                  # 🗃️ Migrações do banco, incluindo app_users
├── routers/
│   ├── search.py             # 🔎 POST /search
│   ├── export.py             # 📥 GET /export
│   └── history.py            # 📜 GET /historico
│   ├── auth.py               # 🔐 Login e sessão HTTP-only
│   ├── users.py              # 👤 Administração de usuários e convites
│   └── webhooks.py           # 🔗 Sincronização de usuários do Clerk
├── services/
│   ├── places.py             # 🗺️ Nearby Search + Place Details
│   ├── geocoding.py          # 📍 Cidade/bairro → lat/lng
│   ├── deduplication.py      # 🚫 Verificação de place_id no banco
│   └── xlsx_generator.py     # 📑 Geração do XLSX em memória
├── templates/
│   ├── base.html             # 🏗️ Layout base com Tailwind
│   ├── index.html            # 🔍 Página de busca
│   └── historico.html        # 📋 Página de histórico
└── static/
    └── app.js                # ⚡ AJAX e renderização de resultados
```

---

## 🌐 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | 🏠 Página principal com formulário de busca |
| `POST` | `/search` | 🔎 Executa busca e salva novos leads |
| `GET` | `/export` | 📥 Download do XLSX com todos os leads |
| `GET` | `/export?only_without_website=true` | 📥 Download apenas dos leads sem site |
| `GET` | `/historico` | 📜 Histórico paginado de leads salvos |
| `GET` | `/login` | Tela Clerk de entrada |
| `POST` | `/auth/session` | Troca JWT Clerk por sessão HTTP-only local |
| `DELETE` | `/auth/session` | Encerra a sessão local |
| `POST` | `/webhooks/clerk` | Sincroniza perfis recebidos do Clerk |
| `GET` | `/admin/users` | Gestão de usuários, somente administrador |

---

## 🏪 Tipos de Negócio Suportados

O campo **Tipo de Negócio** é um combobox pesquisável com 140 opções. Além dos
tipos oficiais da Places API, ele inclui 92 nichos comerciais — como móveis
planejados, reformas, serviços automotivos, eventos, saúde e construção — e
os respectivos termos de busca fornecidos pelo time comercial.

O catálogo está centralizado em
[`services/business_type_catalog.py`](./services/business_type_catalog.py).
Para categorias sem um tipo oficial da Places API, a busca usa os termos do
catálogo sem enviar um `includedType` inválido.

---

## 📌 Observações

- 💰 A Places API (New) exige billing ativo no Google Cloud, mas há crédito gratuito de $200/mês.
- 📄 O arquivo XLSX é gerado em memória (`BytesIO`) — nenhum arquivo temporário é salvo em disco.
- 🔒 O `.env` está no `.gitignore` e nunca deve ser commitado.

---

*🔐 Uso interno — Codex Create*
