# 04 - Componentes do Sistema

## Estrutura proposta

- app/main.py: interface conversacional.
- app/orchestrator.py: coordenação do fluxo entre agentes.
- app/agents/news_agent.py: agente de notícias e sentimento.
- app/agents/trading_agent.py: agente decisor de compra/venda/aguardar.
- app/tools/news_tool.py: coleta e sumarização de notícias.
- app/tools/market_tool.py: coleta de preços históricos.
- app/tools/indicator_tool.py: cálculo de indicadores.
- app/tools/recommendation_tool.py: recomendação e justificativa.
- app/pipelines/daily_job.py: execução diária ponta a ponta.
- app/storage/repository.py: leitura e persistência de análises.
- app/config/settings.py: carregamento de configurações por ambiente.
- app/prompts/system_prompt.py: regras de comportamento do agente.
- tests/: testes unitários e de integração.

## Responsabilidades por componente

### Coleta de mercado

- Ler OHLCV por ticker e período.
- Tratar dados faltantes.
- Garantir ordenação temporal.

### Coleta de notícias

- Ler RSS por fonte.
- Relacionar notícia a ticker por matching simples e palavras-chave.
- Classificar sentimento e impacto.

### Motor de análise

- Calcular indicadores técnicos.
- Consolidar sinais técnicos e sentimento.
- Gerar score de confiança da recomendação.

### Camada de agentes

- Separar responsabilidades por agente (análise e decisão).
- Decidir quando chamar cada tool por etapa.
- Construir resposta em linguagem natural e explicável.
- Expor trilha de decisão resumida e auditável.

### Orquestração

- Encadear execução dos agentes na ordem correta.
- Garantir contrato de dados entre saída de análise e entrada de decisão.
- Registrar status de execução e falhas por etapa.
