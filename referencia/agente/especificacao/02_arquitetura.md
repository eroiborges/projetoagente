# 02 – Arquitetura do Agente

## Visão Arquitetural

```
┌─────────────────────────────────────────────────────────────────┐
│                        Interface (Streamlit)                     │
│           Input: pergunta em linguagem natural (PT-BR)          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Agente Principal                          │
│                    (LangChain + Azure AI Foundry)                │
│                                                                  │
│  ┌────────────────┐  ┌───────────────────┐  ┌────────────────┐ │
│  │  Sistema de    │  │   Loop de Raciocí- │  │  Histórico de  │ │
│  │  Prompt (SQL   │  │   nio ReAct        │  │  Conversa      │ │
│  │  + contexto)   │  │  (Thought→Act→Obs) │  │  (memória)     │ │
│  └────────────────┘  └───────────────────┘  └────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │ aciona tools
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Tool: execute_  │ │  Tool: get_      │ │  Tool: generate_ │
│  sql(query)      │ │  schema_info()   │ │  chart(df, type) │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Trino/Hive      │ │  Metadata Cache  │ │  Matplotlib /    │
│  (0.0.0.0:8080)  │ │  (schemas YAML)  │ │  Plotly          │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## Decisões Arquiteturais

### 1. Abordagem de Acesso a Dados: Text-to-SQL

**Alternativas avaliadas:**

| Abordagem       | Descrição                                               | Prós                              | Contras                                 |
|-----------------|---------------------------------------------------------|-----------------------------------|-----------------------------------------|
| **Text-to-SQL** | LLM gera SQL → executa no Trino → LLM interpreta resultado | Simples, preciso, sem overhead   | Necessita schema no contexto           |
| RAG sobre dados | Vetoriza registros do lake e recupera por similaridade  | Busca semântica rica              | Custo alto, impreciso para agregações  |
| MCP Server      | Expõe Trino como servidor de protocolo MCP              | Padronizado, reutilizável         | Complexidade operacional maior         |

**Decisão: Text-to-SQL para o MVP.**

O schema Gold é pequeno (8 tabelas, ~70 colunas no total) e cabe inteiramente no contexto do LLM. O agente recebe um system prompt com o DDL das tabelas Gold e usa raciocínio ReAct para gerar e executar SQL.

> **MCP Server** é uma evolução natural para Fase 2: permitiria expor o agente como recurso padronizado consumido por múltiplos clientes (Copilot Studio, VS Code, etc.).

---

### 2. RAG — Quando é Necessário?

Para o MVP com dados CNPJ estruturados, RAG **não é necessário**. Os cenários que motivariam RAG no futuro são:

- Glossário de negócio extenso (termos da área contábil → mapeamento para colunas)
- Documentação de regras de negócio grandes demais para o contexto
- Múltiplas fontes heterogêneas (PDFs, wikis, etc.)

**Decisão: RAG diferido para Fase 2.** O sistema de prompt inicial incluirá um mapeamento manual de termos de negócio → colunas/tabelas.

---

### 3. Framework do Agente: LangChain

**Alternativas avaliadas:**

| Framework          | Fit com Azure AI Foundry | SQL Agent | Maturidade |
|--------------------|--------------------------|-----------|------------|
| **LangChain**      | ✅ via `langchain-openai` | ✅ nativo  | Alta       |
| Semantic Kernel    | ✅ nativo Microsoft       | Parcial   | Média      |
| AutoGen            | ✅                        | Manual    | Média      |
| Azure AI SDK puro  | ✅ nativo                 | Manual    | —          |

**Decisão: LangChain + `langchain-openai` (Azure endpoint).**

LangChain oferece `create_sql_agent` e suporte nativo a tool calling, histórico de conversa e streaming de resposta. A integração com Azure AI Foundry é via:

```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint=...,
    azure_deployment=...,   # ex: gpt-4o
    api_version="2024-12-01-preview",
    api_key=...
)
```

---

### 4. Estratégia de Contexto de Schema

O agente terá acesso ao schema das tabelas de três formas:

1. **System prompt estático**: DDL simplificado das tabelas Gold injetado no início de cada sessão (baixo custo, sempre disponível)
2. **Tool `get_schema_info(table)`**: Permite ao agente consultar colunas de uma tabela específica em tempo real via `DESCRIBE` no Trino
3. **Metadados YAML** (`metadata/schemas.yml`): Arquivo versionável com descrições de negócio de cada coluna — base para o system prompt e para um eventual RAG de schema

---

### 5. Interface: Streamlit

**Decisão: Streamlit para o MVP.**

- Desenvolvimento rápido em Python puro
- Suporte nativo a `st.chat_message`, `st.dataframe`, `st.pyplot` / `st.plotly_chart`
- Não requer front-end separado
- Fácil de containerizar e expor

---

### 6. Geração de Gráficos

O agente terá uma tool `generate_chart(data, chart_type, title, x_col, y_col)` que:
1. Recebe o DataFrame resultante da consulta SQL
2. Recebe a configuração de gráfico decidida pelo LLM
3. Gera o gráfico com Plotly (interativo) ou Matplotlib (estático)
4. Retorna a figura para o Streamlit renderizar

Tipos suportados no MVP: `bar`, `line`, `pie`, `scatter`, `horizontal_bar`.

---

### 7. Segurança e Limites

- Todas as queries executadas pelo agente são **somente leitura** (SELECT). O usuário Trino do agente terá permissões restritas a SELECT.
- Queries com `DROP`, `INSERT`, `UPDATE`, `DELETE` serão rejeitadas com validação prévia.
- Timeout de query configurável (padrão: 30s) para evitar scans pesados.
- Histórico de conversas armazenado apenas em memória de sessão (sem persistência de PII no MVP).

---

## Diagrama de Sequência — Pergunta Simples

```
Usuário → UI: "Quantas empresas ativas existem em São Paulo?"
UI → Agente: mensagem + histórico
Agente → LLM: system_prompt + schema + mensagem
LLM → Agente: Thought: preciso contar dim_empresa com filtro UF='SP'
               Action: execute_sql("SELECT COUNT(*) FROM hive.gold.fact_estabelecimentos ...")
Agente → Trino: executa SQL
Trino → Agente: [(123456,)]
LLM → Agente: Observation: 123.456 empresas
               Final Answer: "Existem 123.456 empresas ativas em São Paulo..."
Agente → UI: resposta + dados
UI → Usuário: texto + (opcional) gráfico
```
