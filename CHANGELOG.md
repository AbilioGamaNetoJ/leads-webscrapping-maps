# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o versionamento segue o [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado

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

- O estado "Nenhum resultado" mantinha para sempre o texto de erro depois da primeira
  falha de busca; agora os textos originais são restaurados.
