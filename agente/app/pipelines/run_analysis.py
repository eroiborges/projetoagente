from typing import Iterable

from app.agents.decision_agent import recommend
from app.domain.models import MarketSignal, NewsSignal, Recommendation, RunResult, TickerRunStatus
from app.tools.market_tool import get_technical_history_batch, get_technical_snapshots_batch
from app.tools.news_tool import get_news_signal_with_details


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
    technical_snapshots = get_technical_snapshots_batch(tickers=tickers, data_mode=data_mode)
    technical_history = get_technical_history_batch(tickers=tickers, data_mode=data_mode)
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
        try:
            news, news_status, news_notes, matched_news_count = get_news_signal_with_details(
                ticker=snapshot.ticker,
                data_mode=data_mode,
            )
        except Exception:
            news = NewsSignal(ticker=snapshot.ticker, positive=0, negative=0, neutral=1, consensus="neutral")
            news_status = f"error_{data_mode}_fallback"
            news_notes = "news_exception_fallback"
            matched_news_count = 0

        recommendations.append(recommend(market, news))

        market_status = "ok_real" if snapshot.data_mode == "real" else f"ok_{snapshot.data_mode}"
        if "fallback" in snapshot.data_mode:
            market_status = "error_real_fallback"

        ticker_statuses.append(
            TickerRunStatus(
                ticker=snapshot.ticker,
                market_status=market_status,
                news_status=news_status,
                notes=news_notes,
                matched_news_count=matched_news_count,
            )
        )

    return RunResult(
        recommendations=recommendations,
        technical_snapshots=technical_snapshots,
        technical_history=technical_history,
        ticker_statuses=ticker_statuses,
    )
