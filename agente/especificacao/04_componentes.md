# 04 - Componentes do Sistema

## 1. Interface
Arquivo: app/main.py

Responsabilidades:
- receber parametros de execucao;
- disparar pipeline;
- exibir tabelas e metricas;
- manter monitoramento em sessao;
- disponibilizar chat de explicacao.

## 2. Pipeline
Arquivo: app/pipelines/run_analysis.py

Responsabilidades:
- orquestrar execucao por ticker;
- invocar agente/tools;
- consolidar recomendacoes, status e artefatos;
- entregar RunResult para persistencia e UI.

## 3. Agentes
Arquivos: app/agents/langchain_agent.py, app/agents/explainer_agent.py, app/agents/decision_agent.py

Responsabilidades:
- executar tools do agente;
- montar trilha ReAct;
- gerar decisao e reflexao via Azure OpenAI (modo estrito no fluxo principal);
- responder perguntas do chat com contexto do ultimo ciclo (modo estrito via Azure OpenAI);
- manter `decision_agent.py` como modulo legado de regra deterministica (fora do fluxo principal atual).

## 4. Tools
Arquivos: app/tools/*.py

Responsabilidades:
- market_tool.py: coleta tecnica e indicadores.
- news_tool.py: coleta de noticias, sentimento e resumo.
- insight_tools.py: contexto para explicacoes.
- backtest_tool.py: acuracia, retorno e comparativo Buy-and-Hold.

## 5. Dominio e persistencia
Arquivos: app/domain/models.py, app/storage/json_store.py

Responsabilidades:
- definir contratos de dados;
- gravar artefatos em JSON com deduplicacao.
