# 06 - Fluxos de Interacao

## Fluxo 1 - Execucao principal

1. Usuario escolhe modo de execucao e escopo.
2. Pipeline coleta mercado e noticias.
3. Agente decisor calcula recomendacao e evidencia.
4. Sistema persiste artefatos em `data/`.
5. App mostra tabela de recomendacoes e status.

## Fluxo 2 - Chat explicativo

Exemplo: "Por que ITUB4 ficou COMPRAR hoje?"

1. App envia pergunta + `RunResult` da ultima execucao.
2. Agente explicador detecta intencao e ticker.
3. Ferramentas de insight montam contexto de recomendacao/tecnico/noticias/status.
4. Resposta e retornada em PT-BR com limites e evidencias.

## Fluxo 3 - Comparacao entre ativos

Exemplo: "Compare ITUB4 e VALE3"

1. Agente identifica dois tickers na pergunta.
2. Monta contexto resumido para cada ticker.
3. Retorna comparacao de recomendacao, confianca e leitura de sinais.

## Fluxo 4 - Backtest minimo

1. App le arquivos de `recommendation_records` e `technical_history`.
2. Backtest tenta casar sinal com preco de entrada e D+1.
3. Exibe metricas agregadas e por ticker.
4. Quando nao ha linhas suficientes, exibe diagnostico e orientacao.

## Fluxo 5 - Robustez e fallback

1. Falha em fonte real ativa fallback seguro por ticker.
2. Status por ticker indica o tipo de falha/aviso.
3. Interface mostra mensagens de erro amigaveis para janela invalida ou arquivo invalido no backtest.
