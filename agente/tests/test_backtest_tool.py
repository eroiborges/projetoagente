from app.domain.models import RecommendationRecord, TechnicalHistoryPoint
from app.tools.backtest_tool import (
    build_backtest_rows,
    run_backtest_from_files,
    summarize_backtest,
    summarize_backtest_by_ticker,
)


def _history_point(ticker: str, date: str, close: float) -> TechnicalHistoryPoint:
    return TechnicalHistoryPoint(
        ticker=ticker,
        date=date,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=1000.0,
        rsi=50.0,
        macd_value=0.0,
        macd_signal_value=0.0,
        macd_signal="neutro",
        sma_20=close,
        ema_20=close,
        bb_upper=close + 2,
        bb_lower=close - 2,
        bb_mid=close,
        volume_avg_20=900.0,
        data_mode="mock",
    )


def _record(ticker: str, recommendation: str, generated_at: str) -> RecommendationRecord:
    return RecommendationRecord(
        ticker=ticker,
        recommendation=recommendation,
        confidence=0.75,
        rationale="rationale",
        generated_at=generated_at,
        data_mode="mock",
        market_status="ok_mock",
        news_status="ok_mock",
        matched_news_count=1,
        news_sentiment_score=0.2,
        avg_impact_score=0.4,
        evidence={"total_score": 2},
    )


def test_build_backtest_rows_for_buy_and_sell() -> None:
    history = [
        _history_point("ITUB4", "2026-06-05", 10.0),
        _history_point("ITUB4", "2026-06-06", 11.0),
        _history_point("ITUB4", "2026-06-07", 9.0),
        _history_point("VALE3", "2026-06-05", 20.0),
        _history_point("VALE3", "2026-06-06", 19.0),
        _history_point("VALE3", "2026-06-07", 18.0),
    ]
    records = [
        _record("ITUB4", "COMPRAR", "2026-06-06T10:00:00Z"),
        _record("VALE3", "VENDER", "2026-06-06T10:00:00Z"),
    ]

    rows = build_backtest_rows(records, history)

    assert len(rows) == 2
    assert rows[0]["recommendation"] == "COMPRAR"
    assert rows[0]["outcome"] == "erro"
    assert "buy_hold_return" in rows[0]
    assert "alpha_vs_buy_hold" in rows[0]
    assert rows[1]["recommendation"] == "VENDER"
    assert rows[1]["outcome"] == "acerto"


def test_summarize_backtest_excludes_aguardar_from_hit_rate() -> None:
    rows = [
        {
            "recommendation": "COMPRAR",
            "strategy_return": 0.05,
            "buy_hold_return": 0.05,
            "alpha_vs_buy_hold": 0.0,
            "outcome": "acerto",
        },
        {
            "recommendation": "VENDER",
            "strategy_return": -0.02,
            "buy_hold_return": 0.02,
            "alpha_vs_buy_hold": -0.04,
            "outcome": "erro",
        },
        {
            "recommendation": "AGUARDAR",
            "strategy_return": 0.0,
            "buy_hold_return": 0.01,
            "alpha_vs_buy_hold": -0.01,
            "outcome": "neutro",
        },
    ]

    summary = summarize_backtest(rows)

    assert summary["total_signals"] == 3
    assert summary["evaluated_signals"] == 2
    assert summary["hits"] == 1
    assert summary["hit_rate"] == 0.5
    assert summary["avg_buy_hold_return"] == 0.0267
    assert summary["avg_alpha_vs_buy_hold"] == -0.0167


def test_build_backtest_rows_supports_date_window() -> None:
    history = [
        _history_point("ITUB4", "2026-06-05", 10.0),
        _history_point("ITUB4", "2026-06-06", 11.0),
        _history_point("ITUB4", "2026-06-07", 12.0),
        _history_point("ITUB4", "2026-06-08", 13.0),
    ]
    records = [
        _record("ITUB4", "COMPRAR", "2026-06-06T10:00:00Z"),
        _record("ITUB4", "COMPRAR", "2026-06-08T10:00:00Z"),
    ]

    rows = build_backtest_rows(records, history, start_date="2026-06-07", end_date="2026-06-08")

    assert len(rows) == 0


def test_build_backtest_rows_deduplicates_same_ticker_day() -> None:
    history = [
        _history_point("ITUB4", "2026-06-05", 10.0),
        _history_point("ITUB4", "2026-06-06", 11.0),
        _history_point("ITUB4", "2026-06-07", 10.0),
    ]
    records = [
        _record("ITUB4", "COMPRAR", "2026-06-06T10:00:00Z"),
        _record("ITUB4", "VENDER", "2026-06-06T18:00:00Z"),
    ]

    rows = build_backtest_rows(records, history)

    assert len(rows) == 1
    assert rows[0]["recommendation"] == "VENDER"


def test_summarize_backtest_by_ticker_groups_metrics() -> None:
    rows = [
        {
            "ticker": "ITUB4",
            "recommendation": "COMPRAR",
            "strategy_return": 0.05,
            "buy_hold_return": 0.05,
            "alpha_vs_buy_hold": 0.0,
            "outcome": "acerto",
        },
        {
            "ticker": "ITUB4",
            "recommendation": "AGUARDAR",
            "strategy_return": 0.0,
            "buy_hold_return": 0.01,
            "alpha_vs_buy_hold": -0.01,
            "outcome": "neutro",
        },
        {
            "ticker": "VALE3",
            "recommendation": "VENDER",
            "strategy_return": 0.02,
            "buy_hold_return": -0.02,
            "alpha_vs_buy_hold": 0.04,
            "outcome": "acerto",
        },
    ]

    summary = summarize_backtest_by_ticker(rows)

    assert summary["ITUB4"]["total_signals"] == 2
    assert summary["ITUB4"]["evaluated_signals"] == 1
    assert summary["ITUB4"]["hit_rate"] == 1.0
    assert summary["VALE3"]["hits"] == 1
    assert summary["VALE3"]["avg_buy_hold_return"] == -0.02


def test_run_backtest_from_files_validates_inverted_window(tmp_path) -> None:
    rec_path = tmp_path / "recommendation_records.json"
    hist_path = tmp_path / "technical_history.json"
    rec_path.write_text("[]", encoding="utf-8")
    hist_path.write_text("[]", encoding="utf-8")

    result = run_backtest_from_files(
        str(rec_path),
        str(hist_path),
        start_date="2026-06-08",
        end_date="2026-06-07",
    )

    assert result["rows"] == []
    assert result["summary"]["total_signals"] == 0
    assert "metrics_report" in result
    assert "Janela de backtest invalida" in result["errors"][0]


def test_run_backtest_from_files_validates_date_format(tmp_path) -> None:
    rec_path = tmp_path / "recommendation_records.json"
    hist_path = tmp_path / "technical_history.json"
    rec_path.write_text("[]", encoding="utf-8")
    hist_path.write_text("[]", encoding="utf-8")

    result = run_backtest_from_files(
        str(rec_path),
        str(hist_path),
        start_date="06-06-2026",
        end_date="2026-06-08",
    )

    assert result["rows"] == []
    assert result["summary"]["total_signals"] == 0
    assert "Data inicial invalida" in result["errors"][0]


def test_run_backtest_from_files_returns_error_for_invalid_json(tmp_path) -> None:
    rec_path = tmp_path / "recommendation_records.json"
    hist_path = tmp_path / "technical_history.json"
    rec_path.write_text("{invalid", encoding="utf-8")
    hist_path.write_text("[]", encoding="utf-8")

    result = run_backtest_from_files(str(rec_path), str(hist_path))

    assert result["rows"] == []
    assert result["summary"]["total_signals"] == 0
    assert "Arquivo de recomendacoes invalido" in result["errors"][0]
