# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o versionamento segue o [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado

- Redesign mobile-first com barra de navegação inferior (Buscar · Histórico · Exportar ·
  Usuários para admin · Perfil), no padrão de app nativo: ícone ativo elevado num círculo
  sobre a barra. O cabeçalho de topo com a navegação horizontal e o menu de usuário passam
  a aparecer só a partir de `lg`.
- Folha de perfil (`_profile_sheet.html`), aberta pelo item **Perfil** da barra inferior:
  conta atual, alternar tema claro/escuro, **Instalar app** e **Sair** — tira esses
  controles do cabeçalho no mobile.
- Listas de leads (busca e histórico) e a tabela de usuários agora mostram **cards** abaixo
  de `md`, com botões grandes de Maps/WhatsApp/copiar telefone; a tabela original continua
  no desktop. Formulários de busca e de filtros do histórico viram seções colapsáveis no
  mobile, com um resumo dos filtros ativos quando fechados.
- Prospector agora é um **PWA instalável** em Android, iOS e desktop: `manifest.webmanifest`,
  ícones gerados a partir do símbolo da marca (192, 512, maskable-512, apple-touch-icon) e
  um service worker (`static/sw.js`) com shell estático pré-cacheado e página `/offline` de
  fallback. Botão **Instalar app** usa `beforeinstallprompt` no Android/desktop e mostra o
  passo a passo de "Adicionar à Tela de Início" no Safari iOS (que não dispara esse evento).
- Opção **Todos os tipos** no campo Tipo de Negócio, agora o padrão do formulário.
  Monta um plano com os termos de todas as 140 categorias, embaralhados com semente
  fixa e intercalados, para que os primeiros resultados já venham de nichos variados.
  Cada lead continua salvo com a categoria real que o encontrou.
- Quantidades de 200, 500 e 1000 resultados no formulário de busca.
- Busca em lotes: `POST /search` executa um lote por chamada e devolve o `cursor` do
  próximo, e o front repete a chamada preenchendo a tabela progressivamente. Mantém
  cada request bem abaixo do timeout de 10s da Vercel Hobby mesmo em buscas de 1000.
- Botão **Parar busca** e contador de progresso durante buscas longas.
- `services/deduplication.existing_place_ids` — verifica os `place_id` de um lote inteiro
  em um round-trip por bloco, no lugar de uma consulta por resultado.

### Alterado

- Tailwind deixou de ser carregado via `cdn.tailwindcss.com` (compilador de desenvolvimento
  rodando no navegador, ~400KB, sem cache confiável offline). Agora é compilado com o
  Tailwind CLI para `static/app.css` (~30KB minificado) e comitado — `npm run css` depois de
  qualquer classe nova; `npm run css:watch` durante o desenvolvimento.
- Campos de formulário (busca, filtros do histórico, convite de usuário) passam a
  `text-base` abaixo de `md`, voltando a `text-sm` no desktop — abaixo de 16px o iOS dá
  zoom automático ao focar um input.
- Teto de resultados por busca de 100 para **1000**.
- Combobox de tipo de negócio: filtra a cada tecla (sem o debounce de 80ms, que era
  inútil num filtro local) e mostra todas as opções correspondentes em vez de apenas 8.
  Ao focar, abre a lista completa e seleciona o texto atual.
- Gravação dos leads passou a ser um `add_all` com um commit por lote, no lugar de
  um commit por linha — contra o Postgres serverless isso custava dezenas de segundos
  numa busca grande.
- Chamadas ao Place Details passaram a ser limitadas por semáforo (25 simultâneas),
  evitando estourar o pool do httpx e a QPS do Google em buscas grandes.
- Filtros de nota e de número de avaliações passaram a ser aplicados **antes** do corte
  por quantidade; antes rodavam depois e faziam a busca devolver menos que o pedido.
- Termos de busca repetidos entre categorias (ex.: "Encanador", em 5 nichos) viram uma
  consulta só no modo Todos — 566 consultas em vez de 612.

### Corrigido

- Links de Maps e WhatsApp (nas listas de busca e histórico) e o botão Exportar
  deixaram de abrir em `target="_blank"`. No PWA instalado, uma nova aba/janela tira o
  usuário do contexto do app sem deixar como voltar, forçando fechar e reabrir; sem
  `target="_blank"`, a navegação para fora do escopo acontece na mesma janela e o
  Android mostra a barra de retorno ao app padrão do modo standalone.
- `GET /export` passou a devolver os bytes do XLSX diretamente (`Response`) no lugar de
  um `StreamingResponse` sobre o `BytesIO` do openpyxl, evitando a iteração linha a linha
  implícita desse tipo de objeto. Testes de `services/xlsx_generator.py` e `GET /export`
  passaram a conferir o valor de cada uma das 8 colunas (antes só cabeçalho e nome
  eram testados) — não foi reproduzido um caso em que os dados venham incompletos.
- O estado "Nenhum resultado" mantinha para sempre o texto de erro depois da primeira
  falha de busca; agora os textos originais são restaurados.
