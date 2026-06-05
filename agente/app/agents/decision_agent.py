from app.domain.models import MarketSignal, NewsSignal, Recommendation, utc_now_iso


def _score_market(signal: MarketSignal) -> int:
    score = 0
    if signal.macd_signal == "bullish":
        score += 1
    if signal.macd_signal == "bearish":
        score -= 1

    if signal.rsi < 40:
        score += 1
    elif signal.rsi > 60:
        score -= 1

    return score


def _score_news(signal: NewsSignal) -> int:
    if signal.consensus == "positive":
        return 1
    if signal.consensus == "negative":
        return -1
    return 0


def recommend(market: MarketSignal, news: NewsSignal) -> Recommendation:
    total = _score_market(market) + _score_news(news)

    if total >= 2:
        action = "COMPRAR"
    elif total <= -2:
        action = "VENDER"
    else:
        action = "AGUARDAR"

    confidence = min(0.95, 0.55 + abs(total) * 0.1)
    rationale = (
        f"MACD={market.macd_signal}, RSI={market.rsi:.1f}, "
        f"sentimento={news.consensus} (pos={news.positive}, neg={news.negative}, neu={news.neutral})."
    )

    return Recommendation(
        ticker=market.ticker,
        recommendation=action,
        confidence=round(confidence, 2),
        rationale=rationale,
        generated_at=utc_now_iso(),
    )
