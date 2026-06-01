
# PROJETO INTEGRADO


# AI AGENTS

---
*Página 1*

# O DESAFIO:

A QuantumFinance está expandindo sua atuação para o mercado de renda variável e deseja oferecer aos seus
clientes um Assistente de Investimentos baseado em AI Agents capaz de recomendar operações de compra e
venda de ações de forma autônoma e explicável.
Para isso, a empresa identificou a necessidade de um agente inteligente que combine:
•
Análise de notícias e sentimentos do mercado financeiro em tempo real
•
Indicadores técnicos de análise gráfica (RSI, MACD, Médias Móveis, Bandas de Bollinger)
•
Raciocínio e tomada de decisão autônoma com justificativa para o usuário
•
Interface conversacional para consulta e explicação das recomendações


---
*Página 2*

# O DESAFIO:

As seguintes ações foram selecionadas para a primeira versão do agente:

# VALE3

Vale do Rio Doce
Mineração

# PETR4

Petrobras
Energia

# BBAS3

Banco do Brasil
Financeiro

# ITUB4

Itaú Unibanco
Financeiro
O agente deverá monitorar continuamente essas ações, coletar dados de mercado e notícias, e emitir recomendações
diárias fundamentadas.


---
*Página 3*

# O DESAFIO:

O Assistente de Investimentos deve ser construído como um AI Agent com as seguintes capacidades:

### PERCEPÇÃO

•
Leitura de feeds de notícias
financeiras
•
Coleta de preços e volumes
via API
•
Extração de indicadores
técnicos

### RACIOCÍNIO

•
Análise de sentimento das
notícias (NLP)
•
Interpretação dos indicadores
técnicos
•
Geração de hipóteses de
compra/venda

### AÇÃO

•
Emissão de recomendação
com justificativa
•
Resposta a perguntas em
linguagem natural
•
Registro do raciocínio (Chain-
of-Thought)


---
*Página 4*

# COMO RESOLVER O PROBLEMA:

O agente deverá integrar duas fontes principais de dados para emitir suas recomendações:

### ANÁLISE DE NOTÍCIAS

•
Fontes: RSS feeds (InfoMoney, B3, Reuters) via
feedparser (open source)
•
Processamento com LLM para classificar
sentimento: Positivo / Negativo / Neutro
•
Score de impacto por ação monitorada
•
Sumarização automática dos principais eventos

### INDICADORES TÉCNICOS

•
RSI — Índice de Força Relativa
(sobrecomprado/sobrevendido)
•
MACD — Convergência/Divergência de Médias
Móveis
•
Médias Móveis Simples e Exponenciais
(SMA/EMA)
•
Bandas de Bollinger e Volume

# ⊕

---
*Página 5*

# COMO RESOLVER O PROBLEMA:

Fluxo de execução do AI Agent:

### 1


### Coleta de Dados

APIs de mercado
+ Feeds de notícias

### 2


### Processamento

NLP + Indicadores
técnicos calculados

### 3


### Análise pelo


### LLM Agent

ReAct / Chain-of-Thought
reasoning

### 4


### Recomendação

COMPRAR / VENDER /
AGUARDAR + justificativa
O agente utiliza a estratégia ReAct (Reasoning + Acting) — raciocina passo a passo antes de emitir cada recomendação,
registrando o raciocínio de forma transparente para o usuário.

### Ferramentas (Tools) do Agente: search_news(ticker)  |  get_price_data(ticker, period)  |  calculate_indicators(data)  |

generate_recommendation(analysis)  —  Dados via yfinance + feedparser (ambos open source)


---
*Página 6*

# COMO RESOLVER O PROBLEMA:

Fontes de dados sugeridas para o projeto:

### Tipo de Dado


### Fonte Sugerida


### Formato

Preços históricos de ações
yfinance (open source, Yahoo Finance)
DataFrame (OHLCV)
Notícias financeiras
feedparser — RSS feeds InfoMoney, B3, Reuters
JSON / RSS Feed
Indicadores técnicos
pandas-ta ou TA-Lib (open source)
DataFrame
Dados fundamentalistas
fundamentus (open source, scraping B3)
DataFrame
Exemplo de estrutura de dado esperada para cada ação em cada dia de análise:
{ "ticker": "VALE3", "date": "2024-11-15", "close": 61.42, "rsi": 45.2, "macd_signal": "bullish",
"news_sentiment": 0.72, "recommendation": "COMPRAR" }


---
*Página 7*

# O QUE É ESPERADO COMO ENTREGA?

A solução deve ser um AI Agent funcional, implementado em Python, com entrega em Jupyter Notebook ou
repositório GitHub:

# 01


### Coleta e Pré-processamento

Pipeline de dados: preços históricos, cálculo de
indicadores técnicos e coleta de notícias.

# 02


### Análise de Sentimento

Classificação de notícias financeiras usando LLM ou
modelo de NLP treinado.

# 03


### AI Agent com Tools

Agente implementado com LangChain, AutoGen ou
similar, com pelo menos 3 ferramentas definidas.

# 04


### Recomendações e Backtest

O agente deve gerar recomendações
(COMPRAR/VENDER/AGUARDAR) e registrar o
raciocínio. Backtest opcional.


---
*Página 8*

# O QUE É ESPERADO COMO ENTREGA?

Os seguintes indicadores devem ser apresentados na avaliação do agente:

### Acurácia das recomendações

Comparação entre as recomendações do agente e o comportamento real das ações no período de teste (acerto de
tendência).

### Qualidade do raciocínio (Chain-of-Thought)

O agente deve registrar o passo a passo do raciocínio que levou à recomendação, de forma coerente e explicável.

### Desempenho financeiro via Backtest (opcional, mas valorizado)

Simulação do retorno financeiro caso as recomendações do agente fossem seguidas no período de teste. Comparar com
estratégia Buy-and-Hold.

### Interface conversacional (opcional)

Chatbot ou interface em que o usuário pode perguntar: 'Por que você recomendou comprar PETR4 hoje?'


---
*Página 9*

# O PROBLEMA:


# O que mais seria possível ser feito???

A criatividade é totalmente permitida desde que utilize AI Agents de forma coerente e inovadora.
Multi-agente: um agente de notícias + um agente técnico + um agente orquestrador tomador de decisão
Agente com memória de longo prazo: lembrar de eventos macroeconômicos passados e seu impacto nas ações
Alertas automáticos: agente que envia e-mail ou mensagem no Telegram com recomendações diárias
Comparador de carteiras: agente que monta e avalia carteiras de ações com base em perfil de risco do usuário
Agente de explicabilidade: gera relatórios em linguagem natural justificando cada recomendação para o cliente


---
*Página 10*

# TECNOLOGIAS SUGERIDAS:

Frameworks de AI Agents
LangChain, LangGraph, Google ADK
Modelos de Linguagem
OpenAI GPT-4o ¹, Anthropic Claude ¹, Llama 3 via Ollama (open source e local)
Dados de Mercado
yfinance (open source) — preços históricos via Yahoo Finance, sem necessidade de API key
Notícias Financeiras
feedparser (open source) — leitura de RSS feeds: InfoMoney, Reuters, B3, Valor Econômico
Análise Técnica
pandas-ta (open source), TA-Lib (open source), mplfinance (open source)
NLP / Sentimento (Opcional)
FinBERT via HuggingFace transformers (open source), VADER (open source), spaCy (open source)
Visualização / Interface
Plotly (open source), Matplotlib (open source) – Como Tool do Agente
¹ Modelos proprietários — exigem chave de API paga. Alternativa gratuita: Llama 3 via Ollama (roda localmente).


---
*Página 11*

# OBRIGADO


# FIAP

Copyright © 2026 | Professor Felipe Gustavo Silva Teodoro
Todos os direitos reservados. A reprodução ou divulgação total ou parcial deste documento é expressamente proibida sem consentimento formal, por
escrito, do professor(a)/autor(a).


---
*Página 12*

