from app.agents.explainer_agent import explain_question, get_agent_system_prompt
from app.domain.models import NewsItem, Recommendation, RunResult, TechnicalHistoryPoint, TechnicalSnapshot, TickerRunStatus


def _build_result(
    recommendation: str = "COMPRAR",
    confidence: float = 0.72,
    rsi: float = 38.0,
    macd_signal: str = "alta",
    news_sentiment_score: float = 0.5,
    avg_impact_score: float = 0.8,
    matched_news_count: int = 1,
    news_sentiment_label: str = "positive",
) -> RunResult:
    rec = Recommendation(
        ticker="ITUB4",
        recommendation=recommendation,
        confidence=confidence,
        rationale="MACD=alta, RSI=38.0, sentimento=neutro.",
        generated_at="2026-06-06T10:00:00Z",
    )
    snap = TechnicalSnapshot(
        ticker="ITUB4",
        date="2026-06-06",
        open=34.0,
        high=35.0,
        low=33.5,
        close=34.5,
        volume=1000.0,
        rsi=rsi,
        macd_value=0.2,
        macd_signal_value=0.1,
        macd_signal=macd_signal,
        sma_20=34.2,
        ema_20=34.1,
        bb_upper=35.4,
        bb_lower=33.1,
        bb_mid=34.2,
        volume_avg_20=900.0,
        data_mode="real",
    )
    hist = TechnicalHistoryPoint(
        ticker="ITUB4",
        date="2026-06-06",
        open=34.0,
        high=35.0,
        low=33.5,
        close=34.5,
        volume=1000.0,
        rsi=rsi,
        macd_value=0.2,
        macd_signal_value=0.1,
        macd_signal=macd_signal,
        sma_20=34.2,
        ema_20=34.1,
        bb_upper=35.4,
        bb_lower=33.1,
        bb_mid=34.2,
        volume_avg_20=900.0,
        data_mode="real",
    )
    news = NewsItem(
        ticker="ITUB4",
        source="b3",
        published_at="2026-06-06T09:00:00+00:00",
        title="ITUB4 sobe com melhora de resultado",
        url="https://example.com/news-itub4",
        summary="Resumo",
        sentiment_label=news_sentiment_label,
        sentiment_score=1.0,
        impact_score=avg_impact_score,
        data_mode="real",
    )
    status = TickerRunStatus(
        ticker="ITUB4",
        market_status="ok_real",
        news_status="ok_real",
        notes="live_feeds",
        matched_news_count=matched_news_count,
        news_sentiment_score=news_sentiment_score,
        avg_impact_score=avg_impact_score,
    )
    return RunResult(
        recommendations=[rec],
        technical_snapshots=[snap],
        technical_history=[hist],
        news_items=[news],
        ticker_statuses=[status],
    )


def test_explainer_answers_recommendation() -> None:
    result = _build_result()
    answer = explain_question("Qual a recomendacao para ITUB4?", result)
    assert "ITUB4" in answer
    assert "COMPRAR" in answer
    assert "MACD" in answer
    assert "Justificativa:" not in answer


def test_explainer_answers_news() -> None:
    result = _build_result()
    answer = explain_question("Quais noticias de ITUB4 hoje?", result)
    assert "noticias casadas" in answer
    assert "impacto 0.80" in answer
    assert "https://example.com/news-itub4" in answer


def test_explainer_answers_why_with_natural_language() -> None:
    result = _build_result()
    answer = explain_question("Por que ITUB4 ficou COMPRAR?", result)
    assert "ITUB4 ficou em COMPRAR hoje" in answer
    assert "Causa principal" in answer
    assert "Confianca:" in answer
    assert "Limites:" in answer
    assert "Exemplos para leitura" in answer


def test_explainer_answers_change_conditions() -> None:
    result = _build_result()
    answer = explain_question("O que teria que acontecer para virar VENDER em ITUB4?", result)
    assert "pelo menos dois vetores" in answer
    assert "MACD virar para baixa" in answer


def test_explainer_answers_risks() -> None:
    result = _build_result()
    answer = explain_question("Quais riscos dessa recomendacao hoje para ITUB4?", result)
    assert "Riscos principais" in answer
    assert "impacto alto" in answer


def test_explainer_change_for_vender_scenario() -> None:
    result = _build_result(
        recommendation="VENDER",
        confidence=0.75,
        rsi=66.0,
        macd_signal="baixa",
        news_sentiment_score=-0.5,
        avg_impact_score=0.7,
        news_sentiment_label="negative",
    )
    answer = explain_question("O que teria que acontecer para virar COMPRAR em ITUB4?", result)
    assert "Caminho mais claro para COMPRAR" in answer
    assert "MACD virar para alta" in answer


def test_explainer_summary_for_aguardar_scenario() -> None:
    result = _build_result(
        recommendation="AGUARDAR",
        confidence=0.55,
        rsi=51.0,
        macd_signal="neutro",
        news_sentiment_score=0.0,
        avg_impact_score=0.2,
        matched_news_count=0,
        news_sentiment_label="neutral",
    )
    answer = explain_question("Resumo de ITUB4", result)
    assert "AGUARDAR" in answer
    assert "Nao houve noticias casadas relevantes" in answer
    assert "O sinal pode mudar" in answer


def test_explainer_summary_includes_news_examples_when_available() -> None:
    result = _build_result()
    answer = explain_question("Resumo de ITUB4", result)
    assert "Exemplos para leitura" in answer
    assert "https://example.com/news-itub4" in answer


def test_explainer_why_clarifies_current_recommendation_when_question_disagrees() -> None:
    result = _build_result(
        recommendation="VENDER",
        confidence=0.75,
        rsi=66.0,
        macd_signal="baixa",
        news_sentiment_score=-0.5,
        avg_impact_score=0.7,
        news_sentiment_label="negative",
    )
    answer = explain_question("Por que ITUB4 ficou COMPRAR?", result)
    assert "nao ficou em COMPRAR hoje" in answer
    assert "o sinal atual e VENDER" in answer
    assert "Causa principal" in answer


def test_explainer_requires_ticker_when_missing() -> None:
    result = _build_result()
    answer = explain_question("Explique a recomendacao", result)
    assert "tickers disponiveis" in answer.lower()


def test_explainer_exposes_system_prompt() -> None:
    prompt = get_agent_system_prompt()
    assert "PT-BR" in prompt
    assert "nao inventar dados ausentes" in prompt


def test_explainer_compares_two_tickers() -> None:
    result = _build_result()
    result.recommendations.append(
        Recommendation(
            ticker="VALE3",
            recommendation="VENDER",
            confidence=0.81,
            rationale="Tecnico: MACD em baixa. Noticias: consenso negativo. Decisao final: VENDER.",
            generated_at="2026-06-06T10:00:00Z",
            evidence={
                "technical_factors": ["MACD em baixa"],
                "news_factors": ["Consenso de noticias negativo"],
            },
        )
    )
    result.technical_snapshots.append(
        TechnicalSnapshot(
            ticker="VALE3",
            date="2026-06-06",
            open=61.0,
            high=62.0,
            low=60.0,
            close=60.5,
            volume=2000.0,
            rsi=62.0,
            macd_value=-0.3,
            macd_signal_value=-0.1,
            macd_signal="baixa",
            sma_20=61.2,
            ema_20=61.0,
            bb_upper=63.0,
            bb_lower=59.0,
            bb_mid=61.0,
            volume_avg_20=1800.0,
            data_mode="real",
        )
    )
    result.news_items.append(
        NewsItem(
            ticker="VALE3",
            source="reuters",
            published_at="2026-06-06T09:30:00+00:00",
            title="VALE3 recua com pressao em mineradoras",
            url="https://example.com/news-vale3",
            summary="Resumo",
            sentiment_label="negative",
            sentiment_score=-1.0,
            impact_score=0.7,
            data_mode="real",
        )
    )
    result.ticker_statuses.append(
        TickerRunStatus(
            ticker="VALE3",
            market_status="ok_real",
            news_status="ok_real",
            notes="live_feeds",
            matched_news_count=2,
            news_sentiment_score=-0.4,
            avg_impact_score=0.7,
        )
    )

    answer = explain_question("Compare ITUB4 e VALE3", result)
    assert "Comparando ITUB4 e VALE3" in answer
    assert "Sinal mais convicto agora" in answer
    assert "VALE3" in answer


def test_explainer_compares_two_tickers() -> None:
    result = _build_result()
    result.recommendations.append(
        Recommendation(
            ticker="VALE3",
            recommendation="VENDER",
            confidence=0.81,
            rationale="Tecnico: MACD em baixa. Noticias: consenso negativo. Decisao final: VENDER.",
            generated_at="2026-06-06T10:00:00Z",
            evidence={
                "technical_factors": ["MACD em baixa"],
                "news_factors": ["Consenso de noticias negativo"],
            },
        )
    )
    result.technical_snapshots.append(
        TechnicalSnapshot(
            ticker="VALE3",
            date="2026-06-06",
            open=61.0,
            high=62.0,
            low=60.0,
            close=60.5,
            volume=2000.0,
            rsi=62.0,
            macd_value=-0.3,
            macd_signal_value=-0.1,
            macd_signal="baixa",
            sma_20=61.2,
            ema_20=61.0,
            bb_upper=63.0,
            bb_lower=59.0,
            bb_mid=61.0,
            volume_avg_20=1800.0,
            data_mode="real",
        )
    )
    result.news_items.append(
        NewsItem(
            ticker="VALE3",
            source="reuters",
            published_at="2026-06-06T09:30:00+00:00",
            title="VALE3 recua com pressao em mineradoras",
            url="https://example.com/news-vale3",
            summary="Resumo",
            sentiment_label="negative",
            sentiment_score=-1.0,
            impact_score=0.7,
            data_mode="real",
        )
    )
    result.ticker_statuses.append(
        TickerRunStatus(
            ticker="VALE3",
            market_status="ok_real",
            news_status="ok_real",
            notes="live_feeds",
            matched_news_count=2,
            news_sentiment_score=-0.4,
            avg_impact_score=0.7,
        )
    )

    answer = explain_question("Compare ITUB4 e VALE3", result)
    assert "Comparando ITUB4 e VALE3" in answer
    assert "Sinal mais convicto agora" in answer
    assert "VALE3" in answer
