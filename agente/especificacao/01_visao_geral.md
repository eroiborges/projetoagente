# 01 - Visao Geral do Projeto

## Contexto

Projeto academico de AI Agent para apoio a decisao em renda variavel com foco em explicabilidade e rastreabilidade.

Ativos monitorados:

- VALE3
- PETR4
- BBAS3
- ITUB4

## Objetivo da entrega

Fornecer uma aplicacao funcional que:

- Coleta dados tecnicos e noticias por ticker.
- Gera recomendacao `COMPRAR`, `VENDER` ou `AGUARDAR`.
- Exibe justificativa com evidencias objetivas.
- Permite perguntas em linguagem natural sobre a recomendacao do dia.
- Persiste artefatos em arquivos JSON para auditoria.

## Valor da solucao

- Consolida sinais tecnicos e noticias em uma unica visao.
- Reduz ambiguidade da recomendacao com explicacao causal.
- Permite demonstracao ponta a ponta sem dependencias externas de interface.

## Publico alvo

- Avaliador academico: precisa de reproducibilidade e clareza tecnica.
- Usuario de demonstracao: precisa de saida simples e interpretavel.

## Casos de uso entregues

1. Executar pipeline para um ticker ou para todos.
2. Visualizar recomendacoes e status por ticker.
3. Consultar explicacoes no chat: por que, mudanca, risco, resumo, tecnico, noticias e comparacao.
4. Rodar backtest minimo com resumo agregado e por ticker.

## Fora de escopo

- Execucao automatica de ordens em corretora.
- Gestao de carteira multiativo com otimizacao de alocacao.
- Uso intraday em baixa latencia.
