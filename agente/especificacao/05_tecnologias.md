# 05 - Stack Tecnológica

## Linguagem e runtime

- Python 3.11+

## Bibliotecas de dados

- pandas
- numpy
- yfinance
- feedparser

## Indicadores técnicos

- pandas-ta-classic

## Fontes de notícias (Sprint 1)

- InfoMoney RSS direto.
- B3 via Google News RSS com filtro de domínio `b3.com.br`.
- Reuters via Google News RSS com filtro `reuters.com` para business/stocks.
- Feed dinâmico Google News por ticker para reduzir casos de `no_matching_news`.

Observação:

- TradingView é usado como fonte de leitura externa por ticker no app (link clicável), sem ingestão automática nesta fase.
- O link TradingView aparece junto da linha de recomendação para acesso rápido em nova aba.

## Agente e LLM

- OpenAI SDK compatível com Azure AI Foundry
- Estratégia de tool calling
- Múltiplos agentes especializados (notícias/sentimento e decisão)

## Configuração por ambiente

- Arquivo `.env` para endpoint, chave e deployment do Azure AI Foundry
- Classe de settings para centralizar parâmetros e facilitar reuso

Variáveis previstas:

- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_API_VERSION
- AZURE_OPENAI_DEPLOYMENT_NEWS
- AZURE_OPENAI_DEPLOYMENT_TRADING

## Interface

- Streamlit para validação rápida com usuário

## Persistência

- CSV/JSONL para MVP inicial
- SQLite opcional para histórico estruturado

## Testes

- pytest

## Observabilidade mínima

- Logs estruturados por etapa de pipeline
- Registro de erros por ticker/fonte
