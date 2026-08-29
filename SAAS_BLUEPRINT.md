# Blueprint — SaaS de Prospecção de Leads Locais

> Documento de implementação para portar o Prospector (ferramenta interna da Codex Create)
> para um SaaS multi-tenant. Consolida as decisões e os números levantados durante a
> investigação do incidente de custo de agosto/2026, em que uma fatura de R$ 1.292,34 foi
> gerada por duas sessões de busca.
>
> **Estado dos números:** o custo por lead pós-correção ainda **não foi medido em produção**.
> Onde aparece um valor de custo, está marcado como medido ou estimado. Não construa
> precificação final em cima dos estimados sem medir antes (ver [Medição obrigatória](#medição-obrigatória)).

---

## 1. O produto

Ferramenta de prospecção de negócios locais. O usuário busca por cidade, bairro e categoria;
o sistema devolve empresas com nome, endereço, telefone, avaliação e — o diferencial
comercial — **se a empresa tem ou não site**. Exporta em planilha para o time de vendas.

O nicho é agência digital e prestador de serviço que vende presença online. "Negócio sem
site" é o lead qualificado do produto.

---

## 2. A decisão que define a arquitetura: BYOK

**O modelo é BYOK — Bring Your Own Key. O cliente cadastra a própria chave da Google Maps
Platform e o Google fatura ele diretamente.**

### Por quê

Os Termos da Google Maps Platform restringem armazenamento e redistribuição do conteúdo do
Places. O `place_id` pode ser guardado indefinidamente; nome, telefone, endereço e site, não —
há limite de retenção e cláusulas contra recriar produtos do Google ou redistribuir os dados.

Como ferramenta interna, isso é área cinzenta tolerável. **Como SaaS vendido a terceiros,
armazenar esses campos permanentemente e exportá-los em planilha é exatamente o que os termos
miram.**

BYOK resolve os dois problemas de uma vez:

| | Com BYOK | Você fornecendo o dado |
|---|---|---|
| Custo variável de API | **Zero** | Seu |
| Risco de redistribuição | **Zero** — o dado passa pela conta do cliente | Alto |
| Margem | Software puro (>90%) | 75–85% |
| Capital necessário | Nenhum | Contrato de licenciamento |
| Fricção de onboarding | **Alta** — cliente cria conta no GCP | Nenhuma |

O único custo real do BYOK é a fricção de cadastro. Mitigue com onboarding guiado
(seção 8), não trocando o modelo.

### Alternativas avaliadas e descartadas para o v1

- **Licenciar do Google** — vale a conversa com o comercial, mas é lento e sem garantia para
  um player pequeno.
- **Fornecedor licenciado** (Foursquare Places API, Data Axle, SafeGraph) — contrato com
  mínimo mensal. Só faz sentido com receita recorrente já estabelecida.
- **Datasets abertos** — [Foursquare OS Places](https://opensource.foursquare.com/os-places/)
  (106M POIs, Apache 2.0) e [Overture Maps Places](https://docs.overturemaps.org/guides/places/)
  (61M+, CDLA Permissive 2.0) são gratuitos e redistribuíveis. **Mas `website` e `phone` são
  esparsos para negócios pequenos no Brasil** — justamente os dois campos que o produto
  monetiza. Ausência de dado não é ausência de site; vender lead errado destrói o produto mais
  rápido que qualquer custo de API. Servem como camada de descoberta no médio prazo, não como
  fonte única.
- **Scraping (ScrapeGraphAI e similares)** — extrai de uma página que você já tem; não
  descobre negócios. Exigiria raspar o Google Maps, o que viola os termos. Custo de LLM por
  página (R$ 1,29 a R$ 6,44 por 100 leads, dependendo do modelo) empata ou supera a API oficial.

---

## 3. Stack

Herda do projeto atual o que funciona, troca o que não escala para multi-tenant.

| Camada | Escolha | Observação |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Mantém |
| ORM | SQLAlchemy | Mantém |
| Banco | PostgreSQL (Neon ou Supabase) | Precisa de RLS ou escopo por tenant na aplicação |
| Fila | Redis + RQ, ou Celery | **Novo** — busca não pode mais rodar dentro do request |
| Frontend | Jinja2 + Tailwind, ou Next.js | Jinja serve; Next se quiser app mais rico |
| Auth | Clerk | Mantém — já suporta organizações |
| Pagamento | Stripe (internacional) ou Asaas/Pagar.me (Brasil, Pix) | Pix é decisivo no mercado BR |
| Exportação | openpyxl | Mantém |
| Hospedagem | Railway, Fly.io ou VPS | **Sair da Vercel** — o timeout de 10s foi causa raiz de parte do desperdício |
| Observabilidade | Sentry + tabela própria de custo | Ver seção 7 |

### Por que sair da Vercel

O projeto atual roda cada lote dentro de um request HTTP, com o limite de 10s do plano
Hobby. Isso forçou o design de lotes e contribuiu para chamadas pagas desperdiçadas quando a
função morria com requisições em voo (17% de taxa de erro observada na Places API).

No SaaS, **busca vira job assíncrono**: o usuário dispara, acompanha o progresso, recebe o
resultado. Sem teto de tempo, sem lote artificial, sem chamada paga jogada fora por timeout.

---

## 4. Modelo de dados

```sql
-- Tenant e chave do cliente
CREATE TABLE tenants (
  id              uuid PRIMARY KEY,
  name            text NOT NULL,
  plan            text NOT NULL DEFAULT 'trial',
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE tenant_api_keys (
  tenant_id       uuid PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
  -- NUNCA em texto puro. Envelope encryption (KMS) ou pgcrypto com chave fora do banco.
  encrypted_key   bytea NOT NULL,
  last_validated  timestamptz,
  status          text NOT NULL DEFAULT 'unverified'  -- unverified | active | invalid | quota_exceeded
);

-- Leads, agora escopados por tenant
CREATE TABLE businesses (
  id                    bigserial PRIMARY KEY,
  tenant_id             uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  place_id              text NOT NULL,
  name                  text NOT NULL,
  address               text,
  phone                 text,
  maps_url              text,
  has_website           boolean NOT NULL DEFAULT false,
  rating                real,
  user_ratings_total    integer,
  business_type         text,
  -- Novo: sem isso não dá para saber quais regiões já estão esgotadas
  search_city           text,
  search_neighborhood   text,
  created_at            timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, place_id)   -- deduplicação POR CLIENTE, não global
);
CREATE INDEX ON businesses (tenant_id, created_at DESC);
CREATE INDEX ON businesses (tenant_id, search_city, search_neighborhood);

-- Jobs de busca
CREATE TABLE search_jobs (
  id                uuid PRIMARY KEY,
  tenant_id         uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  status            text NOT NULL,   -- queued | running | done | failed | aborted
  params            jsonb NOT NULL,
  credits_reserved  integer NOT NULL DEFAULT 0,
  credits_charged   integer NOT NULL DEFAULT 0,
  api_calls_used    integer NOT NULL DEFAULT 0,
  leads_delivered   integer NOT NULL DEFAULT 0,
  created_at        timestamptz NOT NULL DEFAULT now(),
  finished_at       timestamptz
);

-- Livro-razão de créditos. Append-only: saldo é soma, nunca UPDATE.
CREATE TABLE credit_ledger (
  id           bigserial PRIMARY KEY,
  tenant_id    uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  amount       integer NOT NULL,        -- positivo credita, negativo debita
  kind         text NOT NULL,           -- plan_grant | topup | search_debit | refund | expiry
  bucket       text NOT NULL,           -- plan | topup  (define ordem de consumo e validade)
  job_id       uuid REFERENCES search_jobs(id),
  expires_at   timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON credit_ledger (tenant_id, created_at DESC);
```

**Três decisões embutidas aí:**

1. `UNIQUE (tenant_id, place_id)` — deduplicação por cliente. Dois clientes buscando a mesma
   região recebem os mesmos leads, cada um pagando com a própria chave. Não há cache
   compartilhado, o que também mantém você fora do problema de redistribuição.
2. `credit_ledger` append-only — saldo é `SUM(amount)`. Nunca faça `UPDATE saldo`. Auditoria,
   estorno e extrato saem de graça.
3. `search_city` / `search_neighborhood` — sem isso é impossível responder "quais regiões já
   varri?", que é a informação que evita rebusca (a operação mais cara que existe, ver seção 6).

---

## 5. O motor de busca — regras de custo

Esta seção é a mais importante do documento. **Cada regra abaixo foi aprendida com a fatura de
R$ 1.292,34.** O código antigo gastava 3,45 chamadas de busca cobradas por lead entregue.

### 5.1 Field mask: peça tudo na busca

Os campos `websiteUri`, `internationalPhoneNumber` e `googleMapsUri` **existem no Text Search**
e entram no mesmo SKU Enterprise que `rating` e `userRatingCount` já forçam. Pedi-los na busca
**não encarece a chamada** e elimina a necessidade de Place Details, que é uma requisição paga
(US$ 0,020) por empresa.

```python
SEARCH_FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.rating,places.userRatingCount,"
    "places.websiteUri,places.internationalPhoneNumber,places.googleMapsUri,"
    "nextPageToken"
)
```

Place Details vira **fallback**, chamado só para os poucos resultados que voltam sem telefone.

> Antes de confiar nisso em produção, valide com dados reais que o Text Search preenche
> `websiteUri` com a mesma completude do Place Details. Divergência nesse campo classifica lead
> errado, o que é pior que o custo. Existe script para isso em `scripts/validate_search_fields.py`.

### 5.2 Página é cobrada por requisição, não por resultado

Uma página custa o mesmo trazendo 20 lugares ou 3. **Sempre peça `maxResultCount = 20`**, mesmo
quando faltam poucos leads para fechar o lote. O código antigo pedia `restante - coletados`,
pagando página cheia por 4 candidatos.

### 5.3 Não pagine antes de saber se precisa

Busque a **primeira página de todos os termos da onda**, verifique se já basta, e só então
pagine. O código antigo drenava as 3 páginas de cada termo de uma vez — até 300 lugares
buscados para preencher 100 vagas, com o excedente descartado já pago.

### 5.4 Pare em região estéril

Se N ondas consecutivas não trouxerem nenhum lead inédito, aborte o job. Numa região já varrida
o motor seguia pagando páginas até esgotar o limite de ondas.

### 5.5 Sobreposição de termos é o desperdício que sobra

O catálogo transforma cada nicho em vários termos. "REFORMAS" vira 9 consultas
(`Empreiteiro`, `Empreiteiro geral`, `Empreiteiro de reformas`, ...) que devolvem
**praticamente as mesmas empresas**. Você paga 9 chamadas para colher o conteúdo de 2 ou 3.

Nenhuma correção de código resolve isso — é do catálogo. A solução é instrumentar: registre
quantos leads **inéditos** cada termo trouxe e pode os redundantes com dado, não por intuição.

### 5.6 Custo por lead varia com a região

A deduplicação protege a planilha do cliente, **não protege o custo** — o dinheiro já saiu na
chamada de busca.

| Situação | Página devolve | Leads novos | Custo/lead* |
|---|---|---|---|
| Cidade grande virgem (raio 15 km) | 20 | 20 | R$ 0,009 |
| Bairro pequeno virgem (raio 2 km) | ~5 | 5 | R$ 0,036 |
| Região 50% varrida | 20 | 10 | R$ 0,018 |
| Região 90% varrida | 20 | 2 | R$ 0,090 |
| Região esgotada | 20 | 0 | infinito |

\* *estimado, a R$ 0,18 por página de Text Search Enterprise*

**Rebuscar região já coberta é a operação mais cara do sistema.** Guie o usuário para regiões
novas e avise quando uma região estiver esgotada — é bom para ele e para a margem.

---

## 6. Guardrails

Um teto por si só não basta; são três camadas.

| Camada | O que faz | Onde |
|---|---|---|
| **Cota diária por API** | Trava real — a API para de responder | Console do cliente (guie no onboarding) |
| **Orçamento com alerta** | Só notifica, **não trava** | Console do cliente |
| **Teto de chamadas por job** | Aborta a busca que não está rendendo | Seu código |

> **O orçamento do Google Cloud não interrompe gasto.** Ele manda e-mail em 50%, 90% e 100% e o
> consumo continua. No incidente de agosto, um orçamento de R$ 200 teria gerado três e-mails e a
> mesma fatura de R$ 1.292. Só a cota diária trava de fato.

O teto por job protege sua margem no modelo gerenciado e protege o bolso do cliente no BYOK:

```python
MAX_API_CALLS_PER_JOB = 200        # ~R$ 36 no pior caso
MAX_BARREN_WAVES = 3               # ondas seguidas sem lead inédito
```

Ao abortar, devolva mensagem útil: *"essa região já foi varrida por você, tente outra cidade ou
categoria"* — não um erro genérico.

---

## 7. Observabilidade de custo

O que faltou em agosto não foi alerta, foi **visibilidade**. Registre, por job:

- chamadas de Text Search e de Place Details
- leads entregues e duplicados descartados
- custo estimado em R$
- cidade, bairro e categoria

Com isso você responde, a qualquer momento: custo por lead, por cliente, por região e por
termo do catálogo. É o painel que transforma "a fatura veio alta" em "o termo X gasta 12
chamadas e traz 1 lead novo".

---

## 8. Onboarding BYOK

A maior fricção do modelo. Trate como funcionalidade de produto, não como página de ajuda.

1. Passo a passo com screenshots: criar projeto no GCP → ativar Places API (New) e Geocoding →
   gerar chave
2. **Definir a cota diária junto com o usuário**, dentro do fluxo. Sugira um valor e explique
   em reais o que ele significa
3. Restringir a chave às APIs usadas
4. Validar a chave com uma chamada de teste real antes de aceitar o cadastro
5. Monitorar: se a chave começar a retornar 403 ou estourar cota, avise o cliente **antes** de
   ele descobrir com busca quebrada

Uma checagem de saúde diária das chaves cadastradas evita a maior parte dos chamados de suporte.

---

## 9. Preços

### 9.1 Planos BYOK — modelo recomendado para o v1

O cliente paga o Google. Você vende software, e o preço reflete valor de uso, não custo de dado.

| Plano | Buscas/mês | Usuários | Preço |
|---|---|---|---|
| **Starter** | 20 | 1 | R$ 97 |
| **Pro** | 100 | 3 | R$ 197 |
| **Business** | Ilimitado | 10 | R$ 397 |

Margem bruta acima de 90% em todos — seu custo é hospedagem e banco.

**Trial:** 5 buscas com a sua chave (custo estimado abaixo de R$ 5) para o cliente ver o produto
funcionando antes de encarar o cadastro no GCP. Essa é a razão de existir do trial: vencer a
fricção do onboarding.

### 9.2 Planos gerenciados — fase 2, após resolver licenciamento

Você fornece o dado e cobra por crédito. **1 crédito = 1 lead novo entregue.**

Assumindo **R$ 0,05/lead de custo** (número de planejamento conservador, **não medido**):

| Plano | Créditos/mês | Preço | R$/lead | Custo | Margem |
|---|---|---|---|---|---|
| **Starter** | 300 | R$ 97 | R$ 0,32 | R$ 15 | 85% |
| **Pro** | 1.000 | R$ 247 | R$ 0,25 | R$ 50 | 80% |
| **Business** | 3.000 | R$ 597 | R$ 0,20 | R$ 150 | 75% |

Créditos avulsos, sempre mais caros que o plano — é o que empurra para a assinatura:

| Pacote | Preço | R$/lead |
|---|---|---|
| 200 | R$ 79 | R$ 0,40 |
| 500 | R$ 169 | R$ 0,34 |
| 1.500 | R$ 449 | R$ 0,30 |

Referência de mercado: Speedio, Cortex e Econodata rodam de R$ 200 a R$ 800/mês no Brasil. O
ângulo "leads sem site" é nicho e se vende sozinho para agência.

> Se o custo medido vier em R$ 0,02, a margem sobe ~6 pontos e dá para ser mais agressivo no
> Business. Se vier R$ 0,09, o Business a R$ 597 cai para ~55% e precisa subir de preço ou
> encolher em créditos.

---

## 10. Contabilização de créditos

Seis regras. São elas que decidem se o sistema de créditos funciona ou vira fila de suporte.

1. **Debita na entrega, não na busca.** Job que falha ou não retorna nada não cobra nada.
2. **Duplicata é grátis.** Lead já presente na conta *daquele tenant* não desconta crédito.
3. **Reserva no início do job, acerta no fim.** Segura o saldo estimado, devolve o não usado.
   Sem isso, duas buscas simultâneas furam o limite.
4. **Crédito de plano expira no fim do ciclo. Avulso dura 12 meses.** Sem expiração você
   acumula passivo eterno.
5. **Consome plano primeiro, avulso depois.** O contrário faz o cliente queimar o que pagou à
   parte e perder o da mensalidade.
6. **Extrato visível.** Data, região, categoria, créditos gastos. É o primeiro chamado que
   abre quando não existe.

Saldo é sempre `SELECT SUM(amount) FROM credit_ledger WHERE tenant_id = ? AND (expires_at IS NULL OR expires_at > now())`.

---

## 11. Medição obrigatória

Antes de fechar qualquer preço do modelo gerenciado, ou de afrouxar qualquer cota:

1. Suba o motor com as correções da seção 5
2. Anote o contador de requisições no painel de APIs do Google
3. Rode **uma** busca de 100 leads numa região nunca varrida
4. Volte ao painel e conte as requisições de Places API (New)

`chamadas ÷ 100` é o seu custo real por lead, multiplicado por R$ 0,18.

Referências para comparar:

| | Chamadas por 100 leads |
|---|---|
| Código antigo (medido em produção) | **345** |
| Melhor caso teórico do código novo | 5 |
| Suposição de planejamento | 10–30 |

O intervalo entre 5 e 345 é largo demais para precificar por estimativa. **Meça.**

---

## 12. Roadmap

**Fase 1 — Fundação (BYOK)**
Multi-tenancy, chave por cliente com criptografia, busca assíncrona em fila, deduplicação por
tenant, guardrails da seção 6, telemetria de custo da seção 7.

**Fase 2 — Comercial**
Planos e cobrança (Stripe ou Asaas com Pix), onboarding guiado de BYOK, trial com chave
própria, extrato de uso.

**Fase 3 — Otimização**
Medição por termo do catálogo, poda dos termos redundantes (seção 5.5), mapa de regiões
esgotadas por tenant, sugestão de próxima região a varrer.

**Fase 4 — Modelo gerenciado**
Só depois de receita recorrente: negociar licenciamento com o Google ou avaliar fornecedor
licenciado, e então habilitar os planos por crédito da seção 9.2.

**Fase 5 — Enriquecimento**
Analisar o site do lead que *tem* site (tecnologia, se é responsivo, idade do layout) para
gerar gancho comercial. Aqui `ScrapeGraphAI` ou um LLM fazem sentido: o insumo é pequeno, o
valor é alto e não há problema de termos de uso.

---

## 13. Riscos conhecidos

| Risco | Mitigação |
|---|---|
| Termos do Google sobre redistribuição | BYOK no v1; licenciar antes da fase 4 |
| Custo por lead ainda não medido | Seção 11, antes de precificar o gerenciado |
| Fricção do onboarding BYOK derruba conversão | Trial com chave própria + onboarding guiado |
| Cliente rebusca região esgotada | Teto por job + mapa de regiões varridas |
| Completude de `websiteUri` na busca | Validar com script antes de eliminar o Place Details |
| Chave do cliente expira ou estoura cota | Health check diário + aviso proativo |
| Dependência de fornecedor único | Fase 3+: avaliar Overture/Foursquare como camada de descoberta |
