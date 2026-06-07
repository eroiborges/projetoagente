# 07 - Escopo da Entrega

## Escopo entregue

1. Coleta de mercado para VALE3, PETR4, BBAS3 e ITUB4.
2. Coleta de noticias com sentimento e impacto por ticker.
3. Indicadores tecnicos (RSI, MACD, SMA/EMA, Bollinger, volume medio).
4. Recomendacao `COMPRAR`, `VENDER`, `AGUARDAR` com `confidence`, `rationale` e `evidence`.
5. Persistencia estruturada dos resultados em JSON.
6. Chat explicativo com intents de por que, mudanca, risco, resumo, noticias, tecnico e comparacao.
7. Backtest minimo com resumo agregado e por ticker, incluindo validacoes de janela.
8. Testes unitarios, integracao e bateria de demo.

## Fora de escopo

- Execucao automatica de ordens reais.
- Otimizacao de carteira e rebalanceamento.
- Dashboard corporativo multiusuario com autenticacao.

## Criterios de aceite da entrega

- Aplicacao executa localmente de ponta a ponta.
- Pipeline gera recomendacoes para o conjunto de tickers alvo.
- Explicacoes no chat sao coerentes com os dados da execucao.
- Artefatos persistidos permitem auditoria basica.
- Backtest executa com metricas e mensagens de erro compreensiveis.
