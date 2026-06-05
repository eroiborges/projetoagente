from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsSignal:
    ticker: str
    positive: int
    negative: int
    neutral: int
    consensus: str


@dataclass
class MarketSignal:
    ticker: str
    close: float
    rsi: float
    macd_signal: str


@dataclass
class Recommendation:
    ticker: str
    recommendation: str
    confidence: float
    rationale: str
    generated_at: str


@dataclass
class TechnicalSnapshot:
    ticker: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    rsi: float
    macd_value: float
    macd_signal_value: float
    macd_signal: str
    sma_20: float
    ema_20: float
    bb_upper: float
    bb_lower: float
    bb_mid: float
    volume_avg_20: float
    data_mode: str


@dataclass
class TechnicalHistoryPoint:
    ticker: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    rsi: float
    macd_value: float
    macd_signal_value: float
    macd_signal: str
    sma_20: float
    ema_20: float
    bb_upper: float
    bb_lower: float
    bb_mid: float
    volume_avg_20: float
    data_mode: str


@dataclass
class TickerRunStatus:
    ticker: str
    market_status: str
    news_status: str
    notes: str
    matched_news_count: int


@dataclass
class RunResult:
    recommendations: list[Recommendation]
    technical_snapshots: list[TechnicalSnapshot]
    technical_history: list[TechnicalHistoryPoint]
    ticker_statuses: list[TickerRunStatus]


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
