# 03 - Modelo de Dados

## Entidades principais

### price_snapshot

Dados de mercado por ticker e data.

Campos sugeridos:

- ticker
- date
- open
- high
- low
- close
- volume

### technical_indicators

Indicadores calculados por ticker e data.

Campos sugeridos:

- ticker
- date
- rsi
- macd
- macd_signal
- sma_20
- ema_20
- bb_upper
- bb_lower
- bb_mid
- volume_avg_20

### news_items

Notícias coletadas e classificadas.

Campos sugeridos:

- ticker
- source
- published_at
- title
- url
- summary
- sentiment_label
- sentiment_score
- impact_score

### daily_analysis

Consolidação diária dos sinais.

Campos sugeridos:

- ticker
- date
- technical_signal
- sentiment_signal
- confidence_score
- recommendation
- rationale

## Exemplo de saída final

{
  "ticker": "VALE3",
  "date": "2026-05-31",
  "close": 61.42,
  "rsi": 45.2,
  "macd_signal": "bullish",
  "news_sentiment": 0.72,
  "recommendation": "COMPRAR"
}
