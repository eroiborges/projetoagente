# 00 - Pendências e Decisões Abertas

## Pendências de escopo

- Nenhuma pendência crítica de escopo para Sprint 0.

## Pendências técnicas

- Nenhuma pendência técnica crítica de Sprint 0.

## Decisões já tomadas

- A estrutura principal do projeto fica em agente na raiz do workspace.
- O projeto terá mais de um agente funcional (mínimo dois).
- LLMs e inferência serão feitos via Azure AI Foundry.
- Endpoint, chaves e deployment ficarão em arquivo de configuração para reparametrização por ambiente.
- Formato de entrega do MVP: app Streamlit.
- Execução: on-demand e modo agendável com o mesmo código.
- Execução por escopo: todos os tickers ou apenas um ticker selecionado.
- Modelo inicial sugerido no Foundry: gpt-5.4-mini para agentes de notícias e decisão.
- Fontes de notícias: InfoMoney, B3 e Reuters, sem prioridade fixa.
- Regra de consenso de sentimento: empate sem consenso (ex: 50/50) deve resultar em neutro.
- Persistência inicial: JSON.
- Biblioteca de indicadores definida: pandas-ta.
- Backtest será completo, iniciado de forma incremental ao longo das sprints.
- Sprint 0 executa com dados mockados para acelerar setup e validação do fluxo.

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
