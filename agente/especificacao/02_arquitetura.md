# 02 - Arquitetura

## 1. Visao em camadas
- Interface: Streamlit em app/main.py.
- Orquestracao: pipeline em app/pipelines/run_analysis.py.
- Agentes: logica de decisao/explicacao em app/agents/.
- Tools: mercado, noticias, insights e backtest em app/tools/.
- Dominio: contratos de dados em app/domain/models.py.
- Persistencia: armazenamento JSON em app/storage/json_store.py.

## 2. Fluxo principal
1. Usuario inicia execucao no app.
2. Pipeline coleta snapshot tecnico e noticias por ticker.
3. Agente executa tools e monta trilha ReAct.
4. Sistema gera recomendacao com evidencia.
5. Resultado e persistido em arquivos JSON.
6. UI mostra recomendacoes, status, backtest e chat explicativo.

## 3. Integracoes externas
- yfinance: dados de mercado.
- feedparser: leitura de feeds RSS.
- Azure OpenAI: decisao, reflexao e explicacoes de chat no fluxo principal.

## 4. Desenho logico (alto nivel)
- Entrada: configuracao + tickers + modo de dados.
- Processamento: tools + agente + normalizacao de sinal.
- Saida: recomendacoes, historicos, status, metricas e respostas de chat.
