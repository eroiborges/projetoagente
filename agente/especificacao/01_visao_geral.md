# 01 - Visao Geral do Projeto

## 1. Objetivo
Construir um AI Agent de investimentos para os tickers VALE3, PETR4, BBAS3 e ITUB4, capaz de:
- monitorar mercado e noticias;
- gerar recomendacao COMPRAR/VENDER/AGUARDAR com justificativa;
- registrar o raciocinio (ReAct/Chain-of-Thought);
- permitir consulta via interface conversacional.

## 2. Escopo funcional implementado
- Coleta de dados de mercado (yfinance) e noticias (RSS via feedparser).
- Processamento tecnico com indicadores (RSI, MACD, SMA/EMA, Bollinger, volume).
- Analise de sentimento com NLP (VADER com ajuste de lexico financeiro).
- Agente com tools e trilha ReAct.
- Recomendacao por ticker com evidencias.
- Backtest com comparativo Buy-and-Hold.
- Interface Streamlit com execucao manual e monitoramento em sessao (5/15/30 min).

## 3. Resultado esperado para avaliacao
- Acuracia de recomendacoes (acerto de tendencia).
- Qualidade de explicacao do raciocinio.
- Desempenho financeiro da estrategia vs Buy-and-Hold.
- Interface conversacional funcional.
