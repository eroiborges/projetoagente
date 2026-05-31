# 06 - Fluxos de Interação

## Fluxo 1 - Recomendação diária

1. Pipeline coleta preços dos 4 tickers.
2. Pipeline coleta notícias e classifica sentimento.
3. Pipeline calcula indicadores técnicos.
4. Motor consolida sinais por ticker.
5. Agente gera recomendação e justificativa.
6. Resultado é salvo e exibido na interface.

## Fluxo 2 - Pergunta explicativa

Exemplo: "Por que PETR4 está em VENDER hoje?"

1. Agente consulta análise diária mais recente.
2. Agente recupera sinais técnicos e sentimento.
3. Agente responde com justificativa objetiva e fatores-chave.

## Fluxo 3 - Pergunta comparativa

Exemplo: "Qual ativo está mais favorável hoje?"

1. Agente consulta análises dos 4 ativos.
2. Compara confidence_score e coerência dos sinais.
3. Retorna ranking com ressalvas e incertezas.

## Fluxo 4 - Tratamento de falta de dados

1. Tool detecta ausência de preço ou notícia.
2. Motor marca sinal como insuficiente.
3. Agente retorna AGUARDAR ou baixa confiança com explicação.
