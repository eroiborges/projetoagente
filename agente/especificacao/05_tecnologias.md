# 05 - Stack Tecnológica

## Linguagem e runtime

- Python 3.11+

## Bibliotecas de dados

- pandas
- numpy
- yfinance
- feedparser

## Indicadores técnicos

- pandas-ta (preferencial para MVP)

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
