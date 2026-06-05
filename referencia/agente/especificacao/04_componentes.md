# 04 – Componentes do Sistema

## Estrutura de Pastas Proposta

```
agente/
├── especificacao/          # Documentação de arquitetura (este folder)
├── info/                   # Documentos de entrada do projeto
├── app/                    # Aplicação principal
│   ├── main.py             # Entry point Streamlit
│   ├── agent.py            # Inicialização e configuração do agente LangChain
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── sql_tool.py     # Tool: execute_sql
│   │   ├── schema_tool.py  # Tool: get_schema_info
│   │   └── chart_tool.py   # Tool: generate_chart
│   ├── prompts/
│   │   ├── system_prompt.py    # System prompt com schema e glossário
│   │   └── few_shots.py        # Exemplos de perguntas → SQL correto
│   ├── metadata/
│   │   └── schemas.yml         # Descrições de negócio das colunas
│   └── utils/
│       ├── trino_client.py     # Cliente HTTP para Trino
│       └── config.py           # Variáveis de ambiente / settings
├── tests/
│   ├── test_sql_tool.py
│   ├── test_agent.py
│   └── fixtures/
└── requirements.txt
```

---

## Componentes Detalhados

### 1. `trino_client.py` — Cliente Trino

Responsável por executar queries SQL no Trino via HTTP API (REST).

**Interface:**
```python
class TrinoClient:
    def __init__(self, host: str, user: str, catalog: str = "hive")
    def execute(self, sql: str, timeout: int = 30) -> tuple[list[dict], list[str]]
        # retorna (rows_as_dicts, column_names)
    def describe_table(self, schema: str, table: str) -> list[dict]
```

**Responsabilidades:**
- Submeter query via `POST /v1/statement`
- Fazer polling em `nextUri` até conclusão
- Rejeitar queries que não sejam `SELECT` (proteção contra escrita)
- Aplicar timeout configurável
- Retornar erro estruturado para o agente tratar

---

### 2. `sql_tool.py` — Tool: execute_sql

Tool LangChain que o agente usa para executar SQL no Trino.

```python
@tool
def execute_sql(query: str) -> str:
    """
    Executa uma query SQL SELECT no Trino/Hive e retorna o resultado
    como JSON string. Use hive.gold.* para consultas analíticas.
    Sempre use LIMIT quando não souber o tamanho do resultado.
    """
```

**Comportamento:**
- Valida que a query é um SELECT
- Executa via `TrinoClient`
- Serializa resultado como JSON com colunas e dados
- Se o resultado for > 1000 linhas, retorna apenas as primeiras 500 e avisa o LLM
- Armazena o último DataFrame em memória de sessão para a tool de gráficos

---

### 3. `schema_tool.py` — Tool: get_schema_info

Permite ao agente inspecionar o schema de uma tabela específica em tempo real.

```python
@tool
def get_schema_info(table_fullname: str) -> str:
    """
    Retorna as colunas e tipos de uma tabela no formato hive.schema.tabela.
    Exemplos válidos: hive.gold.dim_empresa, hive.silver.int_estabelecimento
    """
```

**Uso pelo agente**: Quando o system prompt não contém detalhes suficientes ou o usuário menciona uma coluna não familiar.

---

### 4. `chart_tool.py` — Tool: generate_chart

Gera visualizações a partir dos dados da última query executada.

```python
@tool
def generate_chart(
    chart_type: str,      # bar | line | pie | scatter | horizontal_bar
    x_column: str,        # coluna para eixo X
    y_column: str,        # coluna para eixo Y
    title: str,           # título do gráfico
    top_n: int = 20       # limita a N itens para legibilidade
) -> str:
    """
    Gera um gráfico com os dados da última query SQL executada.
    Requer que execute_sql tenha sido chamado antes.
    Retorna "chart_ready" quando bem-sucedido.
    """
```

**Implementação**: Usa Plotly Express. A figura gerada é armazenada na sessão Streamlit para renderização.

---

### 5. `system_prompt.py` — System Prompt

Constrói o system prompt inicial injetado em cada sessão. Contém:

1. **Papel do agente**: assistente de dados para análise de empresas brasileiras
2. **Instruções de comportamento**: responder em português, ser preciso, citar a fonte dos dados
3. **Schema Gold completo**: DDL simplificado das 8 tabelas Gold com descrições de negócio
4. **Glossário de negócio**: mapeamento de termos do usuário para colunas/valores técnicos
5. **Regras de SQL**: usar LIMIT, não usar funções de escrita, sempre qualificar tabelas com `hive.gold.*`
6. **Instruções de gráfico**: quando e como usar a tool generate_chart

---

### 6. `few_shots.py` — Exemplos (Few-shot Prompting)

Exemplos de pares pergunta → SQL correto para melhorar a precisão do LLM:

```python
FEW_SHOTS = [
    {
        "pergunta": "Quantas empresas ativas existem em Minas Gerais?",
        "sql": """
            SELECT COUNT(DISTINCT e.cnpj_basico) AS total
            FROM hive.gold.fact_estabelecimentos fe
            JOIN hive.gold.dim_empresa e ON fe.cnpj_basico = e.cnpj_basico
            WHERE fe.uf = 'MG'
              AND fe.status = 2
        """
    },
    {
        "pergunta": "Quais os 10 setores com mais empresas abertas?",
        "sql": """
            SELECT c.descricao_cnae, COUNT(*) AS total
            FROM hive.gold.fact_estabelecimentos fe
            JOIN hive.gold.dim_cnae c ON fe.cnae_principal = c.id_cnae
            WHERE fe.status = 2
            GROUP BY c.descricao_cnae
            ORDER BY total DESC
            LIMIT 10
        """
    },
    ...
]
```

---

### 7. `agent.py` — Inicialização do Agente

Monta o agente LangChain com todas as peças:

```python
def create_agent(session_id: str) -> AgentExecutor:
    llm = AzureChatOpenAI(...)
    tools = [execute_sql, get_schema_info, generate_chart]
    memory = ConversationBufferWindowMemory(k=10, ...)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=build_system_prompt()),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
```

---

### 8. `main.py` — Interface Streamlit

**Layout:**
- Sidebar: configurações (modelo, temperatura, limite de linhas)
- Área principal: histórico de chat (`st.chat_message`)
- Após resposta: renderiza `st.dataframe` se houver dados tabulares e `st.plotly_chart` se houver gráfico

**Estado da sessão (`st.session_state`):**
```python
{
    "agent": AgentExecutor,        # instância do agente
    "messages": list[dict],        # histórico formatado para exibição
    "last_df": pd.DataFrame,       # último resultado SQL (para reuso)
    "last_figure": plotly.Figure,  # último gráfico gerado
}
```

---

## Configuração e Variáveis de Ambiente

Arquivo `.env` (nunca comitar):

```env
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<chave>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview

TRINO_HOST=http://0.0.0.0:8080
TRINO_USER=agent_user
TRINO_CATALOG=hive
TRINO_QUERY_TIMEOUT=30
TRINO_MAX_ROWS=500
```
