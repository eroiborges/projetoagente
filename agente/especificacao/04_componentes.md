# 04 - Componentes

## Estrutura implementada

- `app/main.py`: interface Streamlit com execucao, tabela, status, backtest e chat.
- `app/pipelines/run_analysis.py`: pipeline principal e contrato de retorno.
- `app/agents/decision_agent.py`: regra de recomendacao e evidencia.
- `app/agents/explainer_agent.py`: respostas do chat por intencao.
- `app/agents/system_prompt.py`: prompt de sistema do explicador.
- `app/tools/market_tool.py`: coleta de mercado e indicadores.
- `app/tools/news_tool.py`: coleta/classificacao de noticias.
- `app/tools/insight_tools.py`: leitura de contexto para respostas explicativas.
- `app/tools/backtest_tool.py`: backtest e metricas.
- `app/storage/json_store.py`: append com deduplicacao.
- `app/domain/models.py`: dataclasses de dominio.

## Testes implementados

- `tests/test_market_tool.py`
- `tests/test_news_tool.py`
- `tests/test_json_store.py`
- `tests/test_pipeline_integration.py`
- `tests/test_explainer_agent.py`
- `tests/test_backtest_tool.py`
- `tests/test_demo_sprint5.py`

## Responsabilidades resumidas

- Pipeline: orquestrar coleta, decisao e consolidacao.
- Agente decisor: transformar sinais em recomendacao.
- Agente explicador: responder perguntas do usuario com base nos dados do dia.
- Backtest: medir desempenho da estrategia com dados historicos persistidos.
- App: expor experiencia de demonstracao ponta a ponta.
