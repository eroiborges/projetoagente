# 01 – Visão Geral do Projeto

## Contexto

A **Contabilizei** é uma empresa orientada a dados, com múltiplas fontes consolidadas em um data lake. O time de dados constrói pipelines de ingestão e tabelas processadas que respondem a problemas de negócio. Atualmente, qualquer consulta ou relatório ad-hoc depende de membros técnicos do time de BI, criando gargalo para as áreas de negócio.

## Objetivo

Construir um **agente de IA conversacional** que permita a usuários não técnicos:

- Fazer perguntas sobre dados em **linguagem natural (português)**
- Obter respostas acionáveis: tabelas, gráficos e insights textuais
- Explorar dados do lake sem necessidade de SQL ou programação
- Reduzir a dependência do time técnico para consultas rotineiras

## Domínio dos Dados (MVP)

Para o MVP, a fonte de dados é o **cadastro público de empresas brasileiro (CNPJ)**, organizado em três camadas no data lake:

| Camada   | Conteúdo                                                           |
|----------|--------------------------------------------------------------------|
| Bronze   | Dados brutos staged — tabelas `stg_cnpj_*`                        |
| Silver   | Dados integrados e enriquecidos — tabelas `int_*`                  |
| Gold     | Tabelas analíticas prontas para consumo — `dim_*` e `fact_*`       |

> O agente consumirá preferencialmente a camada **Gold**, que já entrega dados limpos e modelados.

## Personas

### Persona 1 — Analista de Negócio
- **Perfil**: Trabalha em áreas como operações, comercial ou produto
- **Dores**: Não sabe SQL; depende do time de dados para cada análise
- **Expectativa**: Perguntar "Quantas empresas ativas há em SP por setor?" e receber um gráfico e um resumo

### Persona 2 — Gestor / Executivo
- **Perfil**: Precisa de visão macro para tomada de decisão
- **Dores**: Relatórios estáticos chegam tarde ou com pouca flexibilidade
- **Expectativa**: Perguntar "Qual a distribuição de empresas por porte no Sul do Brasil?" e receber resposta imediata

### Persona 3 — Parceiro de Negócio (futuro)
- **Perfil**: Cliente ou parceiro externo com acesso controlado
- **Expectativa**: Consultar informações de mercado de forma autônoma

## Casos de Uso Prioritários (MVP)

1. Consulta de quantidade de empresas com filtros (UF, CNAE, porte, situação)
2. Ranking de cidades/estados por número de estabelecimentos ativos
3. Distribuição de empresas por setor econômico (CNAE)
4. Análise de sócios: tipo, qualificação, faixa etária
5. Evolução temporal de abertura de empresas (série histórica)
6. Geração de gráficos a partir das respostas (barras, pizza, linha)
7. Explicação em linguagem natural do resultado retornado

## Fora do Escopo do MVP

- Autenticação e controle de acesso por usuário
- Multi-agente (agente financeiro, de RH, etc.) — previsto para Fase 2
- Integração com Power BI ou dashboards embarcados
- Ingestão de novas fontes de dados fora do CNPJ
