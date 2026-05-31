# 00 - Contexto do Projeto

## Cenário

Este projeto acadêmico pede a construção de um AI Agent de investimentos para renda variável, com foco em quatro ativos:

- VALE3
- PETR4
- BBAS3
- ITUB4

O agente deve combinar sinais de notícias e indicadores técnicos para emitir recomendações diárias com justificativa em linguagem natural.

## Objetivo desta especificação

Documentar um plano de execução incremental, em sprints, para implementar o trabalho com entregas pequenas e verificáveis.

## Referência reaproveitada

Foi adotado como base o approach já validado em [referencia/agente](referencia/agente):

- Orquestração por tool calling
- Ferramentas separadas por responsabilidade
- Loop de decisão com limite de iterações
- Interface conversacional simples para validação rápida
- Foco em MVP antes de evoluções avançadas

## Resumo do que o trabalho exige

- Coleta e pré-processamento de dados de mercado
- Coleta e análise de notícias financeiras
- Cálculo de indicadores técnicos (RSI, MACD, SMA/EMA, Bollinger, volume)
- Agente com no mínimo 3 tools
- Recomendação COMPRAR/VENDER/AGUARDAR com justificativa
- Registro do raciocínio para transparência
- Entrega em Python (notebook ou repositório)
