from dataclasses import dataclass, field
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
    evidence: dict[str, object] = field(default_factory=dict)


@dataclass
class RecommendationRecord:
    ticker: str
    recommendation: str
    confidence: float
    rationale: str
    generated_at: str
    data_mode: str
    market_status: str
    news_status: str
    matched_news_count: int
    news_sentiment_score: float
    avg_impact_score: float
    evidence: dict[str, object] = field(default_factory=dict)


@dataclass
class DailyAnalysisRecord:
    ticker: str
    date: str
    close: float
    rsi: float
    macd_signal: str
    news_sentiment: float
    recommendation: str
    data_mode: str


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
class NewsItem:
    ticker: str
    source: str
    published_at: str
    title: str
    url: str
    summary: str
    sentiment_label: str
    sentiment_score: float
    impact_score: float
    data_mode: str


@dataclass
class TickerRunStatus:
    ticker: str
    market_status: str
    news_status: str
    notes: str
    matched_news_count: int
    news_sentiment_score: float
    avg_impact_score: float
    news_summary: str = ""


@dataclass
class RunResult:
    recommendations: list[Recommendation]
    technical_snapshots: list[TechnicalSnapshot]
    technical_history: list[TechnicalHistoryPoint]
    news_items: list[NewsItem]
    ticker_statuses: list[TickerRunStatus]
    recommendation_records: list[RecommendationRecord] = field(default_factory=list)
    daily_analysis: list[DailyAnalysisRecord] = field(default_factory=list)


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
