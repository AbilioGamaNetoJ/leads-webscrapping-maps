# PRD Técnico — Prospector de Negócios Locais
> Documento de referência para desenvolvimento por IA ou desenvolvedor terceiro.  
> Uso interno da **Codex Create**. Não destinado à comercialização.

---

## 1. Visão Geral

Ferramenta interna de prospecção de negócios locais. Permite filtrar por cidade, bairro, tipo de negócio, quantidade de resultados e — opcionalmente — exibir somente negócios sem site cadastrado. Evita duplicatas entre buscas e exporta os dados em `.xlsx` para uso pelo time comercial.

---

## 2. Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Performance assíncrona, suporte a automação futura e ecossistema de dados |
| Templates HTML | Jinja2 (via FastAPI) | Renderização server-side simples, sem build de frontend |
| Estilização | Tailwind CSS (via CDN) | Interface visual moderna sem necessidade de build pipeline |
| Banco de dados | Neon (PostgreSQL serverless) | Serverless, sem custo inicial, integração direta com Python via psycopg2 |
| ORM | SQLAlchemy (síncrono) | Gerenciamento de tabelas, queries e migrações |
| Geração de XLSX | openpyxl | Geração de planilha em memória, download via StreamingResponse |
| Integração Maps | Google Places API (New) — REST via `httpx` | Busca de negócios por tipo, área e quantidade |
| Variáveis de ambiente | python-dotenv | Gerenciamento de chaves e secrets |

---

## 3. Regras de Negócio

| ID | Regra |
|---|---|
| RN01 | O filtro "Somente sem site" é **opcional**. Quando ativado, apenas negócios sem `websiteUri` cadastrado no Google Places aparecem nos resultados. Quando desativado, todos os negócios da busca são retornados independente de terem site ou não |
| RN02 | Cada negócio é identificado de forma única pelo `place_id` retornado pela Places API |
| RN03 | Se um `place_id` já existir no banco, ele deve ser ignorado silenciosamente e não salvo novamente, independente do filtro de site |
| RN04 | O usuário deve poder definir entre 5 e 100 resultados por busca |
| RN05 | A busca deve aceitar cidade + bairro como área de pesquisa, convertendo esse texto em coordenadas via Geocoding API do Google |
| RN06 | O arquivo XLSX exportado deve conter: Nome do Negócio, Endereço, Link do Maps, Telefone, e uma coluna "Possui Site?" (Sim/Não) |
| RN07 | Campos sem informação disponível (ex: telefone não cadastrado) devem ser preenchidos com "Não informado" |
| RN08 | O sistema deve armazenar apenas os campos estritamente necessários no banco (place_id, nome, endereço, telefone, maps_url, has_website, data de criação) |
| RN09 | A resposta da busca deve sempre informar: total verificado, novos salvos, duplicatas ignoradas e quantos possuem ou não site |

---

## 4. Requisitos Funcionais

| ID | Descrição |
|---|---|
| RF01 | Formulário de busca com campos: Cidade, Bairro, Tipo de Negócio (select com opções predefinidas), Quantidade (5, 10, 20, 50, 100) |
| RF02 | Toggle/checkbox "Somente negócios sem site" no formulário. Quando marcado, filtra apenas os sem site. Quando desmarcado, retorna todos |
| RF03 | Botão "Buscar Negócios" que dispara a busca via chamada AJAX ao endpoint `POST /search` |
| RF04 | Exibição dos resultados em tabela com colunas: Nome, Endereço, Telefone, Possui Site?, Link do Maps (botão "Abrir") |
| RF05 | A coluna "Possui Site?" deve exibir um badge visual: verde "Não" (lead potencial) e cinza/vermelho "Sim" |
| RF06 | Indicador visual de carregamento (spinner) enquanto a busca estiver em andamento |
| RF07 | Resumo pós-busca visível na interface: "X negócios encontrados · Y sem site · Z já vistos antes" |
| RF08 | Botão "Exportar XLSX" que faz download do arquivo gerado pelo endpoint `GET /export` |
| RF09 | Feedback visual quando nenhum resultado novo for encontrado |
| RF10 | Página de histórico (`/historico`) que lista todos os negócios já salvos no banco, com paginação simples e filtro por nome e por "possui site" |

---

## 5. Requisitos Não Funcionais

| ID | Descrição |
|---|---|
| RNF01 | A interface deve ser utilizável por um leigo, sem treinamento técnico |
| RNF02 | A aplicação deve rodar localmente (localhost) ou em servidor simples, sem necessidade de build pipeline |
| RNF03 | Todos os secrets (API Key do Google, string de conexão do Neon) devem estar em arquivo `.env`, nunca hardcoded |
| RNF04 | O `.env` deve estar listado no `.gitignore` |
| RNF05 | O tempo de resposta da busca deve ter feedback visual imediato para o usuário (spinner ativo durante a chamada) |
| RNF06 | O XLSX deve ser gerado em memória (BytesIO), sem salvar arquivo em disco |

---

## 6. Estrutura de Pastas

```
prospector/
├── main.py                   # Instância do FastAPI e inclusão de routers
├── .env                      # Variáveis de ambiente (não commitado)
├── .env.example              # Template do .env (commitado)
├── requirements.txt
├── database/
│   ├── connection.py         # Engine e SessionLocal do SQLAlchemy
│   └── models.py             # Modelo ORM da tabela businesses
├── routers/
│   ├── search.py             # Endpoint POST /search
│   ├── export.py             # Endpoint GET /export
│   └── history.py            # Endpoint GET /historico
├── services/
│   ├── places.py             # Integração com Google Places API (Nearby + Details)
│   ├── geocoding.py          # Conversão de cidade/bairro em lat/lng
│   ├── deduplication.py      # Verificação de place_id existente no banco
│   └── xlsx_generator.py     # Geração do arquivo XLSX em memória
├── templates/
│   ├── base.html             # Layout base com Tailwind CSS (CDN)
│   ├── index.html            # Página principal: formulário + tabela de resultados
│   └── historico.html        # Página de histórico de buscas
└── static/
    └── app.js                # Fetch JS para chamadas AJAX ao backend
```

---

## 7. Modelo de Banco de Dados

### Tabela: `businesses`

| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL PRIMARY KEY | Chave interna |
| place_id | VARCHAR UNIQUE NOT NULL | ID único do Google Places |
| name | VARCHAR NOT NULL | Nome do negócio |
| address | TEXT | Endereço formatado |
| phone | VARCHAR | Telefone (pode ser NULL) |
| maps_url | TEXT | URL do Maps |
| has_website | BOOLEAN NOT NULL DEFAULT FALSE | TRUE se o negócio possui site cadastrado no Google |
| created_at | TIMESTAMP DEFAULT NOW() | Data/hora de inserção |

---

## 8. Variáveis de Ambiente (.env.example)

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
DATABASE_URL=postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require
```

---

## 9. Endpoints da API

### `POST /search`
- **Descrição**: Recebe os filtros do formulário, consulta a Places API, aplica os filtros configurados, remove duplicatas e salva os novos no banco.
- **Body (JSON)**:
```json
{
  "city": "Florianópolis",
  "neighborhood": "Centro",
  "business_type": "restaurant",
  "quantity": 20,
  "only_without_website": true
}
```
- **Resposta (JSON)**:
```json
{
  "results": [
    {
      "name": "Restaurante X",
      "address": "Rua Tal, 123",
      "phone": "+55 48 99999-9999",
      "maps_url": "https://maps.google.com/?cid=...",
      "has_website": false
    }
  ],
  "summary": {
    "total_checked": 20,
    "new_saved": 12,
    "skipped_duplicates": 5,
    "with_website": 3,
    "without_website": 9
  }
}
```

### `GET /export`
- **Descrição**: Gera e retorna o arquivo XLSX com todos os negócios salvos no banco.
- **Query params opcionais**: `?only_without_website=true` para exportar somente os sem site.
- **Resposta**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` como attachment.
- **Filename**: `negocios-prospectados.xlsx`
- **Colunas do XLSX**: Nome do Negócio, Endereço, Telefone, Possui Site?, Link do Maps

### `GET /historico`
- **Descrição**: Renderiza a página HTML de histórico com todos os leads salvos, com paginação de 20 por página, busca por nome e filtro por "Possui Site".

---

## 10. Fluxo da Busca (service `places.py`)

```
1. Recebe filtros: city, neighborhood, business_type, quantity, only_without_website
2. geocoding.py → converte "Florianópolis, Centro" em {lat, lng}
3. Chama Places API Nearby Search (New):
   - POST https://places.googleapis.com/v1/places:searchNearby
   - Headers: X-Goog-Api-Key, X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress
   - Body: { includedTypes: [business_type], maxResultCount: quantity,
             locationRestriction: { circle: { center: {lat, lng}, radius: 2000 } } }
4. Para cada place retornado:
   a. Verifica se place.id já existe no banco (deduplication.py) → se sim, incrementa skipped_duplicates e pula
   b. Chama Place Details:
      - GET https://places.googleapis.com/v1/places/{place_id}
      - FieldMask: internationalPhoneNumber,websiteUri,googleMapsUri
   c. Define has_website = True se websiteUri estiver presente, False caso contrário
   d. Se only_without_website == True e has_website == True → descarta (não salva, não exibe)
   e. Caso contrário → salva no banco com has_website e adiciona ao resultado
5. Retorna lista de resultados + summary com os contadores
```

---

## 11. Tipos de Negócio Suportados (select no formulário)

| Label (PT-BR) | Value (Places API type) |
|---|---|
| Restaurante | restaurant |
| Barbearia | barber_shop |
| Loja de Roupas | clothing_store |
| Salão de Beleza | beauty_salon |
| Farmácia | pharmacy |
| Padaria | bakery |
| Academia | gym |
| Supermercado | supermarket |
| Petshop | pet_store |
| Clínica / Consultório | doctor |

> Essa lista pode ser expandida sem necessidade de alterar a lógica do backend.

---

## 12. Etapas de Desenvolvimento

### Etapa 1 — Setup e Infraestrutura
- Criar repositório com estrutura de pastas definida na seção 6
- Configurar `.env` e `.env.example`
- Criar banco de dados no Neon (free tier)
- Configurar `connection.py` com SQLAlchemy + psycopg2
- Criar tabela `businesses` via `models.py` com `Base.metadata.create_all()`
- Configurar projeto no Google Cloud, habilitar Places API (New) e Geocoding API
- Instalar dependências: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `httpx`, `openpyxl`, `python-dotenv`, `jinja2`

### Etapa 2 — Serviços de Backend
- Implementar `geocoding.py`: recebe "Florianópolis, Centro" e retorna `{lat, lng}`
- Implementar `places.py`: Nearby Search + Place Details, detectando presença de `websiteUri` e definindo `has_website`
- Implementar `deduplication.py`: consulta banco por `place_id` antes de salvar
- Implementar `xlsx_generator.py`: recebe lista de dicts e retorna `BytesIO` com planilha formatada (colunas: Nome, Endereço, Telefone, Possui Site?, Link do Maps)

### Etapa 3 — Endpoints FastAPI
- Implementar `POST /search` em `routers/search.py` com suporte ao campo `only_without_website`
- Implementar `GET /export` em `routers/export.py` com query param `only_without_website`
- Implementar `GET /historico` em `routers/history.py` com filtro por nome e por `has_website`
- Registrar todos os routers em `main.py`

### Etapa 4 — Interface Visual
- Criar `base.html` com Tailwind CSS via CDN, layout responsivo, header com logo Codex Create
- Criar `index.html`:
  - Formulário de filtros com toggle "Somente sem site" bem visível
  - Área de resultados com tabela e badge visual "Possui Site: Sim/Não"
  - Resumo pós-busca: "X encontrados · Y sem site · Z já vistos antes"
  - Spinner de carregamento durante a busca
  - Botão "Exportar XLSX"
- Criar `historico.html`: tabela paginada + campo de busca por nome + filtro por "Possui Site"
- Criar `app.js`: fetch para `POST /search`, atualização dinâmica da tabela e resumo

### Etapa 5 — Validações e UX
- Feedback de "Nenhum resultado novo encontrado"
- Campos "Não informado" para dados ausentes (RN07)
- Validação de formulário no frontend (campos obrigatórios)
- Tratamento de erros da Places API (quota excedida, key inválida, sem resultados)
- Badge visual na tabela: verde para "Não tem site", cinza para "Tem site"

### Etapa 6 — Testes e Ajustes Finais
- Testar fluxo completo com toggle ativado e desativado
- Testar com diferentes tipos de negócio e cidades
- Verificar se o XLSX baixa corretamente com a coluna "Possui Site?"
- Validar que dados sem telefone exibem "Não informado"
- Revisão visual da interface para garantir usabilidade por leigo

---

## 13. Dependências (requirements.txt)

```
fastapi==0.111.0
uvicorn==0.29.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
httpx==0.27.0
openpyxl==3.1.2
python-dotenv==1.0.1
jinja2==3.1.4
```

---

## 14. Observações sobre Uso da Places API

- A Places API (New) requer projeto com billing ativo no Google Cloud, mas possui crédito mensal gratuito ($200/mês).
- A ausência do campo `websiteUri` na resposta do Place Details é o critério usado para classificar `has_website = False`.
- O armazenamento de `place_id` e dados básicos para uso interno de vendas está dentro dos casos de uso permitidos pela política da plataforma.
- Referência oficial: https://developers.google.com/maps/documentation/places/web-service/nearby-search

---

*Documento gerado para uso interno da Codex Create. Versão 1.1.*
