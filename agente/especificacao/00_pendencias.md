# 00 - Pendências e Decisões Abertas

## Pendências de escopo

- Definir formato de entrega do MVP: app Streamlit, notebook, ou híbrido.
- Definir frequência de execução da análise: diária em batch e/ou sob demanda.
- Definir escopo de backtest para a entrega acadêmica (mínimo viável).

## Pendências técnicas

- Definir modelo inicial no Azure AI Foundry para cada agente.
- Escolher biblioteca de indicadores: pandas-ta ou TA-Lib.
- Definir fonte de notícias principal para estabilidade (InfoMoney, B3, Reuters via RSS).
- Definir formato de persistência do histórico de recomendações (CSV, SQLite, JSONL).

## Decisões já tomadas

- A estrutura principal do projeto fica em `agente/` na raiz de `materialAula`.
- O projeto terá mais de um agente funcional (mínimo dois).
- LLMs e inferência serão feitos via Azure AI Foundry.
- Endpoint, chaves e deployment ficarão em arquivo de configuração para reparametrização por ambiente.

## Riscos principais

- Ruído e latência nas fontes RSS.
- Limites de APIs e mudanças de formato em feeds.
- Alucinação do LLM em justificativas sem base em dados.
- Dificuldade de auditar recomendações sem trilha estruturada de decisão.

## Critério para fechar pendência

Cada pendência deve ser fechada com:

1. Decisão explícita.
2. Motivo da decisão.
3. Impacto em escopo, prazo e qualidade.
