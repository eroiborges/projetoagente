import json
from pathlib import Path

from app.domain.models import TechnicalHistoryPoint, TechnicalSnapshot
from app.storage.json_store import append_technical_history, append_technical_snapshots


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
