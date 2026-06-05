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

Objetivo: gerar sinal de sentimento por ticker.

Entregas:

- Coletor RSS multi-fonte com deduplicação.
- Classificação de sentimento (positivo/negativo/neutro).
- Score de impacto por ticker.
- Persistência da tabela news_items.

Critérios de pronto:

- Notícias recentes associadas aos 4 tickers.
- Score de sentimento disponível por ticker no dia.

## Sprint 3 - Agente com tools

Objetivo: colocar o agente para orquestrar dados e responder perguntas.

Entregas:

- Tools implementadas e testadas.
- Orquestração entre agente de notícias e agente decisor.
- Loop de tool calling com limite de iteração por agente.
- Prompt de sistema com regras de transparência e segurança.

Critérios de pronto:

- Cada agente cumpre seu papel com contrato de dados definido.
- Solução usa no mínimo 3 tools de forma funcional.
- Perguntas de explicação por ticker respondidas corretamente.

## Sprint 4 - Recomendação e explicabilidade

Objetivo: padronizar recomendação final com justificativa robusta.

Entregas:

- Regra de decisão combinando técnico + sentimento.
- confidence_score por recomendação.
- Rationale padronizado com evidências rastreáveis.
- Registro diário em arquivo estruturado.
- Primeira versão funcional de backtest (mínima) para validar direção da estratégia.

Critérios de pronto:

- Cada ticker recebe recomendação COMPRAR/VENDER/AGUARDAR.
- Justificativa cita indicadores e sentimento usados.

## Sprint 5 - Validação final e entrega acadêmica

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

## Ordem recomendada de execução

1. Sprint 0
2. Sprint 1
3. Sprint 2
4. Sprint 3
5. Sprint 4
6. Sprint 5
