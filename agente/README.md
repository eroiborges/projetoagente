# Projeto Agente

Aplicacao em Streamlit para analise de ativos com recomendacao explicavel baseada em sinais tecnicos e noticias.

Ativos alvo:

- VALE3
- PETR4
- BBAS3
- ITUB4

## Execucao

1. Instalar dependencias:

```bash
cd /agent/agente
/agent/.venv/bin/python -m pip install -r requirements.txt
```

2. Executar a aplicacao:

```bash
cd /agent/agente
/agent/.venv/bin/streamlit run app/main.py
```

3. Executar bateria principal de testes:

```bash
cd /agent/agente
/agent/.venv/bin/pytest -q
```

## Estrutura atual

- `app/main.py`: interface Streamlit (pipeline, tabela de recomendacoes, backtest, chat).
- `app/pipelines/run_analysis.py`: orquestracao ponta a ponta.
- `app/agents/decision_agent.py`: decisao final de recomendacao.
- `app/agents/explainer_agent.py`: respostas explicativas no chat.
- `app/agents/system_prompt.py`: regras do agente explicador.
- `app/tools/market_tool.py`: coleta e snapshot tecnico.
- `app/tools/news_tool.py`: coleta e consolidacao de noticias/sentimento.
- `app/tools/insight_tools.py`: contexto para respostas do chat.
- `app/tools/backtest_tool.py`: backtest a partir de registros persistidos.
- `app/storage/json_store.py`: persistencia JSON com deduplicacao.
- `app/domain/models.py`: contratos de dados.

## Fluxo funcional

1. Usuario escolhe modo de execucao e escopo de tickers.
2. Pipeline gera recomendacoes com evidencias por ticker.
3. Resultados sao persistidos em JSON na pasta `data/`.
4. App exibe tabela de recomendacoes, status por ticker e painel de backtest.
5. Chat responde perguntas de explicacao com base no resultado da ultima execucao.

## Parametros principais

Arquivo de referencia: `app/config/settings.py`

- `app_default_data_mode`: `mock` ou `real`.
- `app_default_execution_mode`: `on_demand` ou `scheduled`.
- `app_default_tickers`: lista CSV de tickers.
- `app_market_period`: janela de historico para coleta de mercado.
- `app_news_limit_per_ticker`: limite por fonte/ticker na etapa de noticias.
- `app_tradingview_symbol_base`: base do link por ticker.
- `azure_openai_*`: configuracao do provedor para etapas com modelo.

## Arquivos de saida

Persistidos em `data/`:

- `recommendations.json`
- `recommendation_records.json`
- `technical_snapshots.json`
- `technical_history.json`
- `news_items.json`
- `ticker_statuses.json`

## Contratos importantes

- Recomendacao: `COMPRAR`, `VENDER`, `AGUARDAR`.
- `confidence`: intervalo `[0, 1]`.
- `evidence`: inclui `technical_score`, `news_score`, `total_score`, fatores e gatilhos.
- `market_status`: `ok_real`, `ok_mock`, `error_real_fallback`.
- `news_status`: `ok_real`, `ok_mock`, `warning_real_partial`, `warning_real_no_match`, `error_real_fallback`.

## Chat

Intencoes suportadas:

- por que
- o que mudaria
- qual o risco
- resumo
- noticias
- tecnico
- comparacao entre tickers

## Backtest

O backtest utiliza `recommendation_records.json` + `technical_history.json`.

Retorno principal:

- `rows`: linhas avaliadas.
- `summary`: total de sinais, sinais avaliados, acertos, hit rate e retorno medio.
- `by_ticker`: resumo por ativo.
- `window`: janela aplicada.
- `errors`: validacoes de janela/arquivo quando aplicavel.
- `diagnostics`: contagem de motivos para ausencia de linhas (quando houver).

## Entrega academica

Documentacao final em `especificacao/`:

- `01_visao_geral.md`
- `02_arquitetura.md`
- `03_modelo_dados.md`
- `04_componentes.md`
- `05_tecnologias.md`
- `06_fluxos.md`
- `07_mvp_escopo.md`
- `08_plano_sprints.md`
- `09_execucao_final_limitacoes.md`
- `10_roteiro_apresentacao.md`
