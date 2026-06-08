# 00 - Objetivos Oficiais do Professor (fonte unica)

Fonte oficial adotada:
- materialAula/Projeto_Integrado_AI_Agents_v2.pdf
- materialAula/Projeto_Integrado_AI_Agents_v2.md (validado como identico ao PDF)

Regra deste documento:
- Este arquivo lista somente objetivos, entregas e criterios declarados no enunciado.
- Nada foi adicionado fora do que o professor descreveu.

## 1. Objetivo geral do projeto

Construir um Assistente de Investimentos baseado em AI Agents para recomendar compra e venda de acoes com autonomia e explicabilidade, combinando:
- noticias e sentimento de mercado em tempo real;
- indicadores tecnicos (RSI, MACD, medias moveis, Bollinger);
- raciocinio e tomada de decisao com justificativa;
- interface conversacional para explicacoes ao usuario.

## 2. Escopo de ativos obrigatorios

A primeira versao deve cobrir os tickers:
- VALE3
- PETR4
- BBAS3
- ITUB4

## 3. Comportamentos esperados do agente

O agente deve:
- monitorar continuamente os 4 ativos;
- coletar dados de mercado e noticias;
- emitir recomendacoes diarias fundamentadas.

## 4. Capacidades obrigatorias por etapa

### 4.1 Percepcao
- leitura de feeds de noticias financeiras;
- coleta de precos e volumes via API;
- extracao de indicadores tecnicos.

### 4.2 Raciocinio
- analise de sentimento das noticias (NLP);
- interpretacao dos indicadores tecnicos;
- geracao de hipoteses de compra e venda.

### 4.3 Acao
- emissao de recomendacao com justificativa;
- resposta a perguntas em linguagem natural;
- registro do raciocinio (Chain-of-Thought).

## 5. Fluxo tecnico pedido

Fluxo declarado no enunciado:
1. coleta de dados (mercado + noticias);
2. processamento (NLP + indicadores tecnicos);
3. analise por LLM Agent com ReAct/Chain-of-Thought;
4. recomendacao final: COMPRAR, VENDER ou AGUARDAR com justificativa.

## 6. Ferramentas (tools) esperadas no agente

Tools descritas no enunciado:
- search_news(ticker)
- get_price_data(ticker, period)
- calculate_indicators(data)
- generate_recommendation(analysis)

## 7. Fontes e componentes de dados citados

### 7.1 Mercado e indicadores
- yfinance para precos historicos (OHLCV);
- pandas-ta ou TA-Lib para indicadores tecnicos.

### 7.2 Noticias
- RSS via feedparser, com fontes como InfoMoney, B3 e Reuters.

### 7.3 Estrutura esperada de registro diario por ticker
Exemplo citado no enunciado:
{
  "ticker": "VALE3",
  "date": "2024-11-15",
  "close": 61.42,
  "rsi": 45.2,
  "macd_signal": "bullish",
  "news_sentiment": 0.72,
  "recommendation": "COMPRAR"
}

## 8. Entregas esperadas (avaliacao)

A solucao deve ser um AI Agent funcional em Python, entregue via notebook ou repositorio, contendo:
1. Coleta e pre-processamento:
   - pipeline com precos historicos, indicadores e noticias.
2. Analise de sentimento:
   - classificacao com LLM ou modelo de NLP treinado.
3. AI Agent com tools:
   - implementado com LangChain, AutoGen ou similar;
   - pelo menos 3 ferramentas definidas.
4. Recomendacoes e backtest:
   - gerar COMPRAR/VENDER/AGUARDAR;
   - registrar raciocinio;
   - backtest opcional.

## 9. Indicadores de avaliacao

O enunciado explicita avaliacao por:
- acuracia das recomendacoes (acerto de tendencia);
- qualidade do raciocinio (Chain-of-Thought coerente e explicavel);
- desempenho financeiro por backtest (opcional, valorizado), comparando com Buy-and-Hold;
- interface conversacional (opcional).

## 10. Itens opcionais/sugeridos no enunciado

Itens que aparecem como sugestao, opcao ou valorizacao:
- dados fundamentalistas (fundamentus);
- NLP com FinBERT, VADER ou spaCy;
- modelos LLM proprietarios (OpenAI/Claude) ou alternativa local (Llama 3 via Ollama);
- visualizacao com Plotly/Matplotlib como tool do agente;
- multiagente especializado (noticias, tecnico, orquestrador);
- memoria de longo prazo;
- alertas automaticos (email/Telegram);
- comparador de carteiras;
- agente de explicabilidade.

## 11. Checklist de aderencia objetiva (sim/nao)

Checklist para uso nas proximas etapas:
- [ ] 4 tickers obrigatorios implementados.
- [ ] monitoramento continuo e recomendacoes diarias implementados.
- [ ] pipeline de coleta + pre-processamento implementado.
- [ ] analise de sentimento com LLM ou NLP treinado implementada.
- [ ] LLM Agent no loop de analise implementado.
- [ ] ReAct/Chain-of-Thought registrado implementado.
- [ ] agente em LangChain/AutoGen/similar implementado.
- [ ] no minimo 3 tools do agente implementadas.
- [ ] recomendacao COMPRAR/VENDER/AGUARDAR com justificativa implementada.
- [ ] backtest implementado (opcional).
- [ ] comparacao Buy-and-Hold implementada (opcional, valorizada).
- [ ] interface conversacional implementada (opcional).

## 12. Resultado da validacao PDF vs MD

Validacao realizada nesta sessao:
- foi gerado um novo markdown diretamente do PDF fonte;
- comparacao textual linha a linha sem diferencas;
- conclusao: pode-se usar materialAula/Projeto_Integrado_AI_Agents_v2.md como referencia oficial equivalente ao PDF.
