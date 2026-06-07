from app.domain.models import MarketSignal, NewsSignal, Recommendation, utc_now_iso


def _normalize_macd_signal(value: str) -> str:
    raw = (value or "").strip().lower()
    mapping = {
        "bullish": "alta",
        "alta": "alta",
        "bearish": "baixa",
        "baixa": "baixa",
        "neutral": "neutro",
        "neutro": "neutro",
    }
    return mapping.get(raw, "neutro")


def _score_market(signal: MarketSignal) -> int:
    score = 0
    macd_signal = _normalize_macd_signal(signal.macd_signal)

    if macd_signal == "alta":
        score += 1
    if macd_signal == "baixa":
        score -= 1

    if signal.rsi < 40:
        score += 1
    elif signal.rsi > 60:
        score -= 1

    return score


def _market_factors(signal: MarketSignal) -> list[str]:
    factors: list[str] = []
    macd_signal = _normalize_macd_signal(signal.macd_signal)

    if macd_signal == "alta":
        factors.append("MACD em alta")
    elif macd_signal == "baixa":
        factors.append("MACD em baixa")
    else:
        factors.append("MACD neutro")

    if signal.rsi < 40:
        factors.append(f"RSI em {signal.rsi:.1f}, abaixo de 40")
    elif signal.rsi > 60:
        factors.append(f"RSI em {signal.rsi:.1f}, acima de 60")
    else:
        factors.append(f"RSI em {signal.rsi:.1f}, faixa intermediaria")

    return factors


def _score_news(signal: NewsSignal) -> int:
    consensus = _normalize_consensus(signal.consensus)
    if consensus == "positivo":
        return 1
    if consensus == "negativo":
        return -1
    return 0


def _news_factors(signal: NewsSignal) -> list[str]:
    consensus = _normalize_consensus(signal.consensus)
    return [
        f"Consenso de noticias {consensus}",
        f"Distribuicao de noticias: pos={signal.positive}, neg={signal.negative}, neu={signal.neutral}",
    ]


def _normalize_consensus(value: str) -> str:
    raw = (value or "").strip().lower()
    mapping = {
        "positive": "positivo",
        "positivo": "positivo",
        "negative": "negativo",
        "negativo": "negativo",
        "neutral": "neutro",
        "neutro": "neutro",
    }
    return mapping.get(raw, "neutro")


def recommend(market: MarketSignal, news: NewsSignal) -> Recommendation:
    market_score = _score_market(market)
    news_score = _score_news(news)
    total = market_score + news_score

    if total >= 2:
        action = "COMPRAR"
    elif total <= -2:
        action = "VENDER"
    else:
        action = "AGUARDAR"

    confidence = min(0.95, 0.55 + abs(total) * 0.1)
    consensus_pt = _normalize_consensus(news.consensus)
    technical_factors = _market_factors(market)
    news_factors = _news_factors(news)
    signal_breakers = _signal_breakers(action)

    rationale = (
        f"Tecnico: {technical_factors[0]} e {technical_factors[1]}. "
        f"Noticias: consenso {consensus_pt} (pos={news.positive}, neg={news.negative}, neu={news.neutral}). "
        f"Decisao final: {action}, com score tecnico {market_score}, score de noticias {news_score} e score total {total}."
    )

    evidence = {
        "technical_score": market_score,
        "news_score": news_score,
        "total_score": total,
        "technical_factors": technical_factors,
        "news_factors": news_factors,
        "signal_breakers": signal_breakers,
    }

    return Recommendation(
        ticker=market.ticker,
        recommendation=action,
        confidence=round(confidence, 2),
        rationale=rationale,
        generated_at=utc_now_iso(),
        evidence=evidence,
    )


def _signal_breakers(action: str) -> list[str]:
    if action == "COMPRAR":
        return [
            "MACD virar para baixa",
            "RSI subir acima de 60",
            "consenso de noticias migrar para negativo",
        ]
    if action == "VENDER":
        return [
            "MACD virar para alta",
            "RSI cair abaixo de 40",
            "consenso de noticias migrar para positivo",
        ]
    return [
        "tecnico ganhar direcao clara de alta",
        "tecnico ganhar direcao clara de baixa",
        "noticias deixarem de ficar neutras",
    ]
