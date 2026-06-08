from __future__ import annotations

from dataclasses import asdict
import re
import time
from typing import Any

from app.config.settings import settings
from app.domain.models import NewsSignal, Recommendation, TechnicalSnapshot
from app.tools.market_tool import get_technical_snapshot
from app.tools.news_tool import get_news_analysis, summarize_news_events
from openai import AzureOpenAI

try:
    from langchain_core.tools import StructuredTool

    LANGCHAIN_AVAILABLE = True
except Exception:
    StructuredTool = None
    LANGCHAIN_AVAILABLE = False


def search_news(ticker: str, data_mode: str = "mock") -> dict[str, Any]:
    """Busca noticias do ticker e resume o sinal de sentimento do ciclo."""
    signal, status, notes, matched, items = get_news_analysis(ticker=ticker, data_mode=data_mode)
    return {
        "ticker": ticker,
        "signal": asdict(signal),
        "status": status,
        "notes": notes,
        "matched": matched,
        "summary": summarize_news_events(ticker=ticker, items=items),
        "items": [asdict(item) for item in items],
    }


def get_price_data(ticker: str, period: str | None = None, data_mode: str = "mock") -> dict[str, Any]:
    """Coleta snapshot tecnico de preco para o ticker informado."""
    snapshot = get_technical_snapshot(ticker=ticker, data_mode=data_mode)
    return {
        "ticker": ticker,
        "period": period or settings.app_market_period,
        "snapshot": asdict(snapshot),
    }


def calculate_indicators(data: dict[str, Any]) -> dict[str, Any]:
    """Extrai os indicadores tecnicos essenciais do snapshot de mercado."""
    snap = data.get("snapshot", {})
    return {
        "ticker": str(snap.get("ticker", "")),
        "close": float(snap.get("close", 0.0)),
        "rsi": float(snap.get("rsi", 50.0)),
        "macd_signal": str(snap.get("macd_signal", "neutral")),
    }


def generate_recommendation(analysis: dict[str, Any]) -> dict[str, Any]:
    """Valida e normaliza o payload de analise para etapa de decisao da LLM."""
    # Tool de contrato: valida entradas para decisao no passo de LLM.
    technical = analysis.get("technical", {})
    signal = analysis.get("news_signal", {})
    return {
        "ticker": str(analysis.get("ticker", technical.get("ticker", ""))),
        "technical": {
            "close": float(technical.get("close", 0.0)),
            "rsi": float(technical.get("rsi", 50.0)),
            "macd_signal": str(technical.get("macd_signal", "neutral")),
        },
        "news_signal": {
            "positive": int(signal.get("positive", 0)),
            "negative": int(signal.get("negative", 0)),
            "neutral": int(signal.get("neutral", 0)),
            "consensus": str(signal.get("consensus", "neutral")),
        },
    }


class LangChainInvestmentAgent:
    """Executor de tools com contrato de agente via LangChain para Sprint 3."""

    def __init__(self, data_mode: str = "mock") -> None:
        self.data_mode = data_mode
        self._azure_client = self._build_azure_client()
        self.tool_names = [
            "search_news",
            "get_price_data",
            "calculate_indicators",
            "generate_recommendation",
        ]
        self.tools = self._build_tools()

    def _build_azure_client(self) -> AzureOpenAI | None:
        endpoint = (settings.azure_openai_endpoint or "").strip()
        api_key = (settings.azure_openai_api_key or "").strip()
        api_version = (settings.azure_openai_api_version or "").strip()
        if not endpoint or not api_key or not api_version:
            return None

        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

    def _llm_reflection(self, ticker: str, technical: dict[str, Any], news_signal: dict[str, Any], action: str) -> tuple[str, str]:
        if self._azure_client is None:
            raise RuntimeError(
                "Azure OpenAI indisponivel para reflexao. Configure AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION e deployment valido."
            )

        prompt_usuario = (
            f"Ticker: {ticker}\n"
            f"Fechamento: {technical.get('close')}\n"
            f"RSI: {technical.get('rsi')}\n"
            f"MACD signal: {technical.get('macd_signal')}\n"
            f"Noticias positivas: {news_signal.get('positive')}\n"
            f"Noticias negativas: {news_signal.get('negative')}\n"
            f"Noticias neutras: {news_signal.get('neutral')}\n"
            f"Consenso de noticias: {news_signal.get('consensus')}\n"
            f"Recomendacao preliminar: {action}\n\n"
            "Responda em portugues do Brasil com ate 2 frases curtas explicando por que essa recomendacao faz sentido neste ciclo."
        )

        try:
            response = self._azure_client.chat.completions.create(
                model=settings.azure_openai_deployment_trading,
                messages=[
                    {
                        "role": "system",
                        "content": "Voce e um analista financeiro objetivo. Nao invente dados e nao de conselho definitivo.",
                    },
                    {"role": "user", "content": prompt_usuario},
                ],
                temperature=0.1,
                max_completion_tokens=180,
            )
            text = (response.choices[0].message.content or "").strip()
            return text, "azure_openai"
        except Exception as exc:
            raise RuntimeError(f"Falha na reflexao via Azure OpenAI: {exc}") from exc

    def _parse_llm_decision(self, content: str) -> tuple[str, float, str, list[str]] | None:
        text = (content or "").strip()
        if not text:
            return None

        action_match = re.search(r"RECOMMENDATION\s*:\s*(COMPRAR|VENDER|AGUARDAR)", text, flags=re.IGNORECASE)
        confidence_match = re.search(r"CONFIDENCE\s*:\s*([0-9]*\.?[0-9]+)", text, flags=re.IGNORECASE)
        rationale_match = re.search(r"RATIONALE\s*:\s*(.+)", text, flags=re.IGNORECASE)
        breakers_match = re.search(r"SIGNAL_BREAKERS\s*:\s*(.+)", text, flags=re.IGNORECASE)

        if action_match is None:
            return None

        action = action_match.group(1).upper()
        confidence = 0.7
        if confidence_match is not None:
            try:
                confidence = float(confidence_match.group(1))
            except Exception:
                confidence = 0.7
        confidence = max(0.0, min(1.0, confidence))

        rationale = "Decisao gerada pelo LLM com base em tecnico e noticias do ciclo."
        if rationale_match is not None:
            rationale = rationale_match.group(1).strip()

        signal_breakers: list[str] = []
        if breakers_match is not None:
            raw = breakers_match.group(1)
            parts = [item.strip(" -") for item in raw.split(";")]
            signal_breakers = [item for item in parts if item]

        return action, confidence, rationale, signal_breakers

    def _llm_decide_recommendation(self, ticker: str, technical: dict[str, Any], news_signal: dict[str, Any]) -> tuple[Recommendation | None, str]:
        if self._azure_client is None:
            raise RuntimeError(
                "Azure OpenAI indisponivel para decisao. Configure AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION e deployment valido."
            )

        prompt_usuario = (
            "Voce deve decidir entre COMPRAR, VENDER ou AGUARDAR para um unico ticker com base nos dados abaixo.\n"
            "Dados tecnicos e noticias:\n"
            f"Ticker: {ticker}\n"
            f"Fechamento: {technical.get('close')}\n"
            f"RSI: {technical.get('rsi')}\n"
            f"MACD signal: {technical.get('macd_signal')}\n"
            f"Noticias positivas: {news_signal.get('positive')}\n"
            f"Noticias negativas: {news_signal.get('negative')}\n"
            f"Noticias neutras: {news_signal.get('neutral')}\n"
            f"Consenso noticias: {news_signal.get('consensus')}\n\n"
            "Responda EXATAMENTE nestas 4 linhas e no mesmo formato:\n"
            "RECOMMENDATION: COMPRAR|VENDER|AGUARDAR\n"
            "CONFIDENCE: numero entre 0 e 1\n"
            "RATIONALE: justificativa curta em portugues\n"
            "SIGNAL_BREAKERS: item1; item2; item3\n"
        )

        try:
            response = self._azure_client.chat.completions.create(
                model=settings.azure_openai_deployment_trading,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Voce e um analista financeiro objetivo. Nao invente dados. "
                            "Retorne somente os 4 campos no formato solicitado."
                        ),
                    },
                    {"role": "user", "content": prompt_usuario},
                ],
                temperature=0.1,
                max_completion_tokens=220,
            )
            content = (response.choices[0].message.content or "").strip()
            parsed = self._parse_llm_decision(content)
            if parsed is None:
                raise RuntimeError("Falha ao interpretar resposta de decisao da LLM (parse invalido).")

            action, confidence, rationale, signal_breakers = parsed
            recommendation = Recommendation(
                ticker=ticker,
                recommendation=action,
                confidence=round(confidence, 2),
                rationale=rationale,
                generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                evidence={
                    "signal_breakers": signal_breakers,
                    "llm_decision_raw": content,
                },
            )
            return recommendation, "azure_openai"
        except Exception as exc:
            raise RuntimeError(f"Falha na decisao via Azure OpenAI: {exc}") from exc

    def _build_tools(self) -> list[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []

        return [
            StructuredTool.from_function(
                search_news,
                name="search_news",
                description="Busca noticias de um ticker e retorna sinal consolidado de sentimento.",
            ),
            StructuredTool.from_function(
                get_price_data,
                name="get_price_data",
                description="Coleta snapshot tecnico de preco para um ticker.",
            ),
            StructuredTool.from_function(
                calculate_indicators,
                name="calculate_indicators",
                description="Extrai indicadores tecnicos essenciais a partir de um snapshot.",
            ),
            StructuredTool.from_function(
                generate_recommendation,
                name="generate_recommendation",
                description="Normaliza a analise final para a etapa de decisao da LLM.",
            ),
        ]

    def run_for_snapshot(self, snapshot: TechnicalSnapshot) -> dict[str, Any]:
        ticker = snapshot.ticker
        tool_trace: list[str] = []
        react_trace: list[dict[str, str]] = []
        started_at = time.time()

        price_data = get_price_data(ticker=ticker, period=settings.app_market_period, data_mode=self.data_mode)
        tool_trace.append("get_price_data")
        react_trace.append(
            {
                "thought": f"Preciso consolidar os dados de preco e volume de {ticker}.",
                "action": "get_price_data",
                "observation": f"Dados de mercado coletados para periodo {price_data.get('period')}",
            }
        )

        technical = calculate_indicators(price_data)
        tool_trace.append("calculate_indicators")
        react_trace.append(
            {
                "thought": "Com os dados de mercado em maos, calculo os indicadores tecnicos do ciclo.",
                "action": "calculate_indicators",
                "observation": (
                    f"Indicadores: RSI={technical.get('rsi')}, MACD signal={technical.get('macd_signal')}"
                ),
            }
        )

        news_data = search_news(ticker=ticker, data_mode=self.data_mode)
        tool_trace.append("search_news")
        react_trace.append(
            {
                "thought": "Agora avalio o contexto de noticias e sentimento para reduzir vies tecnico isolado.",
                "action": "search_news",
                "observation": (
                    f"Noticias casadas={news_data.get('matched')}, status={news_data.get('status')}"
                ),
            }
        )

        llm_recommendation, llm_decision_source = self._llm_decide_recommendation(
            ticker=ticker,
            technical=technical,
            news_signal=news_data["signal"],
        )

        _ = generate_recommendation(
            {
                "ticker": ticker,
                "technical": technical,
                "news_signal": news_data["signal"],
            }
        )
        tool_trace.append("generate_recommendation")
        recommendation = llm_recommendation
        react_trace.append(
            {
                "thought": "Combino sinal tecnico e noticias e deixo o LLM decidir a acao final.",
                "action": "generate_recommendation",
                "observation": (
                    f"Recomendacao preliminar={recommendation.recommendation}; "
                    f"fonte_decisao={llm_decision_source}"
                ),
            }
        )

        llm_reflection, llm_source = self._llm_reflection(
            ticker=ticker,
            technical=technical,
            news_signal=news_data["signal"],
            action=recommendation.recommendation,
        )
        react_trace.append(
            {
                "thought": "Faço uma reflexao final com LLM para explicabilidade do ciclo.",
                "action": "llm_reflection",
                "observation": llm_reflection or "Sem reflexao LLM para este ciclo.",
            }
        )

        elapsed_ms = int((time.time() - started_at) * 1000)
        recommendation.evidence = {
            **recommendation.evidence,
            "tool_trace": tool_trace,
            "agent_framework": "langchain" if LANGCHAIN_AVAILABLE else "langchain_fallback",
            "react_trace": react_trace,
            "llm_decision_source": llm_decision_source,
            "llm_reflection": llm_reflection,
            "llm_source": llm_source,
            "llm_inputs": {
                "technical": technical,
                "news_signal": news_data["signal"],
            },
            "legacy_scores_not_applicable": True,
            "legacy_scores_reason": "Modo de decisao atual e 100% LLM; score tecnico/noticias do motor antigo nao e calculado.",
            "execution_ms": elapsed_ms,
        }

        signal = NewsSignal(**news_data["signal"])
        return {
            "recommendation": recommendation,
            "news_signal": signal,
            "news_status": str(news_data["status"]),
            "news_notes": str(news_data["notes"]),
            "matched_news_count": int(news_data["matched"]),
            "news_summary": str(news_data["summary"]),
            "news_items": list(news_data["items"]),
        }
