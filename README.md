# 🚀 Prospector de Negócios Locais

Ferramenta interna da **Codex Create** 🏢 para prospecção de negócios locais via Google Places API. Permite filtrar empresas por cidade 📍, bairro 🏘️ e tipo de negócio 🏪, identificar leads sem site cadastrado 🔍 e exportar os resultados em planilha `.xlsx` 📊 para o time comercial.

---

## ✨ Funcionalidades

- 🔎 Busca por cidade + bairro com conversão automática de endereço em coordenadas (Geocoding API)
- 🏷️ Filtro por tipo de negócio, com **Todos os tipos** como padrão — varre as 140 categorias de uma vez
- 📦 Busca em lotes de até **1000 leads**, com a tabela preenchendo progressivamente e botão para parar
- 🎯 Toggle **"Somente sem site"** para focar nos leads com maior potencial de conversão
- 🚫 Deduplicação automática — negócios já vistos nunca são salvos duas vezes
- 📋 Resumo pós-busca: novos encontrados · sem site · já vistos antes
- 📥 Exportação XLSX com todas as colunas necessárias para abordagem comercial
- 📜 Histórico paginado com filtro por nome e por presença de site
- 🔐 Login por e-mail e senha, com convites administrados pelo proprietário
- 👤 Perfis locais, papéis `admin`/`member` e bloqueio imediato de acesso
- 📱 Mobile-first, com barra de navegação inferior, listas em cards e formulários colapsáveis abaixo de `lg`/`md`
- 📲 PWA instalável em Android, iOS e desktop, com página offline de fallback

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| ⚙️ Backend | Python 3.12 + FastAPI |
| 🎨 Templates | Jinja2 |
| 💅 Estilização | Tailwind CSS (compilado com o Tailwind CLI, `static/app.css`) |
| 📲 PWA | Manifest + Service Worker próprios (`static/manifest.webmanifest`, `static/sw.js`) |
| 🗄️ Banco de dados | Neon (PostgreSQL serverless) |
| 📦 ORM | SQLAlchemy (síncrono) |
| 🌐 HTTP client | httpx |
| 📑 Exportação | openpyxl |
| 🔐 Autenticação | Clerk + JWT de sessão + cookie HTTP-only |
| 🔗 API externa | Google Places API (New) + Geocoding API |

---

## ✅ Pré-requisitos

- 🐍 Python 3.12+
- 🟢 Node.js 18+ (só para compilar o CSS do Tailwind — não entra no runtime da aplicação)
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

### 4️⃣ Compilar o CSS

O Tailwind roda pelo CLI, não pelo CDN — é preciso gerar `static/app.css` antes de subir o servidor:

```bash
npm install
npm run css
```

Durante o desenvolvimento, `npm run css:watch` recompila a cada alteração. **Sempre rode `npm run css` antes de commitar** qualquer classe Tailwind nova usada em `templates/` ou `static/app.js` — o arquivo gerado é comitado, o `.env`/CI não builda CSS.

### 5️⃣ Aplicar a migração

```bash
alembic upgrade head
```

Ela preserva (ou cria, se o Neon estiver vazio) a tabela legada `businesses`,
cria `app_users` e garante as colunas de avaliação dos leads. Execute-a uma vez
para cada banco Neon antes do deploy.

### 6️⃣ Iniciar o servidor

```bash
uvicorn main:app --reload
```

A aplicação ficará disponível em `http://localhost:8000`.

> 💡 A tabela `businesses` continua sendo criada automaticamente no banco na primeira execução.

> ⚠️ **Atenção:** sempre ative o venv (`source .venv/bin/activate`) antes de rodar o servidor em uma nova sessão do terminal.

### 7️⃣ Testes

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

- ⏱️ O plano **Hobby** (gratuito) tem timeout de **10 segundos** por requisição. Por isso a busca é feita **em lotes**: o navegador chama `POST /search` várias vezes, cada uma devolvendo até 100 leads mais o `cursor` do próximo lote, e a tabela vai sendo preenchida progressivamente. Cada request isolada fica bem abaixo do limite mesmo numa busca de 1000 resultados. Detalhes em [Busca em lotes](#-busca-em-lotes).
- 💸 O modo **Todos os tipos** varre as 140 categorias do catálogo (566 consultas textuais distintas). É a opção mais cara em chamadas à Places API — meça o consumo antes de rodar buscas de 1000 em produção.
- 🗄️ A tabela `businesses` é criada automaticamente no primeiro acesso (via `create_all` no startup).
- 📂 Arquivos estáticos (`app.js`, `app.css`, ícones do PWA) são servidos pelo próprio FastAPI — sem necessidade de configuração extra.
- 🎨 O `vercel.json` só builda `main.py` (`@vercel/python`) — não roda `npm install`/`npm run css`. **Rode `npm run css` e commite `static/app.css` antes de cada deploy** que mude alguma classe Tailwind.

---

## 📁 Estrutura de Pastas

```
prospector/
├── main.py                   # 🚀 Instância do FastAPI, routers e rotas do PWA
├── .env                      # 🔒 Variáveis de ambiente (não commitado)
├── .env.example              # 📄 Template do .env
├── requirements.txt          # 📦 Dependências Python
├── package.json              # 📦 Dependência única: tailwindcss (build do CSS)
├── tailwind.config.js        # 🎨 Paleta `brand` e conteúdo escaneado pelo Tailwind
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
│   ├── base.html             # 🏗️ Layout base, cabeçalho e inclusão da barra inferior
│   ├── _bottom_nav.html      # 📱 Barra de navegação inferior (mobile)
│   ├── _profile_sheet.html   # 📱 Folha de perfil: tema, instalar app, sair
│   ├── offline.html          # 📴 Fallback servido pelo service worker sem rede
│   ├── index.html            # 🔍 Página de busca
│   └── historico.html        # 📋 Página de histórico
└── static/
    ├── src/input.css         # 🎨 Fonte do Tailwind (`npm run css` gera app.css)
    ├── app.css                # 🎨 CSS compilado, comitado
    ├── app.js                 # ⚡ AJAX e renderização de resultados (tabela + cards)
    ├── pwa.js                 # 📲 Registro do service worker e fluxo de instalação
    ├── sw.js                  # 📲 Service worker (cache do shell estático + /offline)
    ├── manifest.webmanifest   # 📲 Manifest do PWA
    └── icons/                 # 📲 Ícones gerados a partir do símbolo da marca
```

---

## 🌐 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | 🏠 Página principal com formulário de busca |
| `POST` | `/search` | 🔎 Executa **um lote** da busca e salva os novos leads ([detalhes](#-busca-em-lotes)) |
| `GET` | `/export` | 📥 Download do XLSX com todos os leads |
| `GET` | `/export?only_without_website=true` | 📥 Download apenas dos leads sem site |
| `GET` | `/historico` | 📜 Histórico paginado de leads salvos |
| `GET` | `/login` | Tela Clerk de entrada |
| `POST` | `/auth/session` | Troca JWT Clerk por sessão HTTP-only local |
| `DELETE` | `/auth/session` | Encerra a sessão local |
| `POST` | `/webhooks/clerk` | Sincroniza perfis recebidos do Clerk |
| `GET` | `/admin/users` | Gestão de usuários, somente administrador |
| `GET` | `/manifest.webmanifest` | 📲 Manifest do PWA |
| `GET` | `/sw.js` | 📲 Service worker (servido da raiz para controlar toda a navegação) |
| `GET` | `/offline` | 📴 Página de fallback exibida pelo service worker sem conexão |

---

## 📲 PWA — instalar o app

O Prospector pode ser instalado como app em Android, iOS e desktop:

- **Android / Chrome / Edge (desktop):** abra o menu **Perfil** na barra inferior (ou o
  ícone de tema no cabeçalho, no desktop) e toque em **Instalar app**. O botão só aparece
  depois que o navegador dispara o evento `beforeinstallprompt`.
- **iOS (Safari):** o Safari não oferece esse evento — o mesmo botão **Instalar app** mostra
  o passo a passo: toque em **Compartilhar** e depois em **Adicionar à Tela de Início**.

O app funciona offline apenas para a casca estática (abrir sem rede mostra a página
`/offline`) — buscas, histórico e exportação sempre exigem conexão, porque dependem do
banco de dados compartilhado pela equipe.

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

A primeira opção da lista é **Todos os tipos** (valor `all`), que também é o
padrão do formulário. Ela não é uma categoria real: monta um plano com os
termos de **todas** as categorias, embaralhados com semente fixa e
intercalados, para que os primeiros resultados já venham de nichos variados.
Cada lead continua sendo salvo com a categoria real que o encontrou, então o
filtro do histórico segue funcionando normalmente.

---

## 📦 Busca em lotes

`POST /search` executa **um lote** por chamada, não a busca inteira:

| Campo | Direção | Papel |
|---|---|---|
| `quantity` | entrada | Alvo total da busca (5 a 1000) |
| `batch_size` | entrada | Máximo de leads deste lote (5 a 200, padrão 100) |
| `cursor` | entrada | Índice do próximo termo do plano de busca (0 no primeiro lote) |
| `cursor` | saída | Cursor do lote seguinte — `null` quando o plano acabou |

O `static/app.js` repete a chamada até atingir `quantity`, receber `cursor: null`
ou acumular 3 lotes seguidos sem nada novo (cidade já varrida). Cada termo do
plano é esgotado dentro de um lote — por isso o cursor é apenas um índice e
nenhum `pageToken` do Google trafega pelo navegador.

> ⚠️ **`quantity` é um teto, não uma promessa.** A Places API devolve no máximo
> 20 lugares por página e 3 páginas por termo — 60 por consulta textual. Um
> nicho estreito num bairro pequeno se esgota bem antes de 1000; a busca
> simplesmente termina com `cursor: null` e o que existir. Volumes altos são
> alcançáveis principalmente no modo **Todos os tipos**.

---

## 📌 Observações

- 💰 A Places API (New) exige billing ativo no Google Cloud, mas há crédito gratuito de $200/mês.
- 📄 O arquivo XLSX é gerado em memória (`BytesIO`) — nenhum arquivo temporário é salvo em disco.
- 🔒 O `.env` está no `.gitignore` e nunca deve ser commitado.

---

*🔐 Uso interno — Codex Create*
