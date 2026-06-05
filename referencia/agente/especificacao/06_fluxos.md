# 06 – Fluxos de Interação

## Fluxo 1 — Pergunta simples com resposta textual

**Exemplo**: "Quantas empresas estão ativas no Brasil?"

```
Usuário
  │
  │  "Quantas empresas estão ativas no Brasil?"
  ▼
Streamlit (main.py)
  │  Adiciona mensagem ao histórico
  │  Chama executor.stream(input, callbacks)
  ▼
AgentExecutor (LangChain)
  │  Monta prompt: system_prompt + histórico + pergunta
  ▼
Azure AI Foundry (GPT-4o)
  │  Thought: preciso contar empresas com situacao_cadastral=2
  │  Action: execute_sql
  │  Args: {"query": "SELECT COUNT(*) AS total FROM hive.gold.dim_empresa WHERE situacao_cadastral = 2"}
  ▼
sql_tool.execute_sql()
  │  Valida: é SELECT ✓
  │  Chama TrinoClient.execute(sql)
  ▼
Trino REST API
  │  Executa query
  │  Retorna: [{"total": 21453892}]
  ▼
AgentExecutor
  │  Observation: {"columns": ["total"], "data": [[21453892]]}
  ▼
Azure AI Foundry (GPT-4o)
  │  Final Answer: "Existem atualmente 21.453.892 empresas ativas
  │   registradas no Brasil, segundo a base de dados do CNPJ."
  ▼
Streamlit
  └── Exibe resposta no chat
```

---

## Fluxo 2 — Pergunta com geração de gráfico

**Exemplo**: "Me mostre o top 10 estados com mais empresas ativas em formato de gráfico"

```
Usuário
  │  "Me mostre o top 10 estados com mais empresas ativas em gráfico"
  ▼
AgentExecutor
  ▼
GPT-4o
  │  Thought: preciso buscar contagem por UF e depois gerar gráfico
  │
  │  [Action 1] execute_sql
  │  Args: {"query": "SELECT uf, COUNT(*) AS total
  │                   FROM hive.gold.fact_estabelecimentos
  │                   WHERE status = 2
  │                   GROUP BY uf ORDER BY total DESC LIMIT 10"}
  ▼
Trino → resultado 10 linhas (uf, total)
  ▼
GPT-4o
  │  Observation: dados recebidos ✓
  │
  │  [Action 2] generate_chart
  │  Args: {
  │    "chart_type": "horizontal_bar",
  │    "x_column": "total",
  │    "y_column": "uf",
  │    "title": "Top 10 Estados com mais empresas ativas"
  │  }
  ▼
chart_tool.generate_chart()
  │  Recupera last_df da sessão
  │  Gera px.bar(orientation='h', ...)
  │  Armazena figura em st.session_state["last_figure"]
  │  Retorna "chart_ready"
  ▼
GPT-4o
  │  Final Answer: "O gráfico abaixo mostra os 10 estados com mais
  │   empresas ativas. São Paulo lidera com N empresas, seguido por..."
  ▼
Streamlit
  ├── Exibe resposta textual no chat
  └── Detecta last_figure → renderiza st.plotly_chart(fig, use_container_width=True)
```

---

## Fluxo 3 — Pergunta de acompanhamento (memória de conversa)

**Exemplo**: usuário filtra sobre o resultado anterior

```
[Turno anterior]
Usuário: "Quais os 5 setores principais em SP?"
Agente:  (resposta com tabela de 5 setores)

[Turno atual]
Usuário: "E no Rio de Janeiro, como fica essa distribuição?"
  │
  ▼
AgentExecutor
  │  Recupera histórico de conversação (últimas 10 trocas)
  │  GPT-4o entende que "essa distribuição" = top 5 setores por CNAE
  │  Adapta a query para uf = 'RJ'
  ▼
[Mesma lógica do Fluxo 1/2...]
```

**Critério de qualidade**: o agente deve ser capaz de entender referências anafóricas ("esse setor", "aquelas empresas") dentro de uma mesma sessão.

---

## Fluxo 4 — Tratamento de erros de SQL

**Exemplo**: LLM gera SQL com coluna inexistente

```
GPT-4o
  │  Action: execute_sql
  │  Args: {"query": "SELECT cnpj, nome FROM hive.gold.dim_empresa LIMIT 5"}
  │          (coluna "nome" não existe — o correto é "razao_social")
  ▼
TrinoClient
  │  Trino retorna erro: "Column 'nome' cannot be resolved"
  ▼
sql_tool
  │  Retorna: {"error": "Column 'nome' cannot be resolved", "sql": "..."}
  ▼
GPT-4o
  │  Observation: erro de coluna
  │  Thought: vou verificar o schema da tabela
  │
  │  [Action] get_schema_info
  │  Args: {"table_fullname": "hive.gold.dim_empresa"}
  ▼
schema_tool
  │  Executa DESCRIBE hive.gold.dim_empresa
  │  Retorna lista de colunas
  ▼
GPT-4o
  │  Identifica coluna correta: "razao_social"
  │  Corrige e reexecuta SQL
  ▼
[Resultado correto entregue ao usuário]
```

---

## Fluxo 5 — Pergunta fora do escopo dos dados

**Exemplo**: "Qual é o melhor investimento para minha empresa?"

```
GPT-4o
  │  Analisa: pergunta não relacionada a dados do CNPJ
  │  Não chama nenhuma tool
  │  Final Answer: "Não tenho dados suficientes para responder sobre
  │   investimentos. Posso ajudar com análises da base de empresas
  │   brasileiras, como dados cadastrais, distribuição por setor,
  │   localização geográfica ou evolução temporal de abertura de CNPJs."
```

---

## Fluxo 6 — Query com resultado grande

**Exemplo**: "Me dê todos os CNPJs de empresas de tecnologia"

```
GPT-4o
  │  Action: execute_sql
  │  Args: {"query": "SELECT cnpj_basico FROM hive.gold.dim_empresa ..."}
  ▼
sql_tool
  │  Executa query
  │  Detecta resultado > 500 linhas
  │  Trunca para 500 e adiciona aviso no retorno
  │  Retorna: {"warning": "Resultado truncado para 500 linhas (total: 84.231)",
  │             "columns": [...], "data": [...500 linhas...]}
  ▼
GPT-4o
  │  Final Answer: "A consulta retornou 84.231 empresas de tecnologia.
  │   Mostro aqui as primeiras 500. Se precisar exportar todos os dados,
  │   posso refinar a consulta com filtros adicionais.
  │   Gostaria de ver uma distribuição por estado ou segmento?"
```

---

## Diagrama de Estados do Agente por Turno

```
[Recebe mensagem]
       │
       ▼
[Compõe prompt com histórico]
       │
       ▼
[LLM decide próxima ação]
       │
       ├─ Tool Call ──► [Executa tool] ──► [Observation] ──► [volta para LLM]
       │                     │
       │                     └─ Erro ──► [Observation com erro] ──► [LLM tenta corrigir]
       │
       └─ Final Answer ──► [Resposta para o usuário] ──► [Streamlit renderiza]
                                    │
                                    └─ last_figure? ──► st.plotly_chart()
                                    └─ last_df?     ──► st.dataframe()
```
