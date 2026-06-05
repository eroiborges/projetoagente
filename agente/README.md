# Projeto Agente - Sprint 1

Base inicial do projeto com arquitetura multiagente, app Streamlit e pipeline unico para execucao on-demand ou agendavel, com escopo por ticker unico ou todos os tickers.

## Como executar

1. Ative o ambiente virtual na raiz do workspace.
2. Instale dependencias:

```bash
cd /agent/agente
/agent/.venv/bin/python -m pip install -r requirements.txt
```

3. Rode o app:

```bash
cd /agent/agente
/agent/.venv/bin/streamlit run app/main.py
```

## Estado Atual

- Dados em modo mock (padrao)
- Persistencia JSON em data/recommendations.json
- Persistencia tecnica JSON em data/technical_snapshots.json
- Historico tecnico consolidado em data/technical_history.json
- Status operacional por ticker em data/ticker_statuses.json
- Noticias em modo real via RSS (InfoMoney, B3, Reuters) com fallback seguro
- Fontes RSS estaveis em modo real:
	- InfoMoney: https://www.infomoney.com.br/feed/
	- B3 (via Google News RSS): https://news.google.com/rss/search?q=B3+site:b3.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419
	- Reuters (via Google News RSS): https://news.google.com/rss/search?q=site:reuters.com+business+stocks&hl=en-US&gl=US&ceid=US:en
- Feed dinamico por ticker (Google News) para aumentar cobertura de noticias por ativo (ex.: ITUB4)
- .env usado apenas para secrets/credenciais (ex.: endpoint e API key)
- Parametros da aplicacao (feeds, tickers, limites e defaults) centralizados em app/config/settings.py
- Coleta de mercado real com indicadores tecnicos (RSI, MACD, SMA/EMA, Bollinger, volume medio)
- Pipeline com fallback por ticker e status operacional por execucao
- Testes automatizados passando para mercado, noticias, pipeline e persistencia
- App com link clicavel por ticker para abrir pagina da TradingView em nova aba
- Link da TradingView exibido ao lado de cada recomendacao na tabela principal

## Parametros da Aplicacao (settings.py)

Arquivo de referencia: app/config/settings.py

1. azure_openai_endpoint
- Tipo: string
- Descricao: endpoint do Azure OpenAI/Foundry.
- Valor esperado: URL HTTPS valida.

2. azure_openai_api_key
- Tipo: string (secreto)
- Descricao: chave da API do recurso Azure.
- Valor esperado: chave valida do recurso.

3. azure_openai_deployment_news
- Tipo: string
- Descricao: deployment usado para etapa de noticias/sentimento.
- Valor atual: gpt-5.4-mini

4. azure_openai_deployment_trading
- Tipo: string
- Descricao: deployment usado para etapa de decisao de trading.
- Valor atual: gpt-5.4-mini

5. azure_openai_api_version
- Tipo: string
- Descricao: versao da API Azure OpenAI.
- Valor atual: 2024-12-01-preview

6. app_default_data_mode
- Tipo: string
- Valores possiveis: mock, real
- Valor padrao: mock

7. app_default_execution_mode
- Tipo: string
- Valores possiveis: on_demand, scheduled
- Valor padrao: on_demand

8. app_default_tickers
- Tipo: string (CSV)
- Formato: TICKER1,TICKER2,...
- Exemplo: VALE3,PETR4,BBAS3,ITUB4

9. app_market_period
- Tipo: string
- Descricao: janela de historico para yfinance.
- Valores comuns: 1mo, 3mo, 6mo, 1y, 2y, 5y
- Valor padrao: 6mo

10. app_news_limit_per_ticker
- Tipo: inteiro
- Descricao: limite de itens lidos por feed para cada ativo.
- Valor recomendado: inteiro maior que 0
- Valor padrao: 30

11. app_feed_infomoney
- Tipo: string (URL)
- Descricao: feed RSS principal InfoMoney.

12. app_feed_b3
- Tipo: string (URL)
- Descricao: feed RSS estavel para noticias da B3 (via Google News).

13. app_feed_reuters
- Tipo: string (URL)
- Descricao: feed RSS estavel para Reuters business/stocks (via Google News).

14. app_feed_google_news_ticker_template
- Tipo: string (URL template)
- Descricao: feed dinamico por ticker.
- Regra: deve conter o placeholder {query}.

15. app_tradingview_symbol_base
- Tipo: string (URL base)
- Descricao: base para montar link do TradingView por ticker.
- Exemplo valido: https://br.tradingview.com/symbols/BMFBOVESPA

Observacao:

- Apenas secrets devem ficar no .env.
- Parametros de aplicacao permanecem centralizados no settings.py.
