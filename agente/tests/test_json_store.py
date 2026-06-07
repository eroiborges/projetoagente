import json
from pathlib import Path

from app.domain.models import NewsItem, Recommendation, RecommendationRecord, TechnicalHistoryPoint, TechnicalSnapshot
from app.storage.json_store import (
    append_news_items,
    append_recommendation_records,
    append_recommendations,
    append_technical_history,
    append_technical_snapshots,
)


def _snapshot(ticker: str, date: str, data_mode: str, close: float) -> TechnicalSnapshot:
    return TechnicalSnapshot(
        ticker=ticker,
        date=date,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=1000,
        rsi=50.0,
        macd_value=0.0,
        macd_signal_value=0.0,
        macd_signal="neutral",
        sma_20=close,
        ema_20=close,
        bb_upper=close + 2,
        bb_lower=close - 2,
        bb_mid=close,
        volume_avg_20=950,
        data_mode=data_mode,
    )


def test_append_technical_snapshots_deduplicates_by_ticker_date_mode(tmp_path: Path) -> None:
    path = tmp_path / "technical_snapshots.json"

    a1 = _snapshot("VALE3", "2026-06-05", "real", 61.0)
    a2 = _snapshot("VALE3", "2026-06-05", "real", 62.0)  # mesmo key, substitui
    b1 = _snapshot("VALE3", "2026-06-05", "mock", 60.0)  # key diferente por data_mode

    append_technical_snapshots(str(path), [a1])
    append_technical_snapshots(str(path), [a2, b1])

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert len(raw) == 2

    by_mode = {row["data_mode"]: row for row in raw}
    assert by_mode["real"]["close"] == 62.0
    assert by_mode["mock"]["close"] == 60.0


def _history(ticker: str, date: str, data_mode: str, close: float) -> TechnicalHistoryPoint:
    return TechnicalHistoryPoint(
        ticker=ticker,
        date=date,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=1000,
        rsi=50.0,
        macd_value=0.1,
        macd_signal_value=0.05,
        macd_signal="bullish",
        sma_20=close,
        ema_20=close,
        bb_upper=close + 2,
        bb_lower=close - 2,
        bb_mid=close,
        volume_avg_20=980,
        data_mode=data_mode,
    )


def test_append_technical_history_deduplicates_by_ticker_date_mode(tmp_path: Path) -> None:
    path = tmp_path / "technical_history.json"

    a1 = _history("VALE3", "2026-06-05", "real", 61.0)
    a2 = _history("VALE3", "2026-06-05", "real", 62.0)
    b1 = _history("VALE3", "2026-06-05", "mock", 60.0)

    append_technical_history(str(path), [a1])
    append_technical_history(str(path), [a2, b1])

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert len(raw) == 2

    by_mode = {row["data_mode"]: row for row in raw}
    assert by_mode["real"]["close"] == 62.0
    assert by_mode["mock"]["close"] == 60.0


def _news_item(ticker: str, data_mode: str, url: str, title: str, score: float) -> NewsItem:
    return NewsItem(
        ticker=ticker,
        source="infomoney",
        published_at="2026-06-06T10:00:00+00:00",
        title=title,
        url=url,
        summary="resumo",
        sentiment_label="positive",
        sentiment_score=1.0,
        impact_score=score,
        data_mode=data_mode,
    )


def test_append_news_items_deduplicates_by_url_and_mode(tmp_path: Path) -> None:
    path = tmp_path / "news_items.json"

    a1 = _news_item("ITUB4", "real", "https://example.com/n1", "titulo 1", 0.5)
    a2 = _news_item("ITUB4", "real", "https://example.com/n1", "titulo 1 atualizado", 0.9)
    b1 = _news_item("ITUB4", "mock", "https://example.com/n1", "titulo mock", 0.2)

    append_news_items(str(path), [a1])
    append_news_items(str(path), [a2, b1])

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert len(raw) == 2

    by_mode = {row["data_mode"]: row for row in raw}
    assert by_mode["real"]["impact_score"] == 0.9
    assert by_mode["mock"]["impact_score"] == 0.2


def test_append_recommendations_persists_evidence_contract(tmp_path: Path) -> None:
    path = tmp_path / "recommendations.json"
    recommendation = Recommendation(
        ticker="ITUB4",
        recommendation="COMPRAR",
        confidence=0.75,
        rationale="Tecnico: MACD em alta e RSI em 38.0, abaixo de 40. Noticias: consenso neutro. Decisao final: COMPRAR.",
        generated_at="2026-06-06T10:00:00Z",
        evidence={
            "technical_score": 2,
            "news_score": 0,
            "total_score": 2,
            "technical_factors": ["MACD em alta", "RSI em 38.0, abaixo de 40"],
            "news_factors": ["Consenso de noticias neutro"],
            "signal_breakers": ["MACD virar para baixa"],
        },
    )

    append_recommendations(str(path), [recommendation])

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert len(raw) == 1
    assert raw[0]["evidence"]["technical_score"] == 2
    assert raw[0]["evidence"]["signal_breakers"] == ["MACD virar para baixa"]


def test_append_recommendation_records_deduplicates_by_ticker_generated_at_mode(tmp_path: Path) -> None:
    path = tmp_path / "recommendation_records.json"
    a1 = RecommendationRecord(
        ticker="ITUB4",
        recommendation="COMPRAR",
        confidence=0.75,
        rationale="r1",
        generated_at="2026-06-06T10:00:00Z",
        data_mode="mock",
        market_status="ok_mock",
        news_status="ok_mock",
        matched_news_count=2,
        news_sentiment_score=0.3,
        avg_impact_score=0.4,
        evidence={"total_score": 2},
    )
    a2 = RecommendationRecord(
        ticker="ITUB4",
        recommendation="AGUARDAR",
        confidence=0.55,
        rationale="r2",
        generated_at="2026-06-06T10:00:00Z",
        data_mode="mock",
        market_status="ok_mock",
        news_status="ok_mock",
        matched_news_count=1,
        news_sentiment_score=0.0,
        avg_impact_score=0.2,
        evidence={"total_score": 0},
    )

    append_recommendation_records(str(path), [a1])
    append_recommendation_records(str(path), [a2])

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert len(raw) == 1
    assert raw[0]["recommendation"] == "AGUARDAR"
    assert raw[0]["evidence"]["total_score"] == 0
