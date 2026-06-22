# PLAN: Categories Expansion

## Overview
O objetivo deste plano é expandir a base de categorias do Prospector, englobando novos nichos de alto valor (como Odontologia, Estética, Advocacia, Contabilidade, etc.) e aprofundando as categorias existentes (ex: Restaurantes incluindo hamburguerias, pastelarias, pizzarias). A busca será combinada (under the hood), agrupando as sub-buscas em uma única categoria pai para o usuário final, e utilizando os tipos do Google Places (`includedType`) para garantir resultados mais precisos.

## Project Type
**WEB / BACKEND**

## Success Criteria
- [ ] Novas categorias e sub-categorias devem estar configuradas no backend (`places.py`).
- [ ] O frontend deve exibir os novos nichos principais no select do formulário.
- [ ] O backend fará buscas combinadas para cada sub-niche do grupo escolhido.
- [ ] Resultados serão agrupados sob uma única `business_type` pai no banco de dados.

## Tech Stack
- **Backend:** Python (FastAPI/SQLAlchemy), HTTPX para requisições concorrentes.
- **Frontend:** HTML/JS Vanilla (atualização do `<select>` do formulário).
- **API Externa:** Google Places API (New) utilizando `textQuery` com restrição de `includedType`.

## File Structure
```text
├── prospector/
│   ├── services/
│   │   └── places.py (Nova arquitetura de busca múltipla)
│   ├── routers/
│   │   └── places.py (Ajustes se necessário)
│   ├── templates/
│   │   └── index.html (Novas options do select)
```

## Task Breakdown

### 1. Refatoração do Dicionário de Categorias (Backend)
- **Agent:** `backend-specialist`
- **Skills:** `api-patterns`
- **Priority:** P1
- **Dependencies:** None
- **INPUT:** Arquivo `places.py`.
- **OUTPUT:** Novo formato de `CATEGORY_CONFIG` mapeando a categoria pai (ex: `restaurant`, `odontology`) para uma lista de `queries` (ex: `["restaurante", "hamburgueria", "pastelaria"]`) e um `included_type` do Google.
- **VERIFY:** O dicionário deve estar syntax-error free e cobrir todas as novas categorias solicitadas.

### 2. Modificação na Lógica de Busca (Backend)
- **Agent:** `backend-specialist`
- **Skills:** `api-patterns`
- **Priority:** P1
- **Dependencies:** Task 1
- **INPUT:** Arquivo `places.py` (função `search_businesses`).
- **OUTPUT:** Lógica de busca combinada. Ao buscar por uma categoria, o sistema dividirá o limite `quantity` (ex: 20) igualmente entre as `queries` ou buscará em paralelo para cada `textQuery` do nicho, até alcançar a quantidade necessária.
- **VERIFY:** A função deve suportar a paginação (nextPageToken) em múltiplas queries concorrentemente e salvar todas as ocorrências sob a categoria pai no banco de dados.

### 3. Atualização da Interface (Frontend)
- **Agent:** `frontend-specialist`
- **Skills:** `frontend-design`
- **Priority:** P2
- **Dependencies:** None
- **INPUT:** Arquivo `index.html`.
- **OUTPUT:** Adição dos novos `<option>` correspondentes às categorias pai (Odontologia, Estética / Spa, Advocacia, Contabilidade, Imobiliária, Construção e Reforma, Automotivo, Veterinária, Móveis e Decoração, Eventos e Festas, Educação, Ótica e Joalheria, Energia Solar, Seguros).
- **VERIFY:** O valor da opção deve bater exatamente com as chaves definidas no dicionário de `places.py`.

### 4. Atualização da Documentação / Enum do Model (Database)
- **Agent:** `database-architect`
- **Skills:** `database-design`
- **Priority:** P1
- **Dependencies:** Task 1
- **INPUT:** Opcional no `models.py` dependendo se há validação por tipo.
- **OUTPUT:** Garantir que o banco aceite os novos identificadores na coluna `business_type` sem restrições de Enum (ou se for Literal, atualizar o Literal no Python, ex: Pyright errors).
- **VERIFY:** Criação de testes simples ou verificar pelo pyright/flake8 se não existem quebras.

---

## ✅ PHASE X: VERIFICATION
- [ ] Lint: Pass (Verificar com `npm run lint` ou `flake8`)
- [ ] Build/Type: Validar com `pyright` se existem conflitos no enum de Business.
- [ ] Test: O front passa as novas categorias e o back processa `search_businesses` de forma agrupada.
