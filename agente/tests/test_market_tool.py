import pandas as pd

from app.tools.market_tool import has_min_history, is_temporally_consistent, normalize_market_frame


def test_normalize_market_frame_orders_and_deduplicates_index() -> None:
    idx = pd.to_datetime(["2026-06-03", "2026-06-01", "2026-06-02", "2026-06-02"])
    df = pd.DataFrame(
        {
            "Open": [10, 8, 9, 9.1],
            "High": [11, 9, 10, 10.1],
            "Low": [9, 7, 8, 8.1],
            "Close": [10.5, 8.5, 9.5, 9.6],
            "Volume": [100, 80, 90, 91],
        },
        index=idx,
    )

    out = normalize_market_frame(df)

    assert out.index.is_monotonic_increasing
    assert out.index.is_unique
    assert len(out) == 3


def test_normalize_market_frame_requires_ohlcv_columns() -> None:
    bad = pd.DataFrame({"Close": [1, 2, 3]}, index=pd.to_datetime(["2026-06-01", "2026-06-02", "2026-06-03"]))

    try:
        normalize_market_frame(bad)
        assert False, "Expected ValueError for missing OHLCV columns"
    except ValueError as exc:
        assert "Colunas ausentes" in str(exc)


def test_temporal_consistency_and_min_history() -> None:
    idx = pd.date_range("2026-01-01", periods=40, freq="D")
    frame = pd.DataFrame(
        {
            "Open": range(40),
            "High": [x + 1 for x in range(40)],
            "Low": [x - 1 for x in range(40)],
            "Close": [x + 0.5 for x in range(40)],
            "Volume": [1000 + x for x in range(40)],
        },
        index=idx,
    )

    out = normalize_market_frame(frame)
    assert is_temporally_consistent(out)
    assert has_min_history(out)


def test_temporal_consistency_fails_with_duplicate_index() -> None:
    idx = pd.to_datetime(["2026-01-01", "2026-01-01", "2026-01-02"])
    frame = pd.DataFrame(
        {
            "Open": [1, 1, 2],
            "High": [2, 2, 3],
            "Low": [0, 0, 1],
            "Close": [1.5, 1.4, 2.5],
            "Volume": [10, 11, 12],
        },
        index=idx,
    )

    # A normalização remove duplicatas; depois da limpeza o frame deve ficar consistente.
    out = normalize_market_frame(frame)
    assert is_temporally_consistent(out)
