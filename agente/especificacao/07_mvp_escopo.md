# 07 - Escopo do MVP

## Dentro do MVP

1. Coleta de preços históricos por yfinance para VALE3, PETR4, BBAS3, ITUB4.
2. Coleta de notícias via RSS e classificação de sentimento.
3. Cálculo de RSI, MACD, SMA/EMA, Bollinger e volume médio.
4. Agente com pelo menos 3 tools funcionais.
5. Recomendação COMPRAR/VENDER/AGUARDAR com justificativa.
6. Interface conversacional básica para consulta e explicação.
7. Registro diário de saída para auditoria acadêmica.

## Fora do MVP

- Broker integration para executar ordens.
- Estratégia de rebalanceamento de carteira com alocação ótima.
- Painel avançado com autenticação multiusuário.

## Critérios de aceite do MVP

- O pipeline roda de ponta a ponta sem intervenção manual.
- Cada ticker gera recomendação diária com justificativa legível.
- O agente responde perguntas de explicação por ticker.
- Saída contém indicadores e sentimento usados na decisão.
- Há rastreabilidade mínima de dados de entrada e decisão final.
