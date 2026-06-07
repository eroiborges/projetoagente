# 09 - Execucao Final e Limitacoes

## Pre-requisitos

- Python e ambiente virtual disponiveis.
- Dependencias instaladas com `requirements.txt`.
- Acesso a internet para modo `real` (mercado/noticias).

## Como executar

1. Instalar dependencias:

```bash
cd /agent/agente
/agent/.venv/bin/python -m pip install -r requirements.txt
```

2. Iniciar a app:

```bash
cd /agent/agente
/agent/.venv/bin/streamlit run app/main.py
```

3. Na interface:

- Selecionar modo de execucao.
- Selecionar modo de dados (`mock` ou `real`).
- Selecionar escopo (todos ou ticker unico).
- Clicar em `Executar pipeline`.

## Artefatos de saida

A app persiste resultados em `data/`:

- `recommendations.json`
- `recommendation_records.json`
- `technical_snapshots.json`
- `technical_history.json`
- `news_items.json`
- `ticker_statuses.json`

## Verificacao rapida

- Painel principal exibe recomendacoes por ticker.
- Expander de status mostra condicao operacional por ticker.
- Expander de backtest exibe metricas ou mensagem diagnostica.
- Chat responde perguntas sobre o resultado da ultima execucao.

## Testes

Execucao recomendada:

```bash
cd /agent/agente
/agent/.venv/bin/pytest -q
```

## Limitacoes conhecidas

1. Backtest minimo depende de dados com D+1; sem esse ponto nao ha linhas avaliaveis.
2. Fontes RSS podem ter variacao de disponibilidade e cobertura por ticker.
3. Recomendacao e suporte educacional; nao representa execucao automatica de ordem.
4. Janela de backtest muito restrita pode eliminar sinais validos.
5. Em modo real, latencia/instabilidade de rede pode acionar fallback por ticker.

## Comportamento de fallback

- Falhas de mercado/noticias nao interrompem lote completo.
- Status por ticker indica erro ou aviso para facilitar diagnostico.
- Backtest retorna erros amigaveis para janela invalida ou JSON invalido.
