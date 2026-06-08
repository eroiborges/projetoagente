# 03 - Modelo de Dados e Campos

## 1. Recommendation
Arquivo relacionado: data/recommendations.json

Campos principais:
- ticker: ativo (ex.: VALE3).
- recommendation: COMPRAR, VENDER ou AGUARDAR.
- confidence: confianca no intervalo [0,1].
- rationale: justificativa textual.
- generated_at: timestamp UTC ISO.
- evidence: objeto com rastreabilidade (tool_trace, react_trace, scores, llm_source etc).

## 2. RecommendationRecord
Arquivo relacionado: data/recommendation_records.json

Campos principais:
- ticker, recommendation, confidence, rationale, generated_at.
- data_mode: mock ou real.
- market_status, news_status.
- matched_news_count, news_sentiment_score, avg_impact_score.
- evidence.

## 3. DailyAnalysisRecord
Arquivo relacionado: data/daily_analysis.json

Campos:
- ticker, date, close, rsi, macd_signal, news_sentiment, recommendation, data_mode.

## 4. TechnicalSnapshot / TechnicalHistoryPoint
Arquivos relacionados:
- data/technical_snapshots.json
- data/technical_history.json

Campos tecnicos:
- OHLCV: open, high, low, close, volume.
- Indicadores: rsi, macd_value, macd_signal_value, macd_signal, sma_20, ema_20, bb_upper, bb_lower, bb_mid, volume_avg_20.
- ticker, date, data_mode.

## 5. NewsItem
Arquivo relacionado: data/news_items.json

Campos:
- ticker, source, published_at, title, url, summary.
- sentiment_label, sentiment_score, impact_score.
- data_mode.

## 6. TickerRunStatus
Arquivo relacionado: data/ticker_statuses.json

Campos:
- ticker.
- market_status, news_status, notes.
- matched_news_count.
- news_sentiment_score, avg_impact_score.
- news_summary.
