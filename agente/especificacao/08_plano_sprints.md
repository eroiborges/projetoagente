# 08 - Plano de Sprints

## Sprint 0 - Alinhamento e setup

Status: CONCLUIDA

Objetivo: fechar decisões abertas e preparar base do projeto.

Entregas:

- Definição de arquitetura multiagente (mínimo dois agentes funcionais).
- Estrutura de pastas em `agente/` com separação por agentes, tools e pipelines.
- requirements.txt inicial.
- Checklist de fontes e variáveis de ambiente do Azure AI Foundry.
- Definição de modo de execução único com duas formas de disparo: on-demand e agendável.
- Definição de escopo de execução por parâmetro: todos os tickers ou ticker único.

Critérios de pronto:

- Projeto executa localmente.
- Decisões de stack e escopo documentadas.
- Configuração é reparametrizável para outro ambiente sem alterar código.
- Backtest definido como trilha completa, iniciando com versão mínima e incrementos nas sprints seguintes.

## Sprint 1 - Pipeline de mercado e indicadores

Status: CONCLUIDA

Objetivo: obter sinal técnico confiável por ticker.

Entregas:

- Coleta OHLCV com yfinance.
- Cálculo de RSI, MACD, SMA/EMA, Bollinger e volume médio.
- Persistência em JSON de snapshots e histórico técnico com deduplicação por ticker+data+modo.
- Status operacional por ticker para mercado/notícias com fallback seguro.
- Testes básicos de consistência temporal.

Critérios de pronto:

- Todos os 4 ativos com indicadores calculados para a data de referência.
- Sem falhas em execução repetida no mesmo dia.

Resultado da sprint:

- Pipeline técnico real funcional para os ativos alvo com fallback por ticker sem interromper o lote.
- Contratos de dados e persistência técnica validados por testes automatizados.

## Sprint 2 - Notícias e sentimento

Status: CONCLUIDA

Objetivo: gerar sinal de sentimento por ticker.

Entregas:

- Coletor RSS multi-fonte com deduplicação.
- Classificação de sentimento (positivo/negativo/neutro).
- Score de impacto por ticker.
- Persistência da tabela news_items.

Critérios de pronto:

- Notícias recentes associadas aos 4 tickers.
- Score de sentimento disponível por ticker no dia.

Plano de execução desta sprint:

1. Consolidar contrato de dados de notícias (`news_items`) com campos mínimos: ticker, source, published_at, title, url, summary, sentiment_label, sentiment_score, impact_score, data_mode.
2. Implementar coleta estruturada de itens de notícia por ticker (não só agregado), mantendo deduplicação por `url` ou hash de `title+source+published_at`.
3. Implementar `impact_score` por notícia com regra heurística inicial (recência + palavras de impacto + relevância do ticker no texto).
4. Persistir `news_items` em JSON dedicado (`agente/data/news_items.json`) com append idempotente.
5. Expor no pipeline resumo diário por ticker: total de notícias, distribuição de sentimento e média de impacto.
6. Cobrir com testes unitários e de integração: deduplicação, classificação de sentimento, cálculo de impacto e persistência.

Definição de pronto operacional:

- Para VALE3, PETR4, BBAS3 e ITUB4 existe saída diária com sentimento e impacto.
- O arquivo de `news_items` é gerado sem duplicatas em reexecuções no mesmo dia.
- Status por ticker informa `matched_news_count` e não quebra a execução de lote por falha de uma fonte.

Resultado da sprint:

- Coleta estruturada por item de notícia com deduplicação e persistência em `agente/data/news_items.json`.
- Classificação de sentimento por notícia e consolidação por ticker.
- `impact_score` por notícia e resumo no status por ticker com média diária.

## Sprint 3 - Agente com tools

Status: CONCLUIDA

Objetivo: colocar o agente para orquestrar dados e responder perguntas.

Entregas:

- Tools implementadas e testadas.
- Orquestração entre agente de notícias e agente decisor.
- Loop de tool calling com limite de iteração por agente.
- Prompt de sistema com regras de transparência e segurança.
- Governança dos artefatos de execução em `agente/data/` para testes do time (manter snapshots de referência e evitar ruído em commits de código).
- Chat do usuário para consultar recomendações por ticker e pedir explicações baseadas em dados do dia (indicadores + notícias + status).

Critérios de pronto:

- Cada agente cumpre seu papel com contrato de dados definido.
- Solução usa no mínimo 3 tools de forma funcional.
- Perguntas de explicação por ticker respondidas corretamente.

Resultado da sprint:

- Chat lateral na app com explicacoes em PT-BR para `por que`, `o que mudaria`, `qual o risco` e `resumo`.
- `system_prompt` explicito do agente explicador com regras de transparencia, simplicidade e nao-alucinacao.
- Loop deterministico de tool calling no agente explicador com limite de iteracoes.
- Sugestoes de perguntas coerentes com a recomendacao atual para melhorar a demo.

## Sprint 4 - Recomendação e explicabilidade

Status: CONCLUIDA

Objetivo: padronizar recomendação final com justificativa robusta.

Entregas:

- Regra de decisão combinando técnico + sentimento.
- confidence_score por recomendação.
- Rationale padronizado com evidências rastreáveis.
- Registro diário em arquivo estruturado.
- Primeira versão funcional de backtest (mínima) para validar direção da estratégia.
- Evolução do chat para explicabilidade avançada: respostas comparativas entre tickers, justificativas detalhadas e transparência de limites/assunções.

Critérios de pronto:

- Cada ticker recebe recomendação COMPRAR/VENDER/AGUARDAR.
- Justificativa cita indicadores e sentimento usados.

Andamento atual:

- `rationale` da recomendacao padronizada com tecnico, noticias e decisao final.
- Contrato simples de evidencias adicionado a `Recommendation` com scores, fatores e gatilhos de mudanca.
- Chat passou a reutilizar essas evidencias nas respostas de explicacao.
- Registro estruturado da recomendacao adicionado em arquivo dedicado com status, scores e evidencias por ticker.
- Backtest minimo implementado a partir de `recommendation_records` e `technical_history`.
- Backtest evoluido com resumo por ticker e filtro opcional por janela de datas.
- Chat evoluido com comparacoes simples entre tickers na mesma execucao.
- App passou a exibir painel de backtest minimo com resumo agregado e por ticker.

## Sprint 5 - Validação final e entrega acadêmica

Status: CONCLUIDA

Objetivo: consolidar qualidade, demo e documentação.

Entregas:

- Bateria de casos de teste de demonstração.
- Ajustes de robustez e mensagens de erro.
- Documento final de execução e limitações.
- Roteiro de apresentação.
- Evolução do backtest para versão completa com métricas consolidadas.

Critérios de pronto:

- Execução de demo ponta a ponta sem intervenção.
- Entrega pronta para avaliação acadêmica.

Andamento atual:

- Bateria de casos de teste de demonstração implementada em `tests/test_demo_sprint5.py` com cenários de pipeline mock ponta a ponta, perguntas-chave do chat, comparação entre tickers e integração de backtest.
- Suíte de demo validada localmente com `5 passed`.
- Ajustes de robustez aplicados no backtest e na app: validação de janela/data, tratamento de JSON inválido e mensagens amigáveis em tela para falhas de execução.
- Testes de robustez adicionados em `tests/test_backtest_tool.py` e validados junto da suíte de demo (`12 passed`).
- Documento final de execução e limitações adicionado em `especificacao/09_execucao_final_limitacoes.md`.
- Roteiro de apresentação adicionado em `especificacao/10_roteiro_apresentacao.md`.
- Documentação consolidada para entrega final (README e arquivos de especificação atualizados com a estrutura implementada).

## Ordem recomendada de execução

1. Sprint 0
2. Sprint 1
3. Sprint 2
4. Sprint 3
5. Sprint 4
6. Sprint 5
