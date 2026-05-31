# 02 - Arquitetura do Agente

## Visão arquitetural

Fluxo macro:

1. Coleta dados de mercado (OHLCV) dos ativos.
2. Coleta notícias por ticker e classifica sentimento.
3. Calcula indicadores técnicos.
4. Consolida evidências por ativo em base de análise diária.
5. Agente decisor consome a análise e gera recomendação com justificativa.
6. Interface conversa com usuário e apresenta resultado.

## Abordagem escolhida

Abordagem orientada a tools com loop de decisão, em arquitetura multiagente:

- Agente 1 (Market Intelligence): busca notícias, classifica sentimento e atualiza base analítica.
- Agente 2 (Trading Decision): consome base analítica, avalia sinais técnicos e decide COMPRAR/VENDER/AGUARDAR.
- O resultado final é sempre ancorado em dados estruturados do dia.
- O raciocínio é registrado em formato auditável, sem expor cadeia interna sensível do modelo.

## Agentes e responsabilidades

### Agente de notícias e sentimento

- Ingestão de RSS por fonte e ticker.
- Deduplicação e sumarização.
- Classificação de sentimento e impacto.
- Publicação da análise intermediária.

### Agente decisor de recomendação

- Consumo das análises intermediárias e indicadores técnicos.
- Aplicação da política de decisão e score de confiança.
- Geração de recomendação final e justificativa em linguagem natural.

### Possíveis agentes adicionais (evolução)

- Agente de monitoramento/qualidade de dados.
- Agente de backtest e avaliação de estratégia.
- Agente de explicabilidade e relatório executivo.

## Ferramentas mínimas (requisito acadêmico)

- search_news(ticker)
- get_price_data(ticker, period)
- calculate_indicators(data)
- generate_recommendation(analysis)

## Decisões arquiteturais iniciais

- Python como linguagem principal.
- Estrutura modular em camadas: ingestão, análise, multiagente, interface.
- Persistência inicial local (arquivos/SQLite) para acelerar entrega.
- Processo diário reexecutável para reproduzir resultados.
- Configuração de ambiente via arquivo `.env` com parâmetros de Azure AI Foundry.

## Guardrails

- Respostas devem indicar incerteza quando houver dados insuficientes.
- Toda recomendação deve citar sinais técnicos e sentimento usados.
- Sem aconselhamento financeiro absoluto; saída educacional e explicativa.
