import re

from app.domain.models import RunResult


def _normalize_ticker(ticker: str) -> str:
    return (ticker or "").strip().upper()


def list_tickers(run_result: RunResult) -> list[str]:
    return sorted({r.ticker for r in run_result.recommendations})


def detect_ticker(question: str, run_result: RunResult) -> str | None:
    if not question:
        return None

    available = set(list_tickers(run_result))
    for token in re.findall(r"\b[A-Z]{4}\d\b", question.upper()):
        if token in available:
            return token
    return None


def detect_tickers(question: str, run_result: RunResult) -> list[str]:
    if not question:
        return []

    available = set(list_tickers(run_result))
    matches: list[str] = []
    for token in re.findall(r"\b[A-Z]{4}\d\b", question.upper()):
        if token in available and token not in matches:
            matches.append(token)
    return matches


def get_recommendation_context(run_result: RunResult, ticker: str) -> dict | None:
    ticker = _normalize_ticker(ticker)
    rec = next((r for r in run_result.recommendations if r.ticker == ticker), None)
    if rec is None:
        return None

    return {
        "ticker": rec.ticker,
        "recomendacao": rec.recommendation,
        "confianca": rec.confidence,
        "justificativa": rec.rationale,
        "gerado_em": rec.generated_at,
        "evidencias": rec.evidence,
    }


def get_technical_context(run_result: RunResult, ticker: str) -> dict | None:
    ticker = _normalize_ticker(ticker)
    snap = next((s for s in run_result.technical_snapshots if s.ticker == ticker), None)
    if snap is None:
        return None

    return {
        "ticker": snap.ticker,
        "data": snap.date,
        "close": snap.close,
        "rsi": snap.rsi,
        "macd_signal": snap.macd_signal,
        "sma_20": snap.sma_20,
        "ema_20": snap.ema_20,
    }


def get_news_context(run_result: RunResult, ticker: str, top_n: int = 3) -> dict:
    ticker = _normalize_ticker(ticker)
    items = [n for n in run_result.news_items if n.ticker == ticker]
    items.sort(key=lambda x: x.impact_score, reverse=True)

    labels = {"positive": "positivo", "negative": "negativo", "neutral": "neutro"}
    top_items = [
        {
            "titulo": n.title,
            "fonte": n.source,
            "sentimento": labels.get(n.sentiment_label, n.sentiment_label),
            "impacto": n.impact_score,
            "url": n.url,
        }
        for n in items[: max(1, top_n)]
    ]

    return {
        "ticker": ticker,
        "total_noticias": len(items),
        "top_noticias": top_items,
    }


def get_status_context(run_result: RunResult, ticker: str) -> dict | None:
    ticker = _normalize_ticker(ticker)
    status = next((s for s in run_result.ticker_statuses if s.ticker == ticker), None)
    if status is None:
        return None

    return {
        "ticker": status.ticker,
        "market_status": status.market_status,
        "news_status": status.news_status,
        "notes": status.notes,
        "matched_news_count": status.matched_news_count,
        "news_sentiment_score": status.news_sentiment_score,
        "avg_impact_score": status.avg_impact_score,
        "news_summary": status.news_summary,
    }
