# 06 - Fluxos de Execucao

## 1. Fluxo de analise (por ciclo)
1. Selecionar escopo (todos ou unico ticker).
2. Coletar dados tecnicos e noticias.
3. Calcular sentimento e indicadores.
4. Executar agente com tools e trilha ReAct.
5. Gerar recomendacao com justificativa via Azure OpenAI.
6. Persistir resultados.
7. Exibir tabelas, status e backtest.

## 1.1 Fluxo de execucao sob demanda (UI)
1. Usuario clica em "Executar pipeline" no bloco de execucao manual.
2. Sistema executa um ciclo unico com as configuracoes atuais.
3. Resultados e evidencias ficam disponiveis imediatamente na tela.

## 2. Fluxo de monitoramento em sessao
1. Usuario define intervalo: 5, 15 ou 30 min.
2. Usuario inicia/parar monitoramento no bloco agendado.
3. Sistema agenda a proxima execucao automatica.
4. Em cada ciclo, executa pipeline e atualiza dados em tela.
4. Usuario pode interromper monitoramento a qualquer momento.

## 3. Fluxo de chat
1. Usuario pergunta sobre recomendacao, tecnico, noticias, risco ou comparacao.
2. Sistema identifica intencao e ticker.
3. Sistema monta contexto com tools de insight.
4. Agente explicador retorna resposta coerente com dados do ultimo ciclo.

## 4. Fluxo de backtest
1. Ler recommendation_records e technical_history.
2. Deduplicar sinais por ticker+data (manter o mais recente no dia).
3. Construir linhas de avaliacao por sinal.
3. Calcular acuracia, retorno da estrategia e retorno Buy-and-Hold.
4. Calcular alpha medio vs Buy-and-Hold.
5. Exibir consolidado, visao por ticker e diagnostico detalhado.
