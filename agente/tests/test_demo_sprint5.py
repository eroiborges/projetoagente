from app.agents.explainer_agent import explain_question
from app.agents.langchain_agent import LangChainInvestmentAgent
from app.domain.models import Recommendation, utc_now_iso
from app.pipelines.run_analysis import run_pipeline_with_details
from app.tools.backtest_tool import build_backtest_rows, build_metrics_report, summarize_backtest, summarize_backtest_by_ticker


def _stub_llm_decide(self, ticker, technical, news_signal):
    rec = Recommendation(
        ticker=ticker,
        recommendation="COMPRAR",
        confidence=0.8,
        rationale="Decisao LLM de teste.",
        generated_at=utc_now_iso(),
        evidence={"signal_breakers": ["teste"]},
    )
    return rec, "azure_openai"


def _stub_llm_reflection(self, ticker, technical, news_signal, action):
    return "Reflexao de teste.", "azure_openai"


def test_demo_pipeline_end_to_end_mock_contract(monkeypatch) -> None:
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_decide_recommendation", _stub_llm_decide)
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_reflection", _stub_llm_reflection)

    tickers = ["VALE3", "PETR4", "BBAS3", "ITUB4"]
    result = run_pipeline_with_details(tickers=tickers, execution_mode="on_demand", data_mode="mock")

    assert len(result.recommendations) == len(tickers)
    assert len(result.recommendation_records) == len(tickers)
    assert len(result.technical_snapshots) == len(tickers)
    assert len(result.ticker_statuses) == len(tickers)

    recommendation_tickers = {item.ticker for item in result.recommendations}
    status_tickers = {item.ticker for item in result.ticker_statuses}
    assert recommendation_tickers == set(tickers)
    assert status_tickers == set(tickers)

    assert all(item.recommendation in {"COMPRAR", "VENDER", "AGUARDAR"} for item in result.recommendations)
    assert all(0 <= item.confidence <= 1 for item in result.recommendations)
    assert all("llm_decision_source" in item.evidence for item in result.recommendations)


def test_demo_chat_key_questions_single_ticker(monkeypatch) -> None:
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_decide_recommendation", _stub_llm_decide)
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_reflection", _stub_llm_reflection)

    result = run_pipeline_with_details(tickers=["ITUB4"], execution_mode="on_demand", data_mode="mock")

    why_answer = explain_question("Por que ITUB4 ficou assim hoje?", result)
    assert "ITUB4" in why_answer
    assert why_answer.strip()

    change_answer = explain_question("O que mudaria para virar VENDER em ITUB4?", result)
    assert "ITUB4" in change_answer
    assert change_answer.strip()

    risk_answer = explain_question("Quais os riscos da recomendacao para ITUB4?", result)
    assert risk_answer.strip()

    summary_answer = explain_question("Resumo de ITUB4", result)
    assert "ITUB4" in summary_answer

    technical_answer = explain_question("Mostre o tecnico de ITUB4", result)
    assert "ITUB4" in technical_answer

    news_answer = explain_question("Quais noticias de ITUB4 hoje?", result)
    assert "ITUB4" in news_answer
    assert news_answer.strip()


def test_demo_chat_compare_two_tickers(monkeypatch) -> None:
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_decide_recommendation", _stub_llm_decide)
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_reflection", _stub_llm_reflection)

    result = run_pipeline_with_details(tickers=["ITUB4", "VALE3"], execution_mode="on_demand", data_mode="mock")

    answer = explain_question("Compare ITUB4 e VALE3", result)

    assert "ITUB4" in answer
    assert "VALE3" in answer


def test_demo_backtest_integration_runs_with_pipeline_outputs(monkeypatch) -> None:
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_decide_recommendation", _stub_llm_decide)
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_reflection", _stub_llm_reflection)

    result = run_pipeline_with_details(tickers=["ITUB4", "VALE3"], execution_mode="on_demand", data_mode="mock")

    rows = build_backtest_rows(result.recommendation_records, result.technical_history)
    summary = summarize_backtest(rows)
    by_ticker = summarize_backtest_by_ticker(rows)
    report = build_metrics_report(summary=summary, by_ticker=by_ticker)

    assert isinstance(rows, list)
    assert summary["total_signals"] == len(rows)
    assert "hit_rate" in summary
    assert "avg_strategy_return" in summary
    assert "avg_buy_hold_return" in summary
    assert "avg_alpha_vs_buy_hold" in summary
    assert isinstance(by_ticker, dict)
    assert "consolidado" in report
    assert "ranking_alpha" in report


def test_demo_chat_requires_ticker_when_question_is_generic(monkeypatch) -> None:
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_decide_recommendation", _stub_llm_decide)
    monkeypatch.setattr(LangChainInvestmentAgent, "_llm_reflection", _stub_llm_reflection)

    result = run_pipeline_with_details(tickers=["ITUB4", "VALE3"], execution_mode="on_demand", data_mode="mock")

    answer = explain_question("Explique a recomendacao", result)

    assert "tickers disponiveis" in answer.lower()
