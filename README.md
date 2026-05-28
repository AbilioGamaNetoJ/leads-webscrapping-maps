# Prospector de Negócios Locais

Ferramenta interna da **Codex Create** para prospecção de negócios locais via Google Places API. Permite filtrar empresas por cidade, bairro e tipo de negócio, identificar leads sem site cadastrado e exportar os resultados em planilha `.xlsx` para o time comercial.

---

## Funcionalidades

- Busca por cidade + bairro com conversão automática de endereço em coordenadas (Geocoding API)
- Filtro por tipo de negócio (restaurante, barbearia, salão de beleza, farmácia, etc.)
- Toggle **"Somente sem site"** para focar nos leads com maior potencial de conversão
- Deduplicação automática — negócios já vistos nunca são salvos duas vezes
- Resumo pós-busca: novos encontrados · sem site · já vistos antes
- Exportação XLSX com todas as colunas necessárias para abordagem comercial
- Histórico paginado com filtro por nome e por presença de site

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Templates | Jinja2 |
| Estilização | Tailwind CSS (CDN) |
| Banco de dados | Neon (PostgreSQL serverless) |
| ORM | SQLAlchemy (síncrono) |
| HTTP client | httpx |
| Exportação | openpyxl |
| API externa | Google Places API (New) + Geocoding API |

---

## Pré-requisitos

- Python 3.12+
- Conta no [Neon](https://neon.tech) (free tier disponível)
- Projeto no Google Cloud com **Places API (New)** e **Geocoding API** habilitadas

---

## Configuração

### 1. Variáveis de ambiente

Copie o arquivo de exemplo e preencha as chaves:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
GOOGLE_MAPS_API_KEY=sua_chave_aqui
DATABASE_URL=postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require
```

### 2. Criar o ambiente virtual

Debian/Ubuntu modernos bloqueiam instalação de pacotes Python fora de um virtualenv. Crie e ative antes de instalar qualquer dependência:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> No Windows: `.venv\Scripts\activate`

O prompt do terminal vai mostrar `(.venv)` quando o ambiente estiver ativo. Para sair: `deactivate`.

### 3. Instalar dependências

Com o venv ativo:

```bash
pip install -r requirements.txt
```

### 4. Iniciar o servidor

```bash
uvicorn main:app --reload
```

A aplicação ficará disponível em `http://localhost:8000`.

> A tabela `businesses` é criada automaticamente no banco na primeira execução.

> **Atenção:** sempre ative o venv (`source .venv/bin/activate`) antes de rodar o servidor em uma nova sessão do terminal.

---

## Deploy na Vercel

O projeto já inclui o `vercel.json` configurado. O banco Neon é serverless e compatível nativamente com a Vercel.

### 1. Subir para o GitHub

Crie um repositório e suba o conteúdo desta pasta (não a pasta pai):

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

> O `.env` está no `.gitignore` e **não será enviado**. As variáveis serão configuradas direto na Vercel.

### 2. Conectar na Vercel

1. Acesse [vercel.com](https://vercel.com) → **Add New Project**
2. Importe o repositório do GitHub
3. Em **Framework Preset**, selecione **Other**
4. Clique em **Deploy** (o `vercel.json` já configura tudo automaticamente)

> Se o repositório contiver a pasta `prospector/` como subdiretório (e não na raiz), configure o campo **Root Directory** para `prospector` nas opções do projeto antes de fazer o deploy.

### 3. Configurar variáveis de ambiente

No painel do projeto na Vercel: **Settings → Environment Variables**

| Nome | Valor |
|---|---|
| `GOOGLE_MAPS_API_KEY` | Sua chave do Google Cloud |
| `DATABASE_URL` | String de conexão do Neon |

Após adicionar as variáveis, clique em **Redeploy** para aplicar.

### Observações sobre a Vercel

- O plano **Hobby** (gratuito) tem timeout de **10 segundos** por requisição. As chamadas ao Place Details são feitas em paralelo (`asyncio.gather`), então buscas de até 100 resultados tipicamente completam em 2–5 segundos. O gargalo real é a paginação do Nearby Search (sequencial por limitação da API), que adiciona ~200ms por página de 20 resultados.
- A tabela `businesses` é criada automaticamente no primeiro acesso (via `create_all` no startup).
- Arquivos estáticos (`app.js`) são servidos pelo próprio FastAPI — sem necessidade de configuração extra.

---

## Estrutura de Pastas

```
prospector/
├── main.py                   # Instância do FastAPI e routers
├── .env                      # Variáveis de ambiente (não commitado)
├── .env.example              # Template do .env
├── requirements.txt
├── database/
│   ├── connection.py         # Engine e SessionLocal
│   └── models.py             # Modelo ORM da tabela businesses
├── routers/
│   ├── search.py             # POST /search
│   ├── export.py             # GET /export
│   └── history.py            # GET /historico
├── services/
│   ├── places.py             # Nearby Search + Place Details
│   ├── geocoding.py          # Cidade/bairro → lat/lng
│   ├── deduplication.py      # Verificação de place_id no banco
│   └── xlsx_generator.py     # Geração do XLSX em memória
├── templates/
│   ├── base.html             # Layout base com Tailwind
│   ├── index.html            # Página de busca
│   └── historico.html        # Página de histórico
└── static/
    └── app.js                # AJAX e renderização de resultados
```

---

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Página principal com formulário de busca |
| `POST` | `/search` | Executa busca e salva novos leads |
| `GET` | `/export` | Download do XLSX com todos os leads |
| `GET` | `/export?only_without_website=true` | Download apenas dos leads sem site |
| `GET` | `/historico` | Histórico paginado de leads salvos |

---

## Tipos de Negócio Suportados

| Label | Valor (Places API) |
|---|---|
| Restaurante | `restaurant` |
| Barbearia | `barber_shop` |
| Loja de Roupas | `clothing_store` |
| Salão de Beleza | `beauty_salon` |
| Farmácia | `pharmacy` |
| Padaria | `bakery` |
| Academia | `gym` |
| Supermercado | `supermarket` |
| Petshop | `pet_store` |
| Clínica / Consultório | `doctor` |

---

## Observações

- A Places API (New) exige billing ativo no Google Cloud, mas há crédito gratuito de $200/mês.
- O arquivo XLSX é gerado em memória (`BytesIO`) — nenhum arquivo temporário é salvo em disco.
- O `.env` está no `.gitignore` e nunca deve ser commitado.

---

*Uso interno — Codex Create*
