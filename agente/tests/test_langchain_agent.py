from app.agents.langchain_agent import LangChainInvestmentAgent, LANGCHAIN_AVAILABLE
from app.tools.market_tool import get_technical_snapshot


def test_langchain_agent_executes_required_tools_mock() -> None:
    agent = LangChainInvestmentAgent(data_mode="mock")
    snapshot = get_technical_snapshot("ITUB4", data_mode="mock")

    result = agent.run_for_snapshot(snapshot)

    recommendation = result["recommendation"]
    assert recommendation.ticker == "ITUB4"
    assert recommendation.recommendation in {"COMPRAR", "VENDER", "AGUARDAR"}
    assert recommendation.evidence["tool_trace"] == [
        "get_price_data",
        "calculate_indicators",
        "search_news",
        "generate_recommendation",
    ]
    assert recommendation.evidence["agent_framework"] in {"langchain", "langchain_fallback"}
    assert isinstance(recommendation.evidence.get("react_trace"), list)
    assert len(recommendation.evidence.get("react_trace", [])) >= 4
    assert recommendation.evidence.get("llm_source") in {"desabilitado", "azure_openai", "erro_azure_openai"}


def test_langchain_agent_exposes_declared_toolset() -> None:
    agent = LangChainInvestmentAgent(data_mode="mock")

    assert agent.tool_names == [
        "search_news",
        "get_price_data",
        "calculate_indicators",
        "generate_recommendation",
    ]
    if LANGCHAIN_AVAILABLE:
        assert len(agent.tools) == 4
