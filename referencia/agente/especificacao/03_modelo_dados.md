# 03 – Modelo de Dados Disponível

## Catálogo Trino

- **Host**: `0.0.0.0:8080` (interno) / `192.168.200.2:8080`
- **Versão Trino**: 438
- **Catálogo**: `hive`
- **Engine de storage**: MinIO (object storage) + Hive Metastore

---

## Camada Gold — Tabelas Analíticas (uso primário do agente)

### `hive.gold.dim_empresa`

Dimensão principal de empresas brasileiras (CNPJ).

| Coluna                       | Tipo             | Descrição                                     |
|------------------------------|------------------|-----------------------------------------------|
| `cnpj_basico`                | varchar          | CNPJ raiz (8 dígitos) — chave da empresa      |
| `razao_social`               | varchar          | Nome oficial da empresa                       |
| `natureza_juridica`          | integer          | Código da natureza jurídica                   |
| `porte_empresa`              | integer          | 1=ME, 2=EPP, 3=Demais, 5=EI                   |
| `capital_social`             | decimal(15,2)    | Capital social declarado                      |
| `ente_federativo_responsavel`| varchar          | Órgão responsável (para órgãos públicos)      |
| `data_inicio_atividade`      | date             | Data de abertura da empresa                   |
| `situacao_cadastral`         | integer          | 1=Nula, 2=Ativa, 3=Suspensa, 4=Inapta, 8=Baixa|
| `motivo_situacao`            | varchar          | Descrição do motivo da situação               |
| `data_situacao_cadastral`    | date             | Data da última alteração de situação          |
| `data_carga`                 | date             | Data de carga no lake                         |

---

### `hive.gold.dim_estabelecimento`

Dimensão de estabelecimentos físicos (CNPJ completo = matriz + filiais).

| Coluna                    | Tipo     | Descrição                                           |
|---------------------------|----------|-----------------------------------------------------|
| `cnpj_completo`           | varchar  | CNPJ completo 14 dígitos — chave do estabelecimento |
| `cnpj_basico`             | varchar  | CNPJ raiz — FK para dim_empresa                     |
| `tipo_estabelecimento`    | integer  | 1=Matriz, 2=Filial                                  |
| `nome_fantasia`           | varchar  | Nome fantasia                                       |
| `situacao_estabelecimento`| integer  | Situação cadastral do estabelecimento               |
| `data_situacao`           | date     | Data da situação                                    |
| `cnae_principal`          | integer  | Código CNAE principal — FK para dim_cnae            |
| `descricao_cnae_principal`| varchar  | Descrição da atividade principal                    |
| `tipo_logradouro`         | varchar  | Tipo (Rua, Avenida, etc.)                           |
| `logradouro`              | varchar  | Nome do logradouro                                  |
| `numero`                  | varchar  | Número                                              |
| `bairro`                  | varchar  | Bairro                                              |
| `municipio`               | varchar  | Nome do município                                   |
| `uf`                      | varchar  | Sigla do estado (2 letras)                          |
| `pais`                    | varchar  | País                                                |
| `data_inicio_atividade`   | date     | Data de início das atividades                       |
| `data_carga`              | date     | Data de carga no lake                               |

---

### `hive.gold.dim_cnae`

Dimensão de classificação de atividades econômicas.

| Coluna          | Tipo    | Descrição                              |
|-----------------|---------|----------------------------------------|
| `id_cnae`       | integer | Código CNAE (7 dígitos)                |
| `descricao_cnae`| varchar | Descrição da atividade                 |
| `secao`         | varchar | Seção (ex: A, B, C…)                   |
| `divisao`       | varchar | Divisão (ex: 01, 10, 47…)              |
| `grupo`         | varchar | Grupo                                  |
| `classe`        | varchar | Classe                                 |
| `data_carga`    | date    | Data de carga                          |

---

### `hive.gold.dim_localidade`

Dimensão de municípios e países.

| Coluna             | Tipo       | Descrição              |
|--------------------|------------|------------------------|
| `codigo_municipio` | integer    | Código IBGE do município|
| `municipio`        | varchar    | Nome do município      |
| `pais`             | varchar(6) | Código do país         |

---

### `hive.gold.dim_socio`

Dimensão de sócios das empresas.

| Coluna                    | Tipo    | Descrição                                        |
|---------------------------|---------|--------------------------------------------------|
| `id_socio`                | bigint  | Identificador único do sócio (surrogate key)     |
| `cnpj_basico`             | varchar | CNPJ raiz — FK para dim_empresa                  |
| `nome_socio`              | varchar | Nome do sócio ou empresa sócia                   |
| `tipo_socio`              | varchar | T=Pessoa física, E=Empresa, F=Estrangeiro        |
| `qualificacao`            | varchar | Qualificação do sócio (sócio, diretor, etc.)     |
| `pais_origem`             | varchar | País de origem (sócios estrangeiros)             |
| `data_entrada_sociedade`  | date    | Data de entrada como sócio                       |
| `faixa_etaria`            | varchar | Faixa etária (0-28, 29-35, 36-45, 46-55, >65)   |
| `data_carga`              | date    | Data de carga no lake                            |

---

### `hive.gold.fact_empresas`

Fato com métricas agregadas por empresa.

| Coluna                       | Tipo    | Descrição                                  |
|------------------------------|---------|--------------------------------------------|
| `cnpj_basico`                | varchar | CNPJ raiz — FK para dim_empresa            |
| `situacao_cadastral`         | integer | Situação cadastral                         |
| `data_inicio_atividade`      | date    | Data de abertura                           |
| `quantidade_estabelecimentos`| bigint  | Total de estabelecimentos da empresa       |
| `quantidade_socios`          | bigint  | Total de sócios da empresa                 |
| `ano`                        | bigint  | Ano de referência                          |
| `mes`                        | bigint  | Mês de referência                          |

---

### `hive.gold.fact_estabelecimentos`

Fato com atributos analíticos de estabelecimentos.

| Coluna          | Tipo    | Descrição                                        |
|-----------------|---------|--------------------------------------------------|
| `cnpj_completo` | varchar | CNPJ 14 dígitos — chave                          |
| `cnpj_basico`   | varchar | CNPJ raiz — FK para dim_empresa                  |
| `uf`            | varchar | Estado                                           |
| `municipio`     | integer | Código IBGE — FK para dim_localidade             |
| `cnae_principal`| integer | Código CNAE — FK para dim_cnae                   |
| `status`        | integer | Situação do estabelecimento                      |
| `ano_inicio`    | bigint  | Ano de início das atividades                     |
| `mes_inicio`    | bigint  | Mês de início das atividades                     |

---

### `hive.gold.fact_socios`

Fato com atributos analíticos de sócios.

| Coluna        | Tipo    | Descrição                          |
|---------------|---------|------------------------------------|
| `id_socio`    | bigint  | FK para dim_socio                  |
| `cnpj_basico` | varchar | FK para dim_empresa                |
| `tipo_socio`  | varchar | Tipo de sócio                      |
| `qualificacao`| varchar | Qualificação                       |
| `ano_entrada` | bigint  | Ano de entrada na sociedade        |
| `mes_entrada` | bigint  | Mês de entrada na sociedade        |

---

## Relacionamentos entre Tabelas Gold

```
dim_empresa (cnpj_basico) ──────────────── fact_empresas (cnpj_basico)
       │                                          │
       │                           fact_estabelecimentos (cnpj_basico)
       │                                          │
dim_estabelecimento (cnpj_basico) ────────────────┘
       │
       ├── dim_cnae (id_cnae ↔ cnae_principal)
       └── dim_localidade (codigo_municipio ↔ municipio)

dim_socio (cnpj_basico) ─────────────────── fact_socios (cnpj_basico)
```

---

## Camadas Silver e Bronze

O agente priorizará a camada **Gold**. Silver e Bronze só serão usadas quando:
- O usuário explicitamente solicitar dados mais detalhados (ex: colunas presentes apenas no Silver como `email`, `telefone`, `cep`)
- Necessidade de debug ou validação de dados

### Silver — tabelas disponíveis
- `hive.silver.int_empresa` — inclui `natureza_juridica_descricao`, `motivo`, `qualificacao_responsavel`
- `hive.silver.int_estabelecimento` — inclui contato (email, telefones), complemento, CEP, CNAE secundário
- `hive.silver.int_cnae`
- `hive.silver.int_localidade`
- `hive.silver.int_socio`

---

## Glossário de Termos de Negócio

| Termo usado pelo usuário       | Mapeamento técnico                                        |
|--------------------------------|-----------------------------------------------------------|
| "empresa ativa"                | `situacao_cadastral = 2`                                  |
| "empresa baixada"              | `situacao_cadastral = 8`                                  |
| "microempresa" / "ME"          | `porte_empresa = 1`                                       |
| "EPP"                          | `porte_empresa = 3`                                       |
| "CNAE" / "setor" / "atividade" | `cnae_principal` + `dim_cnae.descricao_cnae`              |
| "estado" / "UF"                | coluna `uf` em `dim_estabelecimento` / `fact_estabelecimentos` |
| "matriz"                       | `tipo_estabelecimento = 1`                                |
| "filial"                       | `tipo_estabelecimento = 2`                                |
| "sócio pessoa física"          | `tipo_socio = 'T'`                                        |
| "sócio estrangeiro"            | `tipo_socio = 'F'`                                        |
| "capital social"               | `dim_empresa.capital_social`                              |
