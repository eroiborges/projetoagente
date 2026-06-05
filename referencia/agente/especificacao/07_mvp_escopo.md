# 07 – Escopo do MVP e Roadmap

## Princípios do MVP

> O MVP deve provar o conceito de ponta a ponta com o mínimo de complexidade: um usuário faz uma pergunta em português, o agente consulta o Trino e responde com texto e/ou gráfico.

---

## O que está DENTRO do MVP

### Funcionalidades

| # | Funcionalidade                                         | Prioridade |
|---|--------------------------------------------------------|------------|
| 1 | Chat em PT-BR via interface Streamlit                  | P0         |
| 2 | Geração automática de SQL para consultas na camada Gold| P0         |
| 3 | Exibição de resultados tabulares (st.dataframe)        | P0         |
| 4 | Geração de gráficos (bar, line, pie, horizontal_bar)   | P0         |
| 5 | Memória de conversa dentro da sessão (últimas 10 trocas)| P0        |
| 6 | Tratamento de erros de SQL com auto-correção           | P1         |
| 7 | Truncamento de resultados grandes com aviso ao usuário | P1         |
| 8 | Tool `get_schema_info` para o agente inspecionar schema| P1         |
| 9 | Configuração via `.env` (endpoint Azure, Trino host)   | P0         |

### Dados

- Catálogo: `hive`
- Layer principal: **Gold** (8 tabelas)
- Layer secundária: **Silver** (quando o usuário precisar de dados mais detalhados)
- Fonte: CNPJ público de empresas brasileiras

---

## O que está FORA do MVP

| Item                                    | Justificativa                              | Fase       |
|-----------------------------------------|--------------------------------------------|------------|
| Autenticação / login de usuário         | Complexidade de infra desnecessária no MVP | Fase 2     |
| Controle de acesso por papel (RBAC)     | Depende de autenticação                    | Fase 2     |
| Agentes especializados (Financeiro, RH) | MVP valida o conceito com 1 agente         | Fase 2     |
| MCP Server                              | Padronização após validação do MVP         | Fase 2     |
| RAG sobre documentação de negócio       | Schema estático é suficiente para MVP      | Fase 2     |
| Exportação de resultados (CSV, Excel)   | Nice-to-have                               | Fase 2     |
| Deploy em produção com HTTPS            | Infra de produção                          | Fase 2     |
| Multimodalidade (upload de arquivos)    | Fora do escopo de dados do lake            | Backlog    |
| Persistência de histórico em DB         | Sessão em memória suficiente para validação| Fase 2     |

---

## Critérios de Aceitação do MVP

Para considerar o MVP entregue, as seguintes condições devem ser verdadeiras:

- [ ] Usuário consegue perguntar em português e receber resposta coerente
- [ ] Agente gera SQL correto para ao menos 10 perguntas de negócio de referência (golden set)
- [ ] Agente gera gráfico quando solicitado ou quando a resposta se beneficia de visualização
- [ ] Agente lida graciosamente com perguntas sem dados disponíveis (não trava, não alucina)
- [ ] Agente corrige erros de SQL automaticamente sem intervenção do usuário
- [ ] Histórico de conversa funciona (referências anafóricas dentro da sessão)
- [ ] Interface Streamlit carrega em < 3s e responde em < 30s para queries simples

---

## Golden Set — Perguntas de Validação

Conjunto de perguntas que o MVP deve responder corretamente:

| # | Pergunta                                                              | Esperado           |
|---|-----------------------------------------------------------------------|--------------------|
| 1 | Quantas empresas ativas existem no Brasil?                            | Número + texto     |
| 2 | Quais os 10 estados com mais estabelecimentos ativos?                 | Tabela + gráfico   |
| 3 | Qual a distribuição de empresas por porte?                            | Tabela + gráfico pizza |
| 4 | Quantas empresas abriram em 2023?                                     | Número + texto     |
| 5 | Quais os 5 setores com mais CNPJs ativos em São Paulo?                | Tabela + gráfico   |
| 6 | Quantas microempresas (ME) existem no Brasil?                         | Número + texto     |
| 7 | Qual a evolução de abertura de empresas por ano?                      | Tabela + linha     |
| 8 | Quais os municípios com mais empresas no Rio Grande do Sul?           | Tabela + gráfico   |
| 9 | Quantas empresas têm sócios estrangeiros?                             | Número + texto     |
|10 | Me mostre as empresas com maior capital social ativas em Minas Gerais | Tabela (top 10)    |

---

## Plano de Entregas

### Entrega 1 — Infraestrutura base (Dias 1–3)
- [ ] `trino_client.py` — cliente com execute + describe
- [ ] `config.py` — carregamento de `.env`
- [ ] Testes de conexão ao Trino
- [ ] `requirements.txt` inicial

### Entrega 2 — Tools do agente (Dias 4–6)
- [ ] `sql_tool.py` com validação e truncamento
- [ ] `schema_tool.py`
- [ ] `chart_tool.py` com 4 tipos de gráfico
- [ ] Testes unitários das tools

### Entrega 3 — System Prompt e Few-shots (Dias 7–9)
- [ ] `metadata/schemas.yml` com descrições de negócio
- [ ] `system_prompt.py` — DDL + glossário + regras
- [ ] `few_shots.py` — 10 exemplos do golden set
- [ ] Validação manual do prompt com o LLM

### Entrega 4 — Agente e Interface (Dias 10–13)
- [ ] `agent.py` — montagem do AgentExecutor
- [ ] `main.py` — interface Streamlit funcional
- [ ] Teste end-to-end com o golden set completo
- [ ] Ajustes de prompt baseados nos erros encontrados

### Entrega 5 — Polimento e Documentação (Dias 14–15)
- [ ] Tratamento de edge cases (query vazia, timeout, erro de rede)
- [ ] README da pasta `agente/` com instruções de setup
- [ ] Demo para stakeholders

---

## Fase 2 — Evolução Pós-MVP

### 2.1 Segurança e Acesso
- Autenticação (Azure AD / SSO)
- Controle de acesso: cada usuário/time vê apenas os dados permitidos
- Auditoria de queries executadas

### 2.2 Multi-Agente
- Agente Financeiro (dados contábeis da Contabilizei)
- Agente de Clientes (dados de relacionamento)
- Orquestrador que roteia perguntas para o agente especializado

### 2.3 Enriquecimento de Contexto (RAG)
- Glossário de negócio indexado como embeddings
- Documentação interna (regras de negócio, metadados ricos)
- Vector store: Azure AI Search ou pgvector

### 2.4 MCP Server
- Expor o agente como MCP server padronizado
- Consumo por Copilot Studio, VS Code Chat, outros clientes MCP

### 2.5 Experiência do Usuário
- Sugestões de perguntas contextuais
- Exportação de resultados (CSV, Excel, PNG do gráfico)
- Histórico persistido por usuário
- Dashboard de uso e queries mais populares
