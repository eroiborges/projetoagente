import pandas as pd
import pandas_ta_classic as ta
import yfinance as yf
from datetime import datetime, timezone
from typing import Iterable

from app.config.settings import settings
from app.domain.models import MarketSignal, TechnicalHistoryPoint, TechnicalSnapshot


MIN_BARS_FOR_TECHNICALS = 35


MOCK_MARKET = {
    "VALE3": {
        "open": 60.8,
        "high": 61.9,
        "low": 60.2,
        "close": 61.4,
        "volume": 18000000,
        "rsi": 48.2,
        "macd_value": 0.18,
        "macd_signal_value": 0.11,
        "macd_signal": "alta",
        "sma_20": 60.9,
        "ema_20": 61.1,
        "bb_upper": 63.0,
        "bb_lower": 58.8,
        "bb_mid": 60.9,
        "volume_avg_20": 17600000,
    },
    "PETR4": {
        "open": 35.7,
        "high": 36.4,
        "low": 35.5,
        "close": 36.1,
        "volume": 22000000,
        "rsi": 56.4,
        "macd_value": 0.22,
        "macd_signal_value": 0.19,
        "macd_signal": "alta",
        "sma_20": 35.5,
        "ema_20": 35.8,
        "bb_upper": 37.1,
        "bb_lower": 34.0,
        "bb_mid": 35.5,
        "volume_avg_20": 20800000,
    },
    "BBAS3": {
        "open": 28.5,
        "high": 29.0,
        "low": 28.2,
        "close": 28.7,
        "volume": 12000000,
        "rsi": 51.0,
        "macd_value": 0.03,
        "macd_signal_value": 0.03,
        "macd_signal": "neutro",
        "sma_20": 28.6,
        "ema_20": 28.7,
        "bb_upper": 29.6,
        "bb_lower": 27.5,
        "bb_mid": 28.6,
        "volume_avg_20": 11800000,
    },
    "ITUB4": {
        "open": 34.3,
        "high": 34.5,
        "low": 33.6,
        "close": 33.9,
        "volume": 15400000,
        "rsi": 43.3,
        "macd_value": -0.09,
        "macd_signal_value": -0.03,
        "macd_signal": "baixa",
        "sma_20": 34.2,
        "ema_20": 34.1,
        "bb_upper": 35.0,
        "bb_lower": 33.0,
        "bb_mid": 34.2,
        "volume_avg_20": 14900000,
    },
}


def get_market_signal(ticker: str, data_mode: str = "mock") -> MarketSignal:
    snapshot = get_technical_snapshot(ticker=ticker, data_mode=data_mode)

    return MarketSignal(
        ticker=snapshot.ticker,
        close=snapshot.close,
        rsi=snapshot.rsi,
        macd_signal=snapshot.macd_signal,
    )


def get_technical_snapshot(ticker: str, data_mode: str = "mock") -> TechnicalSnapshot:
    if data_mode == "real":
        return _get_technical_snapshot_real(ticker=ticker)
    return _get_technical_snapshot_mock(ticker=ticker)


def get_technical_snapshots_batch(tickers: Iterable[str], data_mode: str = "mock") -> list[TechnicalSnapshot]:
    snapshots: list[TechnicalSnapshot] = []
    for ticker in tickers:
        try:
            snapshots.append(get_technical_snapshot(ticker=ticker, data_mode=data_mode))
        except Exception:
            # Evita quebrar o lote completo por falha pontual de coleta/cálculo.
            snapshots.append(_get_technical_snapshot_mock(ticker=ticker, reported_data_mode=f"{data_mode}_fallback"))
    return snapshots


def get_technical_history(ticker: str, data_mode: str = "mock") -> list[TechnicalHistoryPoint]:
    if data_mode == "real":
        return _get_technical_history_real(ticker=ticker)

    snap = _get_technical_snapshot_mock(ticker=ticker)
    return [
        TechnicalHistoryPoint(
            ticker=snap.ticker,
            date=snap.date,
            open=snap.open,
            high=snap.high,
            low=snap.low,
            close=snap.close,
            volume=snap.volume,
            rsi=snap.rsi,
            macd_value=snap.macd_value,
            macd_signal_value=snap.macd_signal_value,
            macd_signal=snap.macd_signal,
            sma_20=snap.sma_20,
            ema_20=snap.ema_20,
            bb_upper=snap.bb_upper,
            bb_lower=snap.bb_lower,
            bb_mid=snap.bb_mid,
            volume_avg_20=snap.volume_avg_20,
            data_mode=snap.data_mode,
        )
    ]


def get_technical_history_batch(tickers: Iterable[str], data_mode: str = "mock") -> list[TechnicalHistoryPoint]:
    rows: list[TechnicalHistoryPoint] = []
    for ticker in tickers:
        try:
            rows.extend(get_technical_history(ticker=ticker, data_mode=data_mode))
        except Exception:
            rows.extend(get_technical_history(ticker=ticker, data_mode="mock"))
    return rows


def _get_technical_snapshot_mock(ticker: str, reported_data_mode: str = "mock") -> TechnicalSnapshot:
    data = MOCK_MARKET.get(
        ticker,
        {
            "open": 0.0,
            "high": 0.0,
            "low": 0.0,
            "close": 0.0,
            "volume": 0.0,
            "rsi": 50.0,
            "macd_value": 0.0,
            "macd_signal_value": 0.0,
            "macd_signal": "neutro",
            "sma_20": 0.0,
            "ema_20": 0.0,
            "bb_upper": 0.0,
            "bb_lower": 0.0,
            "bb_mid": 0.0,
            "volume_avg_20": 0.0,
        },
    )

    return TechnicalSnapshot(
        ticker=ticker,
        date=datetime.now(timezone.utc).date().isoformat(),
        open=float(data["open"]),
        high=float(data["high"]),
        low=float(data["low"]),
        close=float(data["close"]),
        volume=float(data["volume"]),
        rsi=float(data["rsi"]),
        macd_value=float(data["macd_value"]),
        macd_signal_value=float(data["macd_signal_value"]),
        macd_signal=str(data["macd_signal"]),
        sma_20=float(data["sma_20"]),
        ema_20=float(data["ema_20"]),
        bb_upper=float(data["bb_upper"]),
        bb_lower=float(data["bb_lower"]),
        bb_mid=float(data["bb_mid"]),
        volume_avg_20=float(data["volume_avg_20"]),
        data_mode=reported_data_mode,
    )


def _ticker_to_yahoo(ticker: str) -> str:
    return ticker if ticker.endswith(".SA") else f"{ticker}.SA"


def normalize_market_frame(df: pd.DataFrame) -> pd.DataFrame:
    # yfinance pode retornar colunas MultiIndex; normaliza para nome simples.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    expected = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes em OHLCV: {missing}")

    frame = df[expected].copy()
    for col in expected:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")

    frame = frame.dropna(subset=["Close"])
    frame = frame.sort_index()
    frame = frame[~frame.index.duplicated(keep="last")]
    return frame


def is_temporally_consistent(frame: pd.DataFrame) -> bool:
    if frame.empty:
        return False
    return bool(frame.index.is_monotonic_increasing and frame.index.is_unique)


def has_min_history(frame: pd.DataFrame, min_rows: int = MIN_BARS_FOR_TECHNICALS) -> bool:
    return len(frame) >= min_rows


def _get_technical_snapshot_real(ticker: str) -> TechnicalSnapshot:
    history = _get_technical_history_real(ticker=ticker)
    if not history:
        return _get_technical_snapshot_mock(ticker, reported_data_mode="real_fallback")

    last = history[-1]
    return TechnicalSnapshot(
        ticker=last.ticker,
        date=last.date,
        open=last.open,
        high=last.high,
        low=last.low,
        close=last.close,
        volume=last.volume,
        rsi=last.rsi,
        macd_value=last.macd_value,
        macd_signal_value=last.macd_signal_value,
        macd_signal=last.macd_signal,
        sma_20=last.sma_20,
        ema_20=last.ema_20,
        bb_upper=last.bb_upper,
        bb_lower=last.bb_lower,
        bb_mid=last.bb_mid,
        volume_avg_20=last.volume_avg_20,
        data_mode=last.data_mode,
    )


def _get_technical_history_real(ticker: str) -> list[TechnicalHistoryPoint]:
    symbol = _ticker_to_yahoo(ticker)
    period = settings.app_market_period

    df = yf.download(symbol, period=period, interval="1d", auto_adjust=False, progress=False)

    if df is None or df.empty:
        return []

    frame = normalize_market_frame(df)
    if frame.empty or not is_temporally_consistent(frame) or not has_min_history(frame):
        return []

    close = frame["Close"]
    volume = frame["Volume"]

    rsi_series = ta.rsi(close, length=14)
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    sma_20 = ta.sma(close, length=20)
    ema_20 = ta.ema(close, length=20)
    bbands = ta.bbands(close, length=20, std=2)
    vol_avg_20 = volume.rolling(20).mean()

    rows: list[TechnicalHistoryPoint] = []
    for idx in frame.index:
        close_value = float(frame.loc[idx, "Close"])
        volume_value = float(frame.loc[idx, "Volume"])

        macd_value = _value_at(macd_df, idx, "MACD_12_26_9", 0.0)
        macd_signal_value = _value_at(macd_df, idx, "MACDs_12_26_9", 0.0)
        if macd_value > macd_signal_value:
            macd_signal = "alta"
        elif macd_value < macd_signal_value:
            macd_signal = "baixa"
        else:
            macd_signal = "neutro"

        rows.append(
            TechnicalHistoryPoint(
                ticker=ticker,
                date=idx.date().isoformat(),
                open=float(frame.loc[idx, "Open"]),
                high=float(frame.loc[idx, "High"]),
                low=float(frame.loc[idx, "Low"]),
                close=close_value,
                volume=volume_value,
                rsi=_value_at_series(rsi_series, idx, 50.0),
                macd_value=macd_value,
                macd_signal_value=macd_signal_value,
                macd_signal=macd_signal,
                sma_20=_value_at_series(sma_20, idx, close_value),
                ema_20=_value_at_series(ema_20, idx, close_value),
                bb_upper=_value_at(bbands, idx, "BBU_20_2.0", close_value),
                bb_lower=_value_at(bbands, idx, "BBL_20_2.0", close_value),
                bb_mid=_value_at(bbands, idx, "BBM_20_2.0", close_value),
                volume_avg_20=_value_at_series(vol_avg_20, idx, volume_value),
                data_mode="real",
            )
        )

    return rows


def _last_or_default(series: pd.Series | None, default: float) -> float:
    if series is None:
        return float(default)
    clean = series.dropna()
    if clean.empty:
        return float(default)
    return float(clean.iloc[-1])


def _value_at(df: pd.DataFrame | None, idx: pd.Timestamp, col: str, default: float) -> float:
    if df is None or col not in df.columns or idx not in df.index:
        return float(default)
    value = df.loc[idx, col]
    if pd.isna(value):
        return float(default)
    return float(value)


def _value_at_series(series: pd.Series | None, idx: pd.Timestamp, default: float) -> float:
    if series is None or idx not in series.index:
        return float(default)
    value = series.loc[idx]
    if pd.isna(value):
        return float(default)
    return float(value)
