# 05 – Stack Tecnológica

## Resumo da Stack

| Camada              | Tecnologia                          | Versão / Notas                       |
|---------------------|-------------------------------------|--------------------------------------|
| LLM                 | Azure AI Foundry (GPT-4o)           | `2024-12-01-preview`                 |
| Framework Agente    | LangChain                           | `>=0.3`                              |
| Integração Azure    | `langchain-openai`                  | AzureChatOpenAI                      |
| Interface           | Streamlit                           | `>=1.32`                             |
| Visualização        | Plotly Express                      | `>=5.0`                              |
| Manipulação dados   | Pandas                              | `>=2.0`                              |
| Query Engine        | Trino                               | v438, HTTP REST API                  |
| Storage             | MinIO + Hive Metastore              | S3-compatible                        |
| Formato de dados    | Parquet (no MinIO)                  | via dbt transformações               |
| Linguagem           | Python                              | `>=3.11`                             |
| Config              | Pydantic Settings + python-dotenv   | —                                    |

---

## LLM — Azure AI Foundry

### Por que Azure AI Foundry?
- Controle de dados corporativos (sem envio de dados para servidores OpenAI públicos)
- Compliance com políticas da empresa
- Integração com Azure Active Directory para controle de acesso
- SLA empresarial e suporte

### Configuração LangChain
```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # ex: gpt-4o
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0,          # determinismo para geração de SQL
    max_tokens=4096,
    streaming=True          # habilita streaming para melhor UX
)
```

### Modelos suportados
| Modelo     | Uso recomendado                    | Tokens contexto |
|------------|------------------------------------|-----------------|
| GPT-4o     | Produção — melhor acurácia SQL      | 128k            |
| GPT-4o-mini| Dev/testes — custo menor           | 128k            |

---

## LangChain

### Módulos utilizados

```
langchain                     # Core
langchain-openai              # AzureChatOpenAI
langchain-community           # utilitários de memória, toolkits SQL (referência)
langchain-core                # BaseMessage, PromptTemplate, tools
```

### Padrão de Agente: OpenAI Tools Agent (Function Calling)

O agente usa **tool calling nativo** do GPT-4o (não ReAct clássico via texto). Vantagens:
- Mais confiável: LLM seleciona tools via JSON estruturado, não parsing de texto
- Menor taxa de erro ao chamar ferramentas
- Suporte a múltiplas tools simultâneas quando necessário

```python
from langchain.agents import create_openai_tools_agent, AgentExecutor

agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
```

### Memória de Conversa
```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    k=10,                           # mantém últimas 10 trocas
    memory_key="chat_history",
    return_messages=True
)
```

---

## Trino — Integração via HTTP REST API

### Por que HTTP REST e não JDBC/ODBC?

- Sem dependência de driver Java no container Python
- Mais leve e simples de configurar
- A API `/v1/statement` com polling é o protocolo nativo do Trino

### Fluxo de execução de query
```
POST /v1/statement  →  { id, nextUri, stats }
GET  nextUri        →  loop até state = FINISHED ou FAILED
                    →  acumula data[] em cada resposta
```

### Headers obrigatórios
```
X-Trino-User: <usuario>
X-Trino-Catalog: hive
X-Trino-Schema: gold   (opcional — default pode ser definido)
```

### Biblioteca alternativa
Para simplificar o cliente, pode-se usar `trino` (PyPI):
```python
import trino

conn = trino.dbapi.connect(
    host="0.0.0.0",
    port=8080,
    user="agent_user",
    catalog="hive",
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM gold.dim_empresa LIMIT 10")
rows = cursor.fetchall()
```

> **Decisão**: usar a biblioteca `trino` (PyPI) para simplificar o código do cliente, mantendo o cliente HTTP customizado como fallback.

---

## Streamlit

### Componentes utilizados
```python
st.chat_input()           # input do usuário
st.chat_message()         # balões de conversa (user/assistant)
st.dataframe()            # exibe resultados tabulares
st.plotly_chart()         # renderiza gráficos Plotly interativos
st.spinner()              # loading state enquanto agente processa
st.sidebar                # configurações e metadados da sessão
st.session_state          # estado persistente por sessão de browser
```

### Streaming de resposta
A resposta do LLM será transmitida em streaming via `AgentExecutor` com callback:
```python
from langchain.callbacks.streamlit import StreamlitCallbackHandler
st_callback = StreamlitCallbackHandler(st.container())
response = executor.invoke({"input": user_question}, callbacks=[st_callback])
```

---

## Plotly Express

Tipos de gráfico e quando usar:

| Tipo             | Função Plotly            | Quando usar                              |
|------------------|--------------------------|-------------------------------------------|
| `bar`            | `px.bar`                 | Comparar categorias (top N setores)       |
| `horizontal_bar` | `px.bar(orientation='h')`| Muitas categorias com nome longo         |
| `line`           | `px.line`                | Séries temporais (abertura por ano)       |
| `pie`            | `px.pie`                 | Distribuição proporcional (% por UF)      |
| `scatter`        | `px.scatter`             | Correlação entre duas métricas            |

---

## Dependências (requirements.txt)

```txt
# LLM e Agente
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-core>=0.3.0
openai>=1.50.0

# Interface
streamlit>=1.32.0

# Visualização
plotly>=5.20.0
pandas>=2.0.0

# Trino
trino>=0.328.0

# Configuração
python-dotenv>=1.0.0
pydantic-settings>=2.0.0

# Utilitários
requests>=2.31.0
```

---

## Diagrama de Dependências dos Componentes

```
main.py (Streamlit)
    └── agent.py
            ├── AzureChatOpenAI (langchain-openai)
            ├── ConversationBufferWindowMemory (langchain)
            ├── system_prompt.py
            ├── few_shots.py
            └── tools/
                    ├── sql_tool.py  ──► trino_client.py  ──► Trino REST API
                    ├── schema_tool.py ► trino_client.py
                    └── chart_tool.py ──► plotly  ──► st.session_state["last_figure"]
```
