# 11 - Auditoria de Aderencia do Material Existente

Base de comparacao:
- materialAula/Projeto_Integrado_AI_Agents_v2.pdf
- materialAula/Projeto_Integrado_AI_Agents_v2.md
- agente/especificacao/00_objetivos_professor.md

Criterio aplicado:
- Manter somente material 100% aderente ao pedido do professor.
- Material parcialmente aderente foi classificado para refatoracao/substituicao.
- Material nao aderente foi retirado da pasta ativa de especificacao.

## 1. Resultado executivo

Mantidos como ativos na especificacao:
- agente/especificacao/00_objetivos_professor.md
- agente/especificacao/08_plano_sprints.md
- agente/especificacao/11_auditoria_aderencia_material_existente.md

Movidos para legado nao aderente (historico):
- agente/especificacao/legado_nao_aderente/01_visao_geral.md
- agente/especificacao/legado_nao_aderente/02_arquitetura.md
- agente/especificacao/legado_nao_aderente/03_modelo_dados.md
- agente/especificacao/legado_nao_aderente/04_componentes.md
- agente/especificacao/legado_nao_aderente/05_tecnologias.md
- agente/especificacao/legado_nao_aderente/06_fluxos.md
- agente/especificacao/legado_nao_aderente/07_mvp_escopo.md
- agente/especificacao/legado_nao_aderente/09_execucao_final_limitacoes.md
- agente/especificacao/legado_nao_aderente/10_roteiro_apresentacao.md

## 2. Classificacao tecnica por modulo

### 2.1 Manter (aderente ao escopo base)

1. app/tools/market_tool.py
- Mantem coleta de preco/volume e calculo de indicadores tecnicos.
- Alinha com percepcao do enunciado (yfinance + RSI/MACD/SMA/EMA/Bollinger/volume).

2. app/storage/json_store.py
- Mantem persistencia estruturada e rastreavel para auditoria dos resultados.

3. app/domain/models.py
- Mantem contratos de dados gerais da aplicacao.
- Ajuste aplicado: contrato diario por ticker implementado para espelhar o formato esperado no enunciado.

4. app/tools/backtest_tool.py
- Mantem acuracia basica e retorno da estrategia.
- Observacao: falta comparativo Buy-and-Hold (item valorizado no enunciado).

### 2.2 Refatorar (parcialmente aderente)

1. app/main.py
- Exibe opcao Agendado, mas ainda nao implementa loop de monitoramento em sessao.
- Deve incluir reexecucao automatica em 5/15/30 min na UI com atualizacao em tela.

2. app/tools/backtest_tool.py
- Falta benchmark Buy-and-Hold no resultado consolidado.

3. app/domain/models.py
- Ajuste concluido para contrato diario por ticker.

### 2.3 Substituir (nao aderente ao pedido central)

1. app/agents/decision_agent.py
- Implementa regra deterministica por score fixo.
- Nao implementa LLM Agent nem ciclo ReAct/Chain-of-Thought.

2. app/agents/explainer_agent.py
- Chat por intents com roteamento fixo e templates.
- Nao usa LLM para raciocinio do agente.

3. app/agents/system_prompt.py
- Suporte do explicador atual, acoplado ao fluxo sem LLM framework.

4. app/pipelines/run_analysis.py
- Orquestra fluxo atual sem agente em framework (LangChain/AutoGen/similar).
- Nao executa monitoramento continuo por si.

5. app/tools/news_tool.py
- Sentimento por lexico estatico (regras de palavras).
- Enunciado exige LLM ou modelo NLP treinado para sentimento.

Atualizacao de aderencia (Sprint 2):
- Sentimento migrado para modelo NLP (VADER) com ajuste de lexico financeiro.
- Sumarizacao automatica dos principais eventos por ticker adicionada ao status operacional.

### 2.4 Atualizar dependencias

requirements.txt:
- Incluir stack necessaria para LangChain e modelo NLP treinado escolhido.
- Remover dependencias sem uso real no fluxo final.

## 3. Evidencias de nao aderencia identificadas

1. Decisao deterministica por threshold fixo:
- app/agents/decision_agent.py

2. Chat sem LLM (intencao por palavras-chave e plano fixo):
- app/agents/explainer_agent.py

3. Sentimento por lista de palavras:
- app/tools/news_tool.py

4. Modo agendado declarado, sem loop de monitoramento implementado:
- app/main.py
- app/pipelines/run_analysis.py

5. Ausencia de framework de agente no codigo:
- app/ (sem uso de LangChain/AutoGen no fluxo implementado)

Atualizacao de aderencia (Sprint 3):
- Agente com framework LangChain implementado no modulo `app/agents/langchain_agent.py`.
- Toolset alinhado ao enunciado (search_news, get_price_data, calculate_indicators, generate_recommendation) integrado ao pipeline.

Atualizacao de aderencia (Sprint 4):
- Trilha de raciocinio ReAct registrada no ciclo do agente com Thought/Action/Observation.
- Integracao de LLM (Azure OpenAI) conectada ao agente para reflexao de explicabilidade, com fallback quando indisponivel.
- Monitoramento continuo em sessao implementado na UI com reexecucao automatica em 5/15/30 minutos e status de ciclo em tela.

Atualizacao de aderencia (Sprint 5):
- Acuracia das recomendacoes consolidada no backtest por taxa de acerto (acerto de tendencia), incluindo visao por ticker e consolidada.
- Comparacao de desempenho da estrategia vs Buy-and-Hold implementada com retorno medio e alpha medio.
- Relatorio consolidado de metricas disponibilizado para apresentacao na interface.

## 3.1 Evidencia de aderencia implementada na Sprint 1

- Registro diario por ticker implementado e persistido em `data/daily_analysis.json`.
- Campos presentes no artefato diario: ticker, date, close, rsi, macd_signal, news_sentiment, recommendation (com data_mode adicional para rastreabilidade operacional).
- Geracao validada em execucao com os 4 tickers do enunciado.

## 3.2 Nota de terminologia PT-BR

- A partir desta etapa, adota-se prioridade de termos em portugues do Brasil na interface, documentacao e textos de saida ao usuario.
- Termos tecnicos de mercado e tecnologia podem permanecer em ingles quando forem padrao consolidado.

## 4. Escopo ativo autorizado a partir desta auditoria

Somente material ativo para execucao:
- agente/especificacao/00_objetivos_professor.md
- agente/especificacao/08_plano_sprints.md
- agente/especificacao/11_auditoria_aderencia_material_existente.md

Todo o restante da especificacao antiga permanece apenas como historico em:
- agente/especificacao/legado_nao_aderente/

## 5. Validacao final de aderencia (2026-06-08)

Base da validacao:
- materialAula/Projeto_Integrado_AI_Agents_v2.md
- agente/especificacao/00_objetivos_professor.md

Resultado por requisito do professor:

1. Tickers obrigatorios (VALE3, PETR4, BBAS3, ITUB4): SIM
- Pipeline processa os 4 ativos no fluxo padrao.

2. Coleta de dados de mercado e indicadores tecnicos: SIM
- Coleta de OHLCV e indicadores (RSI, MACD, SMA/EMA, Bollinger, volume) ativa no modulo tecnico.

3. Coleta de noticias via RSS e processamento de sentimento: SIM
- Fontes RSS (InfoMoney, B3, Reuters e busca por ticker) ativas.
- Sentimento implementado com NLP (VADER), aderente ao enunciado (LLM ou NLP treinado).

4. AI Agent com framework e tools: SIM
- Agente implementado em LangChain com tools declaradas no enunciado:
	- search_news
	- get_price_data
	- calculate_indicators
	- generate_recommendation

5. Analise por LLM Agent com ReAct/Chain-of-Thought: SIM
- Decisao e explicacao operam em modo estrito com LLM.
- Trilha ReAct registrada por ciclo em evidencias do agente.

6. Recomendacao COMPRAR/VENDER/AGUARDAR com justificativa: SIM
- Recomendacao final emitida por ticker com confianca e rationale.

7. Interface conversacional para explicar recomendacoes: SIM
- Chat ativo com resposta em linguagem natural baseada no contexto do ciclo.

8. Monitoramento continuo dos ativos: SIM (delimitado)
- Implementado como monitoramento em sessao na UI (5/15/30 min), com estado persistido e reexecucao automatica.

9. Registro diario por ticker no formato esperado: SIM
- Contrato diario persistido com campos requeridos e rastreabilidade operacional.

10. Acuracia e backtest com comparativo Buy-and-Hold: SIM
- Backtest implementado com hit rate, retorno medio da estrategia, retorno medio Buy-and-Hold e alpha medio.

11. Testes de regressao: SIM
- Suite automatizada ajustada para modo estrito de LLM e validada com sucesso.

Conclusao final:
- A implementacao atual esta aderente ao escopo e aos objetivos declarados pelo professor, considerando a delimitacao formal do monitoramento em sessao na interface.

## 6. Matriz de resolucao do feedback

| Item estava no feedback (/agent/feedback.md) | Resolveu o item do feedback? |
|---|---|
| Uso de LLM como nucleo do agente (decisao e explicacao) | Sim |
| Framework de AI Agents (LangChain/AutoGen/similar) | Sim |
| ReAct e Chain-of-Thought registrados no ciclo | Sim |
| Sentimento via NLP/LLM (nao apenas lexico estatico) | Sim |
| Sumarizacao automatica dos principais eventos | Sim |
| Monitoramento continuo e recomendacoes diarias autonomas | Sim (monitoramento em sessao com intervalo 5/15/30) |
| Tomada de decisao autonoma via IA | Sim |
| Tools no desenho exigido pelo enunciado | Sim |
| Estrutura de dado esperada por ticker/dia | Sim |
| Dados fundamentalistas (fundamentus) | Nao (opcional no enunciado) |
| Backtest comparado com Buy-and-Hold | Sim |
| Visualizacao com Plotly/Matplotlib como tool | Nao (sugerido, nao obrigatorio) |
| Multiagente especializado (noticias, tecnico, orquestrador) | Nao (sugerido, nao obrigatorio) |
| Entrega em notebook (alternativa ao repositorio) | Nao (repositorio GitHub foi adotado) |
| Integracao Azure OpenAI declarada e operante | Sim |
