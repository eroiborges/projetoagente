from app.domain.models import TechnicalHistoryPoint, TechnicalSnapshot
from app.pipelines.run_analysis import run_pipeline_with_details


def test_run_pipeline_with_details_mock_contract() -> None:
    tickers = ["VALE3", "PETR4", "BBAS3", "ITUB4"]
    result = run_pipeline_with_details(tickers=tickers, execution_mode="on_demand", data_mode="mock")

    assert len(result.recommendations) == 4
    assert len(result.recommendation_records) == 4
    assert len(result.technical_snapshots) == 4
    assert len(result.technical_history) == 4
    assert len(result.ticker_statuses) == 4

    assert all(r.recommendation in {"COMPRAR", "VENDER", "AGUARDAR"} for r in result.recommendations)
    assert all(0 <= r.confidence <= 1 for r in result.recommendations)
    assert all(isinstance(r.evidence, dict) for r in result.recommendations)
    assert all("technical_score" in r.evidence for r in result.recommendations)
    assert all("news_score" in r.evidence for r in result.recommendations)
    assert all("signal_breakers" in r.evidence for r in result.recommendations)
    assert all(s.market_status.startswith("ok_") for s in result.ticker_statuses)
    assert all(record.market_status.startswith("ok_") for record in result.recommendation_records)
    assert all("technical_factors" in record.evidence for record in result.recommendation_records)
    assert all(s.matched_news_count >= 0 for s in result.ticker_statuses)
    assert all(-1 <= s.news_sentiment_score <= 1 for s in result.ticker_statuses)
    assert all(0 <= s.avg_impact_score <= 1 for s in result.ticker_statuses)


def test_run_pipeline_marks_market_fallback_status(monkeypatch) -> None:
    fake_snapshot = TechnicalSnapshot(
        ticker="VALE3",
        date="2026-06-05",
        open=61.0,
        high=62.0,
        low=60.0,
        close=61.5,
        volume=1000,
        rsi=50.0,
        macd_value=0.0,
        macd_signal_value=0.0,
        macd_signal="neutral",
        sma_20=61.0,
        ema_20=61.0,
        bb_upper=63.0,
        bb_lower=59.0,
        bb_mid=61.0,
        volume_avg_20=900,
        data_mode="real_fallback",
    )

    fake_history = TechnicalHistoryPoint(
        ticker="VALE3",
        date="2026-06-05",
        open=61.0,
        high=62.0,
        low=60.0,
        close=61.5,
        volume=1000,
        rsi=50.0,
        macd_value=0.0,
        macd_signal_value=0.0,
        macd_signal="neutral",
        sma_20=61.0,
        ema_20=61.0,
        bb_upper=63.0,
        bb_lower=59.0,
        bb_mid=61.0,
        volume_avg_20=900,
        data_mode="real_fallback",
    )

    monkeypatch.setattr("app.pipelines.run_analysis.get_technical_snapshots_batch", lambda tickers, data_mode: [fake_snapshot])
    monkeypatch.setattr("app.pipelines.run_analysis.get_technical_history_batch", lambda tickers, data_mode: [fake_history])

    result = run_pipeline_with_details(tickers=["VALE3"], execution_mode="on_demand", data_mode="real")

    assert len(result.ticker_statuses) == 1
    assert len(result.recommendation_records) == 1
    assert result.ticker_statuses[0].market_status == "error_real_fallback"
    assert result.recommendation_records[0].market_status == "error_real_fallback"
    assert result.ticker_statuses[0].matched_news_count >= 0
    assert -1 <= result.ticker_statuses[0].news_sentiment_score <= 1
    assert 0 <= result.ticker_statuses[0].avg_impact_score <= 1


def test_run_pipeline_recommendation_rationale_is_descriptive() -> None:
    result = run_pipeline_with_details(tickers=["ITUB4"], execution_mode="on_demand", data_mode="mock")

    recommendation = result.recommendations[0]
    assert "Tecnico:" in recommendation.rationale
    assert "Noticias:" in recommendation.rationale
    assert "Decisao final:" in recommendation.rationale


def test_run_pipeline_builds_structured_recommendation_record() -> None:
    result = run_pipeline_with_details(tickers=["ITUB4"], execution_mode="on_demand", data_mode="mock")

    record = result.recommendation_records[0]
    assert record.ticker == "ITUB4"
    assert record.data_mode == "mock"
    assert record.market_status == "ok_mock"
    assert "total_score" in record.evidence
