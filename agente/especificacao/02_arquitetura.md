# 02 - Arquitetura

## Visao de alto nivel

Pipeline funcional:

1. `market_tool` coleta snapshots e historico tecnico por ticker.
2. `news_tool` coleta e consolida noticias/sentimento por ticker.
3. `decision_agent` combina sinais tecnico + noticias e produz recomendacao.
4. `run_analysis` monta `RunResult` com recomendacoes, status e registros estruturados.
5. `json_store` persiste artefatos em `data/`.
6. `main.py` apresenta resultados, backtest e chat explicativo.

## Componentes implementados

- Interface: `app/main.py`.
- Pipeline: `app/pipelines/run_analysis.py`.
- Agente decisor: `app/agents/decision_agent.py`.
- Agente explicador: `app/agents/explainer_agent.py`.
- Prompt do explicador: `app/agents/system_prompt.py`.
- Tools: `app/tools/market_tool.py`, `app/tools/news_tool.py`, `app/tools/insight_tools.py`, `app/tools/backtest_tool.py`.
- Persistencia: `app/storage/json_store.py`.
- Contratos: `app/domain/models.py`.

## Padrao de responsabilidade

- Coleta e transformacao de dados ficam nas tools.
- Regra de decisao fica isolada no agente decisor.
- Explicacao fica isolada no agente explicador.
- Orquestracao e contrato de retorno ficam no pipeline.
- Interface apenas dispara fluxo e exibe saida.

## Guardrails de comportamento

- Fallback seguro quando fonte real falha.
- Resposta explicativa sem inventar dados ausentes.
- Recomendacao sempre com justificativa e evidencias.
- Backtest com validacao de janela e mensagens de erro amigaveis.
