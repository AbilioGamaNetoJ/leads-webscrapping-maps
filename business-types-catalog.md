# Expansão do Catálogo de Tipos de Negócio

## Objetivo

Adicionar os 92 nichos e respectivos termos de busca fornecidos ao seletor de
tipo de negócio, mantendo os tipos oficiais já disponíveis.

## Decisões

- Cada nicho é uma categoria própria do produto, com um identificador estável,
  um rótulo em pt-BR e uma lista de consultas textuais.
- Os tipos oficiais da Places API continuam usando `includedType`; nichos que
  não possuem um tipo oficial equivalente usam apenas `textQuery`.
- A busca distribui a quantidade solicitada entre os termos do nicho e remove
  duplicatas antes de salvar os leads.
- O identificador da categoria é salvo, exibido no histórico e exportado no
  XLSX para que os leads permaneçam rastreáveis.

## Tarefas

- [x] Modelar o catálogo único e conferir a cobertura dos 92 nichos.
- [x] Adaptar a busca para executar as consultas de cada nicho com segurança.
- [x] Persistir, filtrar e exportar a categoria selecionada.
- [x] Validar catálogo, requisições à Places API e fluxo da interface.

## Verificação

- O combobox permite localizar e selecionar cada nicho pelo nome ou por seus
  termos associados.
- Nenhum identificador interno de nicho é enviado indevidamente como
  `includedType`.
- Uma busca salva a categoria selecionada no lead.
- Os testes cobrem todos os nichos fornecidos e as duas modalidades de busca.
