import sys
from datetime import date
from pathlib import Path

import streamlit as st

# Garantia de import absoluto do pacote app ao executar via "streamlit run app/main.py".
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import settings
from app.agents.explainer_agent import explain_question, get_agent_system_prompt
from app.pipelines.run_analysis import run_pipeline_with_details
from app.tools.backtest_tool import run_backtest_from_files
from app.storage.json_store import (
    append_news_items,
    append_recommendation_records,
    append_recommendations,
    append_technical_history,
    append_technical_snapshots,
    append_ticker_statuses,
)


def _resolve_tickers(scope: str, one_ticker: str) -> list[str]:
    all_tickers = [t.strip() for t in settings.app_default_tickers.split(",") if t.strip()]
    if scope == "single":
        return [one_ticker]
    return all_tickers


def _tradingview_symbol_url(ticker: str) -> str:
    base = settings.app_tradingview_symbol_base.rstrip("/-")
    return f"{base}-{ticker.strip().upper()}/"


def _translate_status(value: str) -> str:
    mapping = {
        "ok_real": "OK (real)",
        "ok_mock": "OK (mock)",
        "warning_real_partial": "Aviso (real parcial)",
        "warning_real_no_match": "Aviso (sem correspondencia)",
        "error_real_fallback": "Erro (fallback)",
        "error_mock_fallback": "Erro (fallback)",
    }
    return mapping.get(value, value)


def _translate_note(value: str) -> str:
    mapping = {
        "live_feeds": "fontes ao vivo",
        "mock_data": "dados mock",
        "all_sources_failed": "todas as fontes falharam",
        "no_matching_news": "nenhuma noticia correspondente",
        "news_exception_fallback": "falha na coleta de noticias (fallback)",
    }
    if value.startswith("failed_sources="):
        return value.replace("failed_sources=", "fontes com falha=")
    return mapping.get(value, value)


def _format_recommendation_rows(recommendations: list[object]) -> list[dict]:
    rows: list[dict] = []
    for r in recommendations:
        rows.append(
            {
                "Ticker": r.ticker,
                "Recomendacao": r.recommendation,
                "Confianca": round(float(r.confidence) * 100, 2),
                "Justificativa": r.rationale,
                "Gerado em": r.generated_at,
                "TradingView": _tradingview_symbol_url(r.ticker),
            }
        )
    return rows


def _format_status_rows(statuses: list[object]) -> list[dict]:
    rows: list[dict] = []
    for s in statuses:
        rows.append(
            {
                "Ticker": s.ticker,
                "Status mercado": _translate_status(s.market_status),
                "Status noticias": _translate_status(s.news_status),
                "Observacoes": _translate_note(s.notes),
                "Noticias casadas": s.matched_news_count,
                "Score sentimento (%)": round(float(s.news_sentiment_score) * 100, 2),
                "Impacto medio (%)": round(float(s.avg_impact_score) * 100, 2),
            }
        )
    return rows


def _get_recommendation_for_ticker(recommendations: list[object], ticker: str) -> str | None:
    current_ticker = (ticker or "").strip().upper()
    rec = next((item for item in recommendations if item.ticker == current_ticker), None)
    if rec is None:
        return None
    return rec.recommendation


def _suggest_chat_prompts(recommendation: str | None, ticker: str) -> list[str]:
    current_ticker = (ticker or "").strip().upper()
    if not current_ticker:
        return []

    opposite = {
        "COMPRAR": "VENDER",
        "VENDER": "COMPRAR",
        "AGUARDAR": "COMPRAR",
    }.get((recommendation or "").strip().upper(), "COMPRAR")

    current_label = (recommendation or "recomendacao atual").strip().upper()
    return [
        f"Por que {current_ticker} ficou {current_label}?",
        f"O que teria que acontecer para virar {opposite}?",
        f"Quais riscos dessa recomendacao hoje?",
        f"Resumo de {current_ticker}",
    ]


def _format_backtest_by_ticker_rows(summary: dict[str, dict[str, float | int]]) -> list[dict]:
    rows: list[dict] = []
    for ticker, metrics in sorted(summary.items()):
        rows.append(
            {
                "Ticker": ticker,
                "Sinais": metrics["total_signals"],
                "Sinais avaliados": metrics["evaluated_signals"],
                "Acertos": metrics["hits"],
                "Taxa de acerto (%)": round(float(metrics["hit_rate"]) * 100, 2),
                "Retorno medio (%)": round(float(metrics["avg_strategy_return"]) * 100, 2),
            }
        )
    return rows


def _format_backtest_diagnostic_message(diagnostics: dict[str, int]) -> str:
    records_total = int(diagnostics.get("records_total", 0))
    records_in_window = int(diagnostics.get("records_in_window", 0))
    rows_generated = int(diagnostics.get("rows_generated", 0))
    missing_history_group = int(diagnostics.get("missing_history_group", 0))
    missing_entry_or_next = int(diagnostics.get("missing_entry_or_next", 0))
    entry_close_zero = int(diagnostics.get("entry_close_zero", 0))

    return (
        "Ainda nao ha linhas suficientes para calcular o backtest nesta janela. "
        f"Sinais totais: {records_total}; sinais na janela: {records_in_window}; "
        f"linhas geradas: {rows_generated}. "
        f"Sem historico por ticker/modo: {missing_history_group}; "
        f"sem preco de entrada ou D+1: {missing_entry_or_next}; "
        f"entrada com preco zero: {entry_close_zero}."
    )


st.set_page_config(page_title="Projeto Agente - Entrega Final", page_icon="📈", layout="wide")
st.title("Projeto Agente - Entrega Final")
st.caption("Pipeline unico com disparo sob demanda/agendado, com dados simulados ou reais e fallback seguro.")

main_col, chat_col = st.columns([2, 1], gap="large")

with main_col:
    left, right = st.columns(2)

    with left:
        execution_mode_options = {
            "Sob demanda": "on_demand",
            "Agendado": "scheduled",
        }
        execution_mode_label = st.selectbox("Modo de execucao", list(execution_mode_options.keys()), index=0)
        execution_mode = execution_mode_options[execution_mode_label]

        data_mode_options = {
            "Simulado": "mock",
            "Real": "real",
        }
        data_mode_label = st.selectbox("Modo de dados", list(data_mode_options.keys()), index=0)
        data_mode = data_mode_options[data_mode_label]

    with right:
        scope_options = {
            "Todos": "all",
            "Unico": "single",
        }
        scope_label = st.selectbox("Escopo", list(scope_options.keys()), index=0)
        scope = scope_options[scope_label]
        one_ticker = st.selectbox("Ticker (quando escopo = Unico)", ["VALE3", "PETR4", "BBAS3", "ITUB4"], index=0)

    if st.button("Executar pipeline"):
        tickers = _resolve_tickers(scope, one_ticker)
        try:
            result = run_pipeline_with_details(
                tickers=tickers,
                execution_mode=execution_mode,
                data_mode=data_mode,
            )

            append_recommendations("data/recommendations.json", result.recommendations)
            append_recommendation_records("data/recommendation_records.json", result.recommendation_records)
            append_technical_snapshots("data/technical_snapshots.json", result.technical_snapshots)
            append_technical_history("data/technical_history.json", result.technical_history)
            append_news_items("data/news_items.json", result.news_items)
            append_ticker_statuses("data/ticker_statuses.json", result.ticker_statuses)
            st.session_state["last_result"] = result
            st.session_state["last_ticker"] = one_ticker
        except Exception as exc:
            st.error(
                "Falha ao executar ou persistir o pipeline. "
                "Verifique os dados e tente novamente. "
                f"Detalhe tecnico: {exc}"
            )

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        tickers = _resolve_tickers(scope, one_ticker)
        if not result.recommendations:
            st.warning("A execucao terminou sem recomendacoes para os tickers selecionados.")
            st.stop()
        st.success(f"Pipeline executado para {len(tickers)} ticker(s).")
        rec_rows = _format_recommendation_rows(result.recommendations)
        st.dataframe(
            rec_rows,
            use_container_width=True,
            column_config={
                "Confianca": st.column_config.NumberColumn("Confianca", format="%.2f%%"),
                "TradingView": st.column_config.LinkColumn("TradingView", display_text="Abrir"),
            },
        )

        with st.expander("Status por ticker"):
            st.dataframe(
                _format_status_rows(result.ticker_statuses),
                use_container_width=True,
                column_config={
                    "Score sentimento (%)": st.column_config.NumberColumn("Score sentimento (%)", format="%.2f%%"),
                    "Impacto medio (%)": st.column_config.NumberColumn("Impacto medio (%)", format="%.2f%%"),
                },
            )

        st.caption(
            "Resultados adicionados em data/recommendations.json, data/recommendation_records.json, "
            "data/technical_snapshots.json, data/technical_history.json, data/news_items.json e data/ticker_statuses.json"
        )

        with st.expander("Backtest minimo"):
            backtest_start = st.text_input(
                "Data inicial (YYYY-MM-DD, opcional)",
                value="",
                key="backtest_start_date",
                placeholder="2026-06-01",
            ).strip() or None
            backtest_end = st.text_input(
                "Data final (YYYY-MM-DD, opcional)",
                value="",
                key="backtest_end_date",
                placeholder=str(date.today()),
            ).strip() or None

            backtest_result = run_backtest_from_files(
                "data/recommendation_records.json",
                "data/technical_history.json",
                start_date=backtest_start,
                end_date=backtest_end,
            )
            errors = backtest_result.get("errors", [])
            if errors:
                for item in errors:
                    st.warning(item)
            else:
                summary = backtest_result["summary"]
                diagnostics = backtest_result.get("diagnostics", {})
                metric_cols = st.columns(4)
                metric_cols[0].metric("Sinais", int(summary["total_signals"]))
                metric_cols[1].metric("Sinais avaliados", int(summary["evaluated_signals"]))
                metric_cols[2].metric("Acertos", int(summary["hits"]))
                metric_cols[3].metric("Taxa de acerto", f"{float(summary['hit_rate']) * 100:.2f}%")
                st.caption(f"Retorno medio simples: {float(summary['avg_strategy_return']) * 100:.2f}%")

                if backtest_result["by_ticker"]:
                    st.dataframe(
                        _format_backtest_by_ticker_rows(backtest_result["by_ticker"]),
                        use_container_width=True,
                    )
                else:
                    st.info(_format_backtest_diagnostic_message(diagnostics))

with chat_col:
    st.subheader("Chat com especialista (Agente)")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    if "last_result" not in st.session_state:
        st.info("Rode o pipeline para habilitar perguntas sobre as recomendacoes.")
    else:
        recommendation = _get_recommendation_for_ticker(
            st.session_state["last_result"].recommendations,
            st.session_state.get("last_ticker", ""),
        )
        suggested_prompts = _suggest_chat_prompts(recommendation, st.session_state.get("last_ticker", ""))
        with st.expander("Regras do agente na demo"):
            st.markdown(get_agent_system_prompt())

        if suggested_prompts:
            st.caption("Exemplos de perguntas para esta execucao:")
            st.markdown("\n".join(f"- {prompt}" for prompt in suggested_prompts))
            if len(st.session_state["last_result"].recommendations) >= 2:
                pair = st.session_state["last_result"].recommendations[:2]
                st.markdown(f"- Compare {pair[0].ticker} e {pair[1].ticker}")

        for msg in st.session_state["chat_messages"][-2:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        with st.form("chat_question_form", clear_on_submit=True):
            user_question = st.text_input("Pergunta", placeholder="Pergunte sobre recomendacoes, tecnico ou noticias")
            submitted = st.form_submit_button("Enviar", use_container_width=True)

        if submitted and user_question.strip():
            answer = explain_question(
                question=user_question,
                run_result=st.session_state["last_result"],
                default_ticker=st.session_state.get("last_ticker", ""),
            )
            st.session_state["chat_messages"] = [
                {"role": "user", "content": user_question},
                {"role": "assistant", "content": answer},
            ]
            st.rerun()
