from collections.abc import Callable

from app.agents.system_prompt import MAX_TOOL_ITERATIONS, get_system_prompt
from app.domain.models import RunResult
from app.tools.insight_tools import (
    detect_ticker,
    detect_tickers,
    get_news_context,
    get_recommendation_context,
    get_status_context,
    get_technical_context,
    list_tickers,
)


def explain_question(question: str, run_result: RunResult, default_ticker: str | None = None) -> str:
    if run_result is None:
        return "Ainda nao ha execucao para explicar. Rode o pipeline primeiro."

    question_norm = (question or "").strip()
    if not question_norm:
        return "Escreva uma pergunta sobre recomendacao, tecnico ou noticias de um ticker."

    question_lower = _normalize_text(question_norm)
    intent = _detect_intent(question_lower)
    if intent == "compare":
        tickers = detect_tickers(question_norm, run_result)
        if len(tickers) < 2:
            available = ", ".join(list_tickers(run_result))
            return f"Para comparar, cite pelo menos dois tickers na pergunta. Tickers disponiveis: {available}."
        return _answer_compare(run_result, tickers[:2])

    ticker = detect_ticker(question_norm, run_result) or (default_ticker or "").strip().upper()
    if not ticker:
        tickers = ", ".join(list_tickers(run_result))
        return f"Nao identifiquei o ticker na pergunta. Tickers disponiveis: {tickers}."

    context = _run_tool_loop(run_result, ticker, intent)
    return _compose_answer(intent, ticker, question_lower, context)


def get_agent_system_prompt() -> str:
    return get_system_prompt()


def _run_tool_loop(run_result: RunResult, ticker: str, intent: str) -> dict:
    tool_context: dict[str, dict | None] = {
        "recommendation": None,
        "technical": None,
        "news": None,
        "status": None,
    }
    plan = _build_tool_plan(intent)
    handlers: dict[str, Callable[[], dict | None]] = {
        "recommendation": lambda: get_recommendation_context(run_result, ticker),
        "technical": lambda: get_technical_context(run_result, ticker),
        "news": lambda: get_news_context(run_result, ticker, top_n=3),
        "status": lambda: get_status_context(run_result, ticker),
    }

    steps = 0
    for tool_name in plan:
        if steps >= MAX_TOOL_ITERATIONS:
            break
        tool_context[tool_name] = handlers[tool_name]()
        steps += 1

    tool_context["meta"] = {
        "intent": intent,
        "steps_used": steps,
        "max_steps": MAX_TOOL_ITERATIONS,
        "system_prompt": get_agent_system_prompt(),
    }
    return tool_context


def _build_tool_plan(intent: str) -> list[str]:
    if intent == "news":
        return ["news", "status"]
    if intent == "technical":
        return ["technical"]
    if intent == "change":
        return ["recommendation"]
    if intent == "risk":
        return ["recommendation", "technical", "status"]
    return ["recommendation", "technical", "status", "news"]


def _compose_answer(intent: str, ticker: str, question: str, context: dict) -> str:
    if intent == "news":
        return _answer_news(ticker, context)
    if intent == "technical":
        return _answer_technical(ticker, context)
    if intent == "why":
        return _answer_why(ticker, question, context)
    if intent == "change":
        return _answer_change(ticker, question, context)
    if intent == "risk":
        return _answer_risk(ticker, context)
    return _answer_summary(ticker, context)


def _normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def _detect_intent(question: str) -> str:
    if any(k in question for k in ["compar", "compare", "versus", " vs ", "entre "]):
        return "compare"
    if any(k in question for k in ["o que mudaria", "mudaria", "para virar", "virar ", "mudar para"]):
        return "change"
    if any(k in question for k in ["risco", "riscos"]):
        return "risk"
    if any(k in question for k in ["resumo", "resuma", "visao geral"]):
        return "summary"
    if any(k in question for k in ["noticia", "noticias", "news"]):
        return "news"
    if any(k in question for k in ["tecnico", "tecnica", "rsi", "macd", "indicador"]):
        return "technical"
    if any(k in question for k in ["por que", "porque", "motivo", "explica", "explique"]):
        return "why"
    return "summary"


def _answer_recommendation(ticker: str, context: dict) -> str:
    rec = context.get("recommendation")
    if rec is None:
        return f"Nao encontrei recomendacao para {ticker}."
    return f"{ticker} esta em {rec['recomendacao']} com confianca de {rec['confianca']:.0%}."


def _answer_technical(ticker: str, context: dict) -> str:
    tech = context.get("technical")
    if tech is None:
        return f"Nao encontrei dados tecnicos para {ticker}."

    return (
        f"Panorama tecnico de {ticker}:\n\n"
        f"Fechamento em {tech['close']:.2f}. O MACD aponta {_describe_macd(tech['macd_signal'])} "
        f"e o RSI esta em {tech['rsi']:.1f}, o que sugere {_describe_rsi(tech['rsi'])}. "
        f"As medias curtas seguem em SMA20={tech['sma_20']:.2f} e EMA20={tech['ema_20']:.2f}."
    )


def _answer_news(ticker: str, context: dict) -> str:
    news = context.get("news")
    status = context.get("status")
    if news is None:
        return f"Nao encontrei noticias casadas para {ticker} nesta execucao."
    if news["total_noticias"] == 0:
        return f"Nao encontrei noticias casadas para {ticker} nesta execucao."

    sentiment_text = _describe_news_sentiment(status)
    highlights = _format_news_examples(news)
    return (
        f"Panorama de noticias de {ticker}:\n\n"
        f"Encontrei {news['total_noticias']} noticias casadas. O contexto agregado esta {sentiment_text}. "
        f"Principais destaques: {highlights}."
    )


def _answer_why(ticker: str, question: str, context: dict) -> str:
    rec = context.get("recommendation")
    tech = context.get("technical")
    status = context.get("status")
    news = context.get("news")
    if rec is None or tech is None:
        return f"Nao encontrei contexto suficiente para explicar {ticker}."

    news_clause = _build_news_clause(status, news)
    requested_target = _extract_requested_recommendation(question)
    if requested_target and requested_target != rec["recomendacao"]:
        intro = (
            f"{ticker} nao ficou em {requested_target} hoje; o sinal atual e {rec['recomendacao']}."
        )
    else:
        intro = f"{ticker} ficou em {rec['recomendacao']} hoje."
    evidence_text = _format_evidence_highlights(rec.get("evidencias", {}))
    return (
        f"{intro}\n\n"
        f"Causa principal: o quadro tecnico favorece essa leitura. O MACD aponta {_describe_macd(tech['macd_signal'])} "
        f"e o RSI em {tech['rsi']:.1f} indica {_describe_rsi(tech['rsi'])}.\n\n"
        f"Evidencias rastreaveis: {evidence_text}.\n\n"
        f"Contexto de noticias: {news_clause}\n\n"
        f"Confianca: {rec['confianca']:.0%}.\n\n"
        f"Limites: nao e um sinal definitivo. Se o MACD perder direcao, se o RSI migrar para a faixa oposta ou se o fluxo de noticias piorar, a recomendacao pode mudar."
    )


def _answer_change(ticker: str, question: str, context: dict) -> str:
    rec = context.get("recommendation")
    if rec is None:
        return f"Nao encontrei recomendacao para {ticker}."

    evidence = rec.get("evidencias", {})
    requested_target = _extract_requested_recommendation(question)
    current = rec["recomendacao"]
    target = requested_target or _default_change_target(current)
    signal_breakers = evidence.get("signal_breakers", [])

    if target == "VENDER":
        conditions = "o MACD virar para baixa, o RSI passar de 60 e/ou o consenso de noticias ficar negativo"
    elif target == "COMPRAR":
        conditions = "o MACD virar para alta, o RSI cair abaixo de 40 e/ou o consenso de noticias melhorar para positivo"
    else:
        conditions = "pelo menos dois vetores ganharem a mesma direcao, como MACD e noticias apontando juntos ou um RSI em zona mais extrema"

    if target == current:
        return (
            f"Hoje {ticker} ja esta em {current}.\n\n"
            f"Para perder esse sinal e migrar para outro estado, o modelo precisaria ver pelo menos dois vetores mudando de direcao. "
            f"O caminho mais claro seria o oposto de agora: {_format_signal_breakers(signal_breakers) or _conditions_for_opposite(current)}."
        )

    return (
        f"Para {ticker} mudar o sinal atual, o modelo precisa ver deterioracao ou melhora suficiente em pelo menos dois vetores.\n\n"
        f"Caminho mais claro para {target}: {_format_signal_breakers(signal_breakers) or conditions}.\n\n"
        f"Se apenas um fator oscilar isoladamente, a tendencia e a recomendacao ficar mais perto de AGUARDAR do que fazer uma virada completa."
    )


def _answer_risk(ticker: str, context: dict) -> str:
    rec = context.get("recommendation")
    tech = context.get("technical")
    status = context.get("status")
    if rec is None or tech is None:
        return f"Nao encontrei contexto suficiente para avaliar os riscos de {ticker}."

    risk_items = [
        _technical_risk(tech["macd_signal"], tech["rsi"]),
        _news_risk(status),
        f"A confianca de {rec['confianca']:.0%} ajuda, mas ainda deixa margem para reversao se os dados do proximo ciclo vierem piores.",
        f"Os gatilhos mais claros de mudanca hoje sao: {_format_signal_breakers(rec.get('evidencias', {}).get('signal_breakers', []))}.",
    ]
    return (
        f"Riscos principais de {ticker} hoje:\n\n"
        f"1. {risk_items[0]}\n"
        f"2. {risk_items[1]}\n"
        f"3. {risk_items[2]}\n"
        f"4. {risk_items[3]}"
    )


def _answer_summary(ticker: str, context: dict) -> str:
    rec = context.get("recommendation")
    tech = context.get("technical")
    status = context.get("status")
    news = context.get("news")
    if rec is None:
        return f"Nao encontrei recomendacao para {ticker}."

    parts = [f"Resumo de {ticker}: recomendacao em {rec['recomendacao']} com confianca de {rec['confianca']:.0%}."]
    if tech is not None:
        parts.append(
            f"No tecnico, MACD em {tech['macd_signal']} e RSI em {tech['rsi']:.1f}, sugerindo {_describe_rsi(tech['rsi'])}."
        )
    evidence_text = _format_evidence_highlights(rec.get("evidencias", {}))
    if evidence_text:
        parts.append(f"Evidencias principais: {evidence_text}.")
    parts.append(_build_news_clause(status, news))
    parts.append("O sinal pode mudar se tecnico e noticias deixarem de apontar na mesma direcao.")
    return "\n\n".join(parts)


def _answer_compare(run_result: RunResult, tickers: list[str]) -> str:
    first, second = tickers[0], tickers[1]
    first_context = _run_tool_loop(run_result, first, "summary")
    second_context = _run_tool_loop(run_result, second, "summary")
    first_rec = first_context.get("recommendation")
    second_rec = second_context.get("recommendation")
    first_status = first_context.get("status")
    second_status = second_context.get("status")
    first_tech = first_context.get("technical")
    second_tech = second_context.get("technical")

    if first_rec is None or second_rec is None:
        return "Nao encontrei contexto suficiente para comparar esses tickers nesta execucao."

    stronger = _pick_stronger_signal(first_rec, second_rec)
    stronger_context = first_context if stronger == first else second_context
    stronger_reason = _comparison_reason(stronger, stronger_context)

    return (
        f"Comparando {first} e {second}:\n\n"
        f"{first}: {first_rec['recomendacao']} com confianca de {first_rec['confianca']:.0%}, "
        f"MACD em {first_tech['macd_signal'] if first_tech else 'indefinido'} e sentimento {_describe_news_sentiment(first_status)}.\n"
        f"{second}: {second_rec['recomendacao']} com confianca de {second_rec['confianca']:.0%}, "
        f"MACD em {second_tech['macd_signal'] if second_tech else 'indefinido'} e sentimento {_describe_news_sentiment(second_status)}.\n\n"
        f"Sinal mais convicto agora: {stronger}. {stronger_reason}"
    )


def _build_news_clause(status: dict | None, news: dict | None) -> str:
    if status is None:
        return "Nao houve contexto de status suficiente para qualificar o bloco de noticias."
    if status["matched_news_count"] == 0:
        return "Nao houve noticias casadas relevantes nesta execucao, entao o peso maior ficou no tecnico."

    sentiment_text = _describe_news_sentiment(status)
    examples = _format_news_examples(news, limit=2)
    return (
        f"No noticiario, houve {status['matched_news_count']} item(ns) relevante(s) e o saldo agregado esta {sentiment_text}, "
        f"com impacto medio de {status['avg_impact_score']:.2f}. Exemplos para leitura: {examples}."
    )


def _format_news_examples(news: dict | None, limit: int = 2) -> str:
    if news is None or not news.get("top_noticias"):
        return "nenhum destaque disponivel"

    examples = []
    for item in news["top_noticias"][:limit]:
        title = item["titulo"]
        source = item["fonte"]
        impact = item["impacto"]
        url = (item.get("url") or "").strip()
        if url:
            examples.append(f"[{title}]({url}) ({source}, impacto {impact:.2f})")
        else:
            examples.append(f"{title} ({source}, impacto {impact:.2f})")
    return "; ".join(examples)


def _describe_news_sentiment(status: dict | None) -> str:
    if status is None:
        return "indefinido"

    score = status["news_sentiment_score"]
    if score >= 0.25:
        return "positivo"
    if score <= -0.25:
        return "negativo"
    return "neutro"


def _describe_macd(value: str) -> str:
    mapping = {
        "alta": "vies de alta",
        "baixa": "vies de baixa",
        "neutro": "falta de direcao clara",
    }
    return mapping.get((value or "").strip().lower(), "falta de direcao clara")


def _describe_rsi(value: float) -> str:
    if value < 40:
        return "um ativo mais pressionado, com espaco para recuperacao se o fluxo melhorar"
    if value > 60:
        return "uma leitura mais esticada, com menos folga para continuar subindo sem pausa"
    return "um equilibrio, sem extremo tecnico claro"


def _technical_risk(macd_signal: str, rsi: float) -> str:
    if (macd_signal or "").strip().lower() == "alta" and rsi < 40:
        return "O tecnico ainda depende da continuidade da recuperacao; se ela falhar, o sinal enfraquece rapido."
    if (macd_signal or "").strip().lower() == "baixa" and rsi > 60:
        return "O tecnico esta sensivel a uma reversao curta; qualquer alivio pode reduzir a conviccao da venda."
    return "Os indicadores nao estao em extremo, entao pequenas mudancas no preco ja podem alterar a leitura do modelo."


def _news_risk(status: dict | None) -> str:
    if status is None or status["matched_news_count"] == 0:
        return "Como quase nao houve noticias casadas, o modelo esta mais exposto a surpresa informacional fora da amostra."
    if status["avg_impact_score"] >= 0.7:
        return "As noticias do dia tiveram impacto alto, entao uma manchete contraria tende a mexer mais no sinal."
    return "O bloco de noticias nao esta extremo, mas pode virar rapidamente se o sentimento mudar de neutro para negativo ou positivo."


def _extract_requested_recommendation(question: str) -> str | None:
    if "vender" in question:
        return "VENDER"
    if "comprar" in question:
        return "COMPRAR"
    if "aguardar" in question:
        return "AGUARDAR"
    return None


def _default_change_target(current: str) -> str:
    if current == "COMPRAR":
        return "VENDER"
    if current == "VENDER":
        return "COMPRAR"
    return "AGUARDAR"


def _conditions_for_opposite(current: str) -> str:
    if current == "COMPRAR":
        return "o MACD virar para baixa, o RSI passar de 60 e/ou o consenso de noticias ficar negativo"
    if current == "VENDER":
        return "o MACD virar para alta, o RSI cair abaixo de 40 e/ou o consenso de noticias melhorar para positivo"
    return "tecnico e noticias passarem a apontar juntos para compra ou venda"


def _format_evidence_highlights(evidence: dict) -> str:
    if not evidence:
        return ""

    technical_factors = evidence.get("technical_factors", [])
    news_factors = evidence.get("news_factors", [])
    selected = technical_factors[:1] + news_factors[:1]
    return "; ".join(selected)


def _format_signal_breakers(signal_breakers: list[str]) -> str:
    if not signal_breakers:
        return ""
    return ", ".join(signal_breakers)


def _pick_stronger_signal(first_rec: dict, second_rec: dict) -> str:
    first_key = (_recommendation_rank(first_rec["recomendacao"]), float(first_rec["confianca"]))
    second_key = (_recommendation_rank(second_rec["recomendacao"]), float(second_rec["confianca"]))
    return first_rec["ticker"] if first_key >= second_key else second_rec["ticker"]


def _recommendation_rank(value: str) -> int:
    if value in {"COMPRAR", "VENDER"}:
        return 2
    return 1


def _comparison_reason(ticker: str, context: dict) -> str:
    rec = context.get("recommendation") or {}
    tech = context.get("technical") or {}
    status = context.get("status") or {}
    evidence_text = _format_evidence_highlights(rec.get("evidencias", {}))
    return (
        f"{ticker} combina {rec.get('recomendacao', 'sinal indefinido')} com confianca de {rec.get('confianca', 0):.0%}, "
        f"MACD em {tech.get('macd_signal', 'indefinido')}, sentimento {_describe_news_sentiment(status)} "
        f"e evidencias como {evidence_text or 'fatores ainda limitados nesta execucao'}."
    )
