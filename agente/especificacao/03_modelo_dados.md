# 03 - Modelo de Dados

## Contratos principais implementados

### Recommendation

- `ticker`
- `recommendation` (`COMPRAR`, `VENDER`, `AGUARDAR`)
- `confidence` (0 a 1)
- `rationale`
- `generated_at`
- `evidence` (scores, fatores e gatilhos)

### RecommendationRecord

- Campos da recomendacao final
- `data_mode`
- `market_status`
- `news_status`
- `matched_news_count`
- `news_sentiment_score`
- `avg_impact_score`
- `evidence`

### TechnicalSnapshot e TechnicalHistoryPoint

- `ticker`, `date`
- OHLCV (`open`, `high`, `low`, `close`, `volume`)
- Indicadores (`rsi`, `macd_value`, `macd_signal_value`, `macd_signal`, `sma_20`, `ema_20`, `bb_upper`, `bb_lower`, `bb_mid`, `volume_avg_20`)
- `data_mode`

### NewsItem

- `ticker`, `source`, `published_at`
- `title`, `url`, `summary`
- `sentiment_label`, `sentiment_score`, `impact_score`
- `data_mode`

### TickerRunStatus

- `ticker`
- `market_status`, `news_status`
- `notes`
- `matched_news_count`
- `news_sentiment_score`
- `avg_impact_score`

### RunResult

Agregado da execucao com:

- `recommendations`
- `recommendation_records`
- `technical_snapshots`
- `technical_history`
- `news_items`
- `ticker_statuses`

## Persistencia em JSON

Arquivos finais em `data/`:

- `recommendations.json`
- `recommendation_records.json`
- `technical_snapshots.json`
- `technical_history.json`
- `news_items.json`
- `ticker_statuses.json`
