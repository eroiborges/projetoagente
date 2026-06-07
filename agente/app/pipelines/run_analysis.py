from typing import Iterable

from app.agents.decision_agent import recommend
from app.domain.models import (
    MarketSignal,
    NewsItem,
    NewsSignal,
    Recommendation,
    RecommendationRecord,
    RunResult,
    TickerRunStatus,
)
from app.tools.market_tool import get_technical_history_batch, get_technical_snapshots_batch
from app.tools.news_tool import get_news_analysis


def run_pipeline(
    tickers: Iterable[str],
    execution_mode: str = "on_demand",
    data_mode: str = "mock",
) -> list[Recommendation]:
    result = run_pipeline_with_details(
        tickers=tickers,
        execution_mode=execution_mode,
        data_mode=data_mode,
    )
    return result.recommendations


def run_pipeline_with_details(
    tickers: Iterable[str],
    execution_mode: str = "on_demand",
    data_mode: str = "mock",
) -> RunResult:
    # O mesmo pipeline roda por demanda ou modo agendável; muda apenas o gatilho.
    _ = execution_mode
    recommendations: list[Recommendation] = []
    recommendation_records: list[RecommendationRecord] = []
    technical_snapshots = get_technical_snapshots_batch(tickers=tickers, data_mode=data_mode)
    technical_history = get_technical_history_batch(tickers=tickers, data_mode=data_mode)
    news_items: list[NewsItem] = []
    ticker_statuses: list[TickerRunStatus] = []

    for snapshot in technical_snapshots:
        market = MarketSignal(
            ticker=snapshot.ticker,
            close=snapshot.close,
            rsi=snapshot.rsi,
            macd_signal=snapshot.macd_signal,
        )
        news_notes = ""
        matched_news_count = 0
        news_sentiment_score = 0.0
        avg_impact_score = 0.0
        try:
            news, news_status, news_notes, matched_news_count, ticker_news_items = get_news_analysis(
                ticker=snapshot.ticker,
                data_mode=data_mode,
            )
            news_items.extend(ticker_news_items)

            total_votes = max(1, news.positive + news.negative + news.neutral)
            news_sentiment_score = (news.positive - news.negative) / total_votes
            if ticker_news_items:
                avg_impact_score = sum(item.impact_score for item in ticker_news_items) / len(ticker_news_items)
        except Exception:
            news = NewsSignal(ticker=snapshot.ticker, positive=0, negative=0, neutral=1, consensus="neutral")
            news_status = f"error_{data_mode}_fallback"
            news_notes = "news_exception_fallback"
            matched_news_count = 0
            news_sentiment_score = 0.0
            avg_impact_score = 0.0

        recommendation = recommend(market, news)
        recommendations.append(recommendation)

        market_status = "ok_real" if snapshot.data_mode == "real" else f"ok_{snapshot.data_mode}"
        if "fallback" in snapshot.data_mode:
            market_status = "error_real_fallback"

        ticker_status = TickerRunStatus(
            ticker=snapshot.ticker,
            market_status=market_status,
            news_status=news_status,
            notes=news_notes,
            matched_news_count=matched_news_count,
            news_sentiment_score=round(news_sentiment_score, 4),
            avg_impact_score=round(avg_impact_score, 4),
        )
        ticker_statuses.append(ticker_status)

        recommendation_records.append(
            RecommendationRecord(
                ticker=recommendation.ticker,
                recommendation=recommendation.recommendation,
                confidence=recommendation.confidence,
                rationale=recommendation.rationale,
                generated_at=recommendation.generated_at,
                data_mode=snapshot.data_mode,
                market_status=ticker_status.market_status,
                news_status=ticker_status.news_status,
                matched_news_count=ticker_status.matched_news_count,
                news_sentiment_score=ticker_status.news_sentiment_score,
                avg_impact_score=ticker_status.avg_impact_score,
                evidence=recommendation.evidence,
            )
        )

    return RunResult(
        recommendations=recommendations,
        recommendation_records=recommendation_records,
        technical_snapshots=technical_snapshots,
        technical_history=technical_history,
        news_items=news_items,
        ticker_statuses=ticker_statuses,
    )
