# 08 - Plano de Sprints (reconstrucao total)

Base de referencia unica:
- materialAula/Projeto_Integrado_AI_Agents_v2.pdf
- materialAula/Projeto_Integrado_AI_Agents_v2.md (validado como identico ao PDF)

Regra deste plano:
- Somente tarefas derivadas do enunciado do professor.
- Sem funcionalidades fora do pedido.

Nota de linguagem:
- Priorizar termos em portugues do Brasil na interface, na documentacao e nos textos de saida para o usuario.
- Manter termos tecnicos em ingles somente quando forem nomes padrao de mercado/tecnologia (ex.: RSI, MACD, Backtest, Buy-and-Hold, LangChain, ReAct).

Decisoes tecnicas fixadas nesta sessao:
- Framework do agente: LangChain.
- Modelo LLM: Azure OpenAI.
- Sentimento: NLP treinado (nao LLM).
- Registro de raciocinio: log detalhado de passos ReAct.
- Monitoramento na UI: opcao de reexecucao automatica em sessao (5, 15 ou 30 minutos), com loop de consultas e atualizacao em tela.
- Prioridade: incluir no MVP os itens opcionais valorizados (backtest vs buy-and-hold e chat).

## 1. Backlog mestre de requisitos -> tarefas

### 1.1 Objetivo principal (AI Agent de investimentos)
- Definir agente capaz de recomendar COMPRAR/VENDER/AGUARDAR com justificativa.
- Cobrir os tickers obrigatorios: VALE3, PETR4, BBAS3, ITUB4.

### 1.2 Percepcao
- Implementar leitura de noticias financeiras via RSS (InfoMoney, B3, Reuters).
- Implementar coleta de precos e volume via API de mercado.
- Implementar calculo de indicadores tecnicos (RSI, MACD, SMA/EMA, Bollinger, volume).

### 1.3 Raciocinio
- Implementar analise de sentimento das noticias com NLP treinado.
- Interpretar indicadores tecnicos por ticker.
- Gerar hipotese de compra/venda/aguardar por ticker.

### 1.4 Acao
- Emitir recomendacao por ticker com justificativa.
- Responder perguntas em linguagem natural na interface.
- Registrar raciocinio do agente em formato ReAct (passo a passo).

### 1.5 Fluxo obrigatorio do agente
- Coleta de dados.
- Processamento (NLP + indicadores).
- Analise pelo LLM Agent usando ReAct/Chain-of-Thought.
- Recomendacao final.

### 1.6 AI Agent com tools
- Implementar agente com LangChain.
- Definir no minimo 3 tools operacionais.
- Cobrir as tools declaradas no enunciado:
	- search_news(ticker)
	- get_price_data(ticker, period)
	- calculate_indicators(data)
	- generate_recommendation(analysis)

### 1.7 Estrutura e dados
- Garantir registros diarios por ticker contendo os campos esperados no enunciado (ticker, date, close, rsi, macd_signal, news_sentiment, recommendation).

### 1.8 Entregas de avaliacao
- Entrega 01: coleta e pre-processamento.
- Entrega 02: analise de sentimento com LLM ou NLP treinado.
- Entrega 03: AI Agent com LangChain/AutoGen/similar e >= 3 tools.
- Entrega 04: recomendacoes + registro do raciocinio + backtest (opcional).

### 1.9 Indicadores de avaliacao
- Acuracia das recomendacoes (acerto de tendencia).
- Qualidade do raciocinio (CoT/ReAct coerente e explicavel).
- Desempenho financeiro (backtest) com comparacao Buy-and-Hold.
- Interface conversacional.

## 2. Plano de sprints (novo)

## Sprint 1 - Fundacao de dados e contratos

Objetivo:
- Fechar a base de dados e contratos obrigatorios para os 4 tickers.

Tarefas:
1. Padronizar contratos diarios por ticker com campos do enunciado.
2. Validar coleta de precos/volume para VALE3, PETR4, BBAS3, ITUB4.
3. Validar calculo de RSI, MACD, SMA/EMA, Bollinger e volume.
4. Integrar coleta RSS para InfoMoney, B3 e Reuters.
5. Definir persistencia de dados de entrada e saida por dia/ticker.

Criterios de pronto:
- 4 tickers processados ponta a ponta na etapa de percepcao.
- Dados diarios salvos no contrato esperado.

Andamento desta sprint:
- Contrato diario implementado e persistido em `data/daily_analysis.json` com campos: ticker, date, close, rsi, macd_signal, news_sentiment, recommendation e data_mode.
- Validacao operacional realizada com os 4 tickers em modo mock, com geracao correta dos registros diarios por ticker.

## Sprint 2 - Sentimento com NLP treinado

Objetivo:
- Entregar analise de sentimento conforme entrega 02 do enunciado.

Tarefas:
1. Selecionar e integrar modelo de NLP treinado para sentimento.
2. Classificar noticias em positivo/negativo/neutro por ticker.
3. Calcular score de sentimento agregado por ticker.
4. Implementar score de impacto por ticker.
5. Implementar sumarizacao automatica dos principais eventos.

Criterios de pronto:
- Toda noticia relevante tem classe de sentimento.
- Cada ticker possui score consolidado no dia.
- Existe resumo automatico dos principais eventos por ticker.

Andamento desta sprint:
- Classificacao de sentimento migrada para modelo NLP com VADER (com ajuste de lexico financeiro em portugues).
- Pipeline passou a gerar `news_summary` automatico por ticker a partir dos eventos de maior impacto no ciclo.
- UI passou a exibir o resumo de noticias no quadro de status por ticker.

## Sprint 3 - AI Agent com LangChain e tools

Objetivo:
- Entregar o agente com framework e toolset exigidos.

Tarefas:
1. Implementar agente em LangChain.
2. Implementar as tools declaradas no enunciado.
3. Conectar tools no loop do agente para decisao por ticker.
4. Garantir uso de no minimo 3 tools em execucao real.
5. Registrar logs de chamada de tools para auditoria.

Criterios de pronto:
- Agente funcional com LangChain.
- Tool calling ativo com no minimo 3 tools.
- Recomendacao final gerada pelo fluxo do agente.

Andamento desta sprint:
- Agente de investimento implementado com estrutura de tools em LangChain.
- Tools exigidas pelo enunciado implementadas: `search_news`, `get_price_data`, `calculate_indicators`, `generate_recommendation`.
- Pipeline principal passou a gerar recomendacao via fluxo do agente de tools, mantendo persistencia e contratos existentes.

## Sprint 4 - ReAct, recomendacao e explicabilidade

Objetivo:
- Entregar raciocinio e recomendacao com explicabilidade conforme avaliacao.

Tarefas:
1. Implementar ciclo ReAct no agente (Thought, Action, Observation, Decision).
2. Registrar trilha de raciocinio por ticker em log estruturado.
3. Emitir recomendacao COMPRAR/VENDER/AGUARDAR com justificativa.
4. Implementar interface conversacional para perguntas do tipo "por que recomendou X?".
5. Implementar monitoramento em sessao na UI com reexecucao automatica da analise a cada 5, 15 ou 30 minutos.
6. Exibir na tela status do monitoramento, ultima execucao e atualizacao dos resultados em cada ciclo.
7. Garantir consistencia entre recomendacao, dados e explicacao no chat.

Criterios de pronto:
- Cada recomendacao tem justificativa e trilha de raciocinio auditavel.
- Chat responde perguntas coerentes com dados e decisao.
- Monitoramento em sessao executa ciclos automaticos no intervalo escolhido (5, 15 ou 30 minutos) com atualizacao visivel em tela.

Status desta sprint: concluida.

Entregas desta sprint:
- Trilha ReAct estruturada adicionada no agente com passos de Thought/Action/Observation por ciclo.
- Reflexao de explicabilidade com Azure OpenAI integrada ao agente em modo estrito (sem fallback de decisao/reflexao no fluxo principal).
- UI atualizada com monitoramento em sessao: iniciar/parar monitoramento, intervalos de 5/15/30 minutos, ultima e proxima execucao em tela.
- UI reorganizada em dois blocos claros: "Execucao sob demanda" e "Agendamento de monitoramento".

## Sprint 5 - Avaliacao final e metricas

Objetivo:
- Fechar os indicadores de avaliacao do professor com evidencias.

Tarefas:
1. Calcular acuracia de recomendacoes (acerto de tendencia).
2. Implementar backtest da estrategia do agente.
3. Implementar comparacao de desempenho vs Buy-and-Hold.
4. Consolidar relatorio de metricas para apresentacao.
5. Executar testes finais de regressao no fluxo completo.

Criterios de pronto:
- Acuracia reportada por ticker e consolidada.
- Backtest com comparativo Buy-and-Hold disponivel.
- Evidencias prontas para avaliacao academica.

Status desta sprint: concluida.

Entregas desta sprint:
- Acuracia consolidada e por ticker calculada no modulo de backtest (taxa de acerto por tendencia).
- Comparativo de desempenho da estrategia vs Buy-and-Hold implementado com metricas de retorno medio e alpha medio.
- Relatorio consolidado de metricas adicionado para apresentacao (consolidado geral + ranking por alpha).
- UI atualizada para exibir metricas da estrategia, Buy-and-Hold e alpha no painel de backtest.
- Backtest atualizado com deduplicacao por ticker+data (mantem registro mais recente do dia) e diagnostico detalhado em tela.
- Testes de regressao executados com sucesso apos as alteracoes da sprint.

## 3. Ponto de delimitacao tecnica (aderencia)

Delimitacao:
- O monitoramento continuo sera atendido por monitoramento em sessao na UI (com tela aberta), por ciclos de 5, 15 ou 30 minutos.

Registro:
- Esta delimitacao deve ser documentada na entrega para caracterizar o modo de operacao do monitoramento.

## 4. Ordem de execucao

1. Sprint 1
2. Sprint 2
3. Sprint 3
4. Sprint 4
5. Sprint 5
