from typing import Iterable

from app.agents.langchain_agent import LangChainInvestmentAgent
from app.config.settings import settings
from app.domain.models import (
    DailyAnalysisRecord,
    NewsItem,
    Recommendation,
    RecommendationRecord,
    RunResult,
    TickerRunStatus,
)
from app.tools.market_tool import get_technical_history_batch, get_technical_snapshots_batch


def _normalize_macd_signal(value: str) -> str:
    raw = (value or "").strip().lower()
    if raw in {"bullish", "alta"}:
        return "bullish"
    if raw in {"bearish", "baixa"}:
        return "bearish"
    return "neutral"


def run_pipeline(
    tickers: Iterable[str],
    execution_mode: str | None = None,
    data_mode: str | None = None,
) -> list[Recommendation]:
    execution_mode = execution_mode or settings.app_default_execution_mode
    data_mode = data_mode or settings.app_default_data_mode
    result = run_pipeline_with_details(
        tickers=tickers,
        execution_mode=execution_mode,
        data_mode=data_mode,
    )
    return result.recommendations


def run_pipeline_with_details(
    tickers: Iterable[str],
    execution_mode: str | None = None,
    data_mode: str | None = None,
) -> RunResult:
    execution_mode = execution_mode or settings.app_default_execution_mode
    data_mode = data_mode or settings.app_default_data_mode
    # O mesmo pipeline roda por demanda ou modo agendável; muda apenas o gatilho.
    _ = execution_mode
    recommendations: list[Recommendation] = []
    recommendation_records: list[RecommendationRecord] = []
    daily_analysis: list[DailyAnalysisRecord] = []
    agent = LangChainInvestmentAgent(data_mode=data_mode)
    technical_snapshots = get_technical_snapshots_batch(tickers=tickers, data_mode=data_mode)
    technical_history = get_technical_history_batch(tickers=tickers, data_mode=data_mode)
    news_items: list[NewsItem] = []
    ticker_statuses: list[TickerRunStatus] = []

    for snapshot in technical_snapshots:
        news_notes = ""
        news_summary = ""
        matched_news_count = 0
        news_sentiment_score = 0.0
        avg_impact_score = 0.0
        try:
            agent_result = agent.run_for_snapshot(snapshot)
        except Exception as exc:
            raise RuntimeError(
                f"Falha no processamento do ticker {snapshot.ticker}. "
                "Corrija configuracao do Azure OpenAI e dependencias de dados antes de reexecutar. "
                f"Detalhe: {exc}"
            ) from exc

        recommendation = agent_result["recommendation"]
        news = agent_result["news_signal"]
        news_status = agent_result["news_status"]
        news_notes = agent_result["news_notes"]
        news_summary = agent_result["news_summary"]
        matched_news_count = agent_result["matched_news_count"]
        ticker_news_items = [NewsItem(**row) for row in agent_result["news_items"]]
        news_items.extend(ticker_news_items)

        total_votes = max(1, news.positive + news.negative + news.neutral)
        news_sentiment_score = (news.positive - news.negative) / total_votes
        if ticker_news_items:
            avg_impact_score = sum(item.impact_score for item in ticker_news_items) / len(ticker_news_items)
        recommendations.append(recommendation)

        market_status = "ok_real" if snapshot.data_mode == "real" else f"ok_{snapshot.data_mode}"

        ticker_status = TickerRunStatus(
            ticker=snapshot.ticker,
            market_status=market_status,
            news_status=news_status,
            notes=news_notes,
            matched_news_count=matched_news_count,
            news_sentiment_score=round(news_sentiment_score, 4),
            avg_impact_score=round(avg_impact_score, 4),
            news_summary=news_summary,
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

        daily_analysis.append(
            DailyAnalysisRecord(
                ticker=snapshot.ticker,
                date=snapshot.date,
                close=round(float(snapshot.close), 4),
                rsi=round(float(snapshot.rsi), 4),
                macd_signal=_normalize_macd_signal(snapshot.macd_signal),
                news_sentiment=round(float(news_sentiment_score), 4),
                recommendation=recommendation.recommendation,
                data_mode=snapshot.data_mode,
            )
        )

    return RunResult(
        recommendations=recommendations,
        recommendation_records=recommendation_records,
        technical_snapshots=technical_snapshots,
        technical_history=technical_history,
        news_items=news_items,
        ticker_statuses=ticker_statuses,
        daily_analysis=daily_analysis,
    )
