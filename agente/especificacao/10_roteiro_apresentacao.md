# 10 - Roteiro de Apresentacao

## Objetivo da demo

Mostrar o fluxo ponta a ponta: execucao do pipeline, leitura dos resultados, explicacao no chat e visao de backtest.

## Tempo sugerido

- 8 a 12 minutos.

## Sequencia

1. Abertura (1 min)
- Contexto do problema.
- Ativos monitorados: VALE3, PETR4, BBAS3, ITUB4.

2. Execucao do pipeline (2 min)
- Mostrar selecao de modo e escopo.
- Executar pipeline.
- Confirmar tabela de recomendacoes.

3. Status operacional (1 min)
- Abrir `Status por ticker`.
- Explicar `market_status`, `news_status` e contagem de noticias.

4. Explicabilidade no chat (2 a 3 min)
- Pergunta 1: "Por que ITUB4 ficou COMPRAR hoje?"
- Pergunta 2: "Quais riscos dessa recomendacao hoje?"
- Pergunta 3: "Compare ITUB4 e VALE3"

5. Backtest minimo (2 min)
- Abrir expander de backtest.
- Mostrar metricas agregadas e por ticker.
- Se nao houver linhas suficientes, explicar mensagem diagnostica.

6. Encerramento (1 a 2 min)
- Destacar rastreabilidade via arquivos JSON.
- Reforcar limitacoes e possiveis evolucoes futuras.

## Perguntas de apoio

- Como o sistema evita parar quando uma fonte falha?
- Onde as evidencias da recomendacao ficam registradas?
- O que e necessario para o backtest ter linhas avaliaveis?

## Checklist pre-demo

- App abre sem erro.
- Pipeline executa para os 4 tickers.
- Dados em `data/` atualizados.
- Chat habilitado apos execucao.
- Backtest exibindo metricas ou diagnostico coerente.
