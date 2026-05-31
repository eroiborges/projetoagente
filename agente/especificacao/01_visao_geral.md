# 01 - Visão Geral do Projeto

## Contexto

A QuantumFinance deseja um assistente de investimentos baseado em AI Agent para apoiar decisões em renda variável com explicabilidade.

## Objetivo

Construir um agente conversacional em Python que:

- Monitore VALE3, PETR4, BBAS3 e ITUB4
- Analise notícias e sentimento por ativo
- Calcule indicadores técnicos
- Gere recomendação COMPRAR, VENDER ou AGUARDAR com justificativa

## Problemas que vamos resolver

- Dificuldade de consolidar sinais técnicos e notícias em uma visão única.
- Falta de explicação transparente sobre por que recomendar uma ação.
- Dependência de análise manual para decisões repetitivas diárias.

## Personas

- Investidor iniciante: quer recomendação simples e explicada.
- Investidor intermediário: quer ver sinais e peso de cada evidência.
- Avaliador acadêmico: quer rastreabilidade do pipeline e do raciocínio.

## Casos de uso do MVP

1. Receber recomendação diária por ativo com justificativa.
2. Perguntar em linguagem natural: "Por que VALE3 ficou em AGUARDAR hoje?".
3. Consultar resumo de notícias e sentimento por ativo.
4. Consultar indicadores técnicos e estado atual (sobrecompra/sobrevenda etc.).

## Fora de escopo do MVP

- Execução automática de ordens reais em corretora.
- Estratégias de portfólio multiativo com otimização matemática avançada.
- Operação intraday em baixa latência.
