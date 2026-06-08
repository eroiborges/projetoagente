# 07 - Parametros e Configuracao

Arquivo-base: app/config/settings.py

## 1. Parametros Azure OpenAI
- azure_openai_endpoint: endpoint do recurso Azure OpenAI.
- azure_openai_api_key: chave de API.
- azure_openai_deployment_news: deployment reservado (atualmente nao utilizado no fluxo principal).
- azure_openai_deployment_trading: deployment usado para decisao e reflexao da recomendacao.
- azure_openai_api_version: versao da API Azure OpenAI.

## 2. Parametros de aplicacao
- app_default_data_mode:
	- valores aceitos: mock, real
	- default atual em settings.py: real
	- uso: default de modo de dados na UI e fallback de chamada do pipeline sem parametro explicito.
- app_default_execution_mode:
	- valores aceitos: on_demand, scheduled
	- default atual em settings.py: on_demand
	- uso: default de modo de execucao na UI e fallback de chamada do pipeline sem parametro explicito.
- app_default_tickers:
	- formato: CSV (ex.: VALE3,PETR4,BBAS3,ITUB4)
	- uso: lista de tickers para escopo Todos e opcoes de ticker na UI.
- app_market_period:
	- exemplo: 6mo
	- uso: janela de historico na coleta de mercado (yfinance).
- app_news_limit_per_ticker:
	- tipo: inteiro
	- uso: limite de noticias por fonte/ticker na coleta real.
- app_news_summary_top_n:
	- tipo: inteiro
	- uso: quantidade de eventos destacados no resumo de noticias.

## 3. Parametros de feeds
- app_feed_infomoney: feed RSS base.
- app_feed_b3: feed RSS de busca da B3.
- app_feed_reuters: feed RSS de busca Reuters.
- app_feed_google_news_ticker_template: template RSS por ticker com placeholder {query}.

## 4. Parametro de link externo
- app_tradingview_symbol_base: base para links por ticker na interface.

## 5. Modos de operacao
- mock: usa dados simulados para mercado e noticias.
- real: tenta fontes reais de mercado/noticias; em caso de falha de coleta pode cair para fallback de dados.

## 6. Observacoes importantes
- Alterar settings.py muda os defaults da aplicacao, mas selecoes de monitoramento em andamento podem manter estado salvo em data/monitor_state.json.
- Se quiser aplicar imediatamente novos defaults de monitoramento, pare o monitoramento ativo e reinicie a sessao da interface.
