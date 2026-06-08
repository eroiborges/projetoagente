import sys
import time
import json
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# Garantia de import absoluto do pacote app ao executar via "streamlit run app/main.py".
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import settings
from app.agents.explainer_agent import explain_question, get_agent_system_prompt
from app.pipelines.run_analysis import run_pipeline_with_details
from app.tools.backtest_tool import run_backtest_from_files
from app.storage.json_store import (
    append_daily_analysis,
    append_news_items,
    append_recommendation_records,
    append_recommendations,
    append_technical_history,
    append_technical_snapshots,
    append_ticker_statuses,
)


MONITOR_STATE_PATH = Path("data/monitor_state.json")


def _configured_default_data_mode() -> str:
    raw = (settings.app_default_data_mode or "").strip().lower()
    return raw if raw in {"mock", "real"} else "mock"


def _configured_default_execution_mode() -> str:
    raw = (settings.app_default_execution_mode or "").strip().lower()
    return raw if raw in {"on_demand", "scheduled"} else "on_demand"


def _configured_tickers() -> list[str]:
    tickers = [t.strip().upper() for t in settings.app_default_tickers.split(",") if t.strip()]
    return tickers or ["VALE3", "PETR4", "BBAS3", "ITUB4"]


def _configured_default_one_ticker() -> str:
    return _configured_tickers()[0]


def _default_monitor_state() -> dict[str, object]:
    return {
        "monitoramento_ativo": False,
        "monitoramento_intervalo_min": 5,
        "monitoramento_ultima_execucao": 0.0,
        "monitoramento_proxima_execucao": 0.0,
        "monitoramento_scope": "all",
        "monitoramento_one_ticker": _configured_default_one_ticker(),
        "monitoramento_data_mode": _configured_default_data_mode(),
    }


def _load_monitor_state() -> dict[str, object]:
    default = _default_monitor_state()
    if not MONITOR_STATE_PATH.exists():
        return default

    try:
        loaded = json.loads(MONITOR_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return default

    if not isinstance(loaded, dict):
        return default
    return {**default, **loaded}


def _save_monitor_state(state: dict[str, object]) -> None:
    MONITOR_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MONITOR_STATE_PATH.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")


def _session_monitor_state() -> dict[str, object]:
    return {
        "monitoramento_ativo": bool(st.session_state.get("monitoramento_ativo", False)),
        "monitoramento_intervalo_min": int(st.session_state.get("monitoramento_intervalo_min", 5)),
        "monitoramento_ultima_execucao": float(st.session_state.get("monitoramento_ultima_execucao", 0.0)),
        "monitoramento_proxima_execucao": float(st.session_state.get("monitoramento_proxima_execucao", 0.0)),
        "monitoramento_scope": str(st.session_state.get("monitoramento_scope", "all")),
        "monitoramento_one_ticker": str(
            st.session_state.get("monitoramento_one_ticker", _configured_default_one_ticker())
        ),
        "monitoramento_data_mode": str(
            st.session_state.get("monitoramento_data_mode", _configured_default_data_mode())
        ),
    }


def _apply_monitor_state_to_session(state: dict[str, object]) -> None:
    st.session_state["monitoramento_ativo"] = bool(state.get("monitoramento_ativo", False))
    st.session_state["monitoramento_intervalo_min"] = int(state.get("monitoramento_intervalo_min", 5))
    st.session_state["monitoramento_ultima_execucao"] = float(state.get("monitoramento_ultima_execucao", 0.0))
    st.session_state["monitoramento_proxima_execucao"] = float(state.get("monitoramento_proxima_execucao", 0.0))
    st.session_state["monitoramento_scope"] = str(state.get("monitoramento_scope", "all"))
    st.session_state["monitoramento_one_ticker"] = str(
        state.get("monitoramento_one_ticker", _configured_default_one_ticker())
    )
    st.session_state["monitoramento_data_mode"] = str(
        state.get("monitoramento_data_mode", _configured_default_data_mode())
    )


def _resolve_tickers(scope: str, one_ticker: str) -> list[str]:
    all_tickers = _configured_tickers()
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


def _format_evidence_rows(recommendations: list[object]) -> list[dict]:
    rows: list[dict] = []
    for rec in recommendations:
        evidence = dict(getattr(rec, "evidence", {}) or {})
        react_trace = evidence.get("react_trace", [])
        rows.append(
            {
                "Ticker": rec.ticker,
                "Recomendacao": rec.recommendation,
                "Fonte decisao": evidence.get("llm_decision_source", "n/d"),
                "Fonte reflexao": evidence.get("llm_source", "n/d"),
                "Framework agente": evidence.get("agent_framework", "n/d"),
                "Tools executadas": ", ".join(evidence.get("tool_trace", [])) if evidence.get("tool_trace") else "n/d",
                "Passos ReAct": len(react_trace) if isinstance(react_trace, list) else 0,
                "Tempo execucao (ms)": evidence.get("execution_ms", 0),
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
                "Resumo noticias": s.news_summary,
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
                "Buy-and-Hold medio (%)": round(float(metrics["avg_buy_hold_return"]) * 100, 2),
                "Alpha medio vs Buy-and-Hold (%)": round(float(metrics["avg_alpha_vs_buy_hold"]) * 100, 2),
            }
        )
    return rows


def _format_backtest_diagnostic_message(diagnostics: dict[str, int]) -> str:
    records_total = int(diagnostics.get("records_total", 0))
    records_in_window = int(diagnostics.get("records_in_window", 0))
    records_after_dedup = int(diagnostics.get("records_after_dedup", records_in_window))
    duplicate_same_day_discarded = int(diagnostics.get("duplicate_same_day_discarded", 0))
    rows_generated = int(diagnostics.get("rows_generated", 0))
    missing_history_group = int(diagnostics.get("missing_history_group", 0))
    missing_entry_or_next = int(diagnostics.get("missing_entry_or_next", 0))
    entry_close_zero = int(diagnostics.get("entry_close_zero", 0))

    return (
        "Diagnostico do backtest na janela selecionada. "
        f"Sinais totais: {records_total}; sinais na janela: {records_in_window}; "
        f"sinais apos deduplicacao por ticker+data: {records_after_dedup}; "
        f"duplicados descartados (mesmo ticker+data): {duplicate_same_day_discarded}; "
        f"linhas geradas: {rows_generated}. "
        f"Sem historico por ticker/modo: {missing_history_group}; "
        f"sem preco de entrada ou D+1: {missing_entry_or_next}; "
        f"entrada com preco zero: {entry_close_zero}."
    )


def _persist_result(result: object) -> None:
    append_recommendations("data/recommendations.json", result.recommendations)
    append_recommendation_records("data/recommendation_records.json", result.recommendation_records)
    append_daily_analysis("data/daily_analysis.json", result.daily_analysis)
    append_technical_snapshots("data/technical_snapshots.json", result.technical_snapshots)
    append_technical_history("data/technical_history.json", result.technical_history)
    append_news_items("data/news_items.json", result.news_items)
    append_ticker_statuses("data/ticker_statuses.json", result.ticker_statuses)


def _execute_pipeline(tickers: list[str], execution_mode: str, data_mode: str, one_ticker: str) -> object:
    result = run_pipeline_with_details(
        tickers=tickers,
        execution_mode=execution_mode,
        data_mode=data_mode,
    )
    _persist_result(result)
    st.session_state["last_result"] = result
    st.session_state["last_ticker"] = one_ticker
    return result


def _inject_auto_refresh(interval_seconds: int) -> None:
    components.html(
        f"""
        <script>
            setTimeout(function() {{
                window.parent.location.reload();
            }}, {int(interval_seconds * 1000)});
        </script>
        """,
        height=0,
    )


st.set_page_config(page_title="Projeto Agente - Entrega Final", page_icon="📈", layout="wide")
st.title("Projeto Agente - Entrega Final")
st.caption("Pipeline unico com disparo sob demanda/agendado, com dados simulados ou reais e fallback seguro.")

if not st.session_state.get("monitor_state_initialized", False):
    _apply_monitor_state_to_session(_load_monitor_state())
    st.session_state["monitor_state_initialized"] = True

main_col, chat_col = st.columns([2, 1], gap="large")

with main_col:
    left, right = st.columns(2)

    with left:
        execution_mode_options = {
            "Sob demanda": "on_demand",
            "Agendado": "scheduled",
        }
        default_execution_mode = _configured_default_execution_mode()
        execution_mode_default_label = "Agendado" if default_execution_mode == "scheduled" else "Sob demanda"
        execution_mode_labels = list(execution_mode_options.keys())
        execution_mode_label = st.selectbox(
            "Modo de execucao",
            execution_mode_labels,
            index=execution_mode_labels.index(execution_mode_default_label),
        )
        execution_mode = execution_mode_options[execution_mode_label]

        data_mode_options = {
            "Simulado": "mock",
            "Real": "real",
        }
        default_data_mode = _configured_default_data_mode()
        data_mode_labels = list(data_mode_options.keys())
        data_mode_default_label = "Simulado" if default_data_mode == "mock" else "Real"
        data_mode_label = st.selectbox(
            "Modo de dados",
            data_mode_labels,
            index=data_mode_labels.index(data_mode_default_label),
        )
        data_mode = data_mode_options[data_mode_label]

    with right:
        scope_options = {
            "Todos": "all",
            "Unico": "single",
        }
        default_scope = str(st.session_state.get("monitoramento_scope", "all"))
        scope_labels = list(scope_options.keys())
        scope_default_label = "Todos" if default_scope == "all" else "Unico"
        scope_label = st.selectbox("Escopo", scope_labels, index=scope_labels.index(scope_default_label))
        scope = scope_options[scope_label]
        ticker_options = _configured_tickers()
        default_ticker = str(st.session_state.get("monitoramento_one_ticker", _configured_default_one_ticker()))
        ticker_index = ticker_options.index(default_ticker) if default_ticker in ticker_options else 0
        one_ticker = st.selectbox("Ticker (quando escopo = Unico)", ticker_options, index=ticker_index)

    st.markdown("#### Execucao sob demanda")
    st.caption("Executa imediatamente um ciclo unico usando as configuracoes atuais de modo, escopo e ticker.")
    tickers = _resolve_tickers(scope, one_ticker)
    monitoramento_ativo = bool(st.session_state.get("monitoramento_ativo", False))
    if st.button("Executar pipeline", use_container_width=False):
        try:
            _execute_pipeline(tickers=tickers, execution_mode=execution_mode, data_mode=data_mode, one_ticker=one_ticker)
            if monitoramento_ativo:
                intervalo_ref = int(st.session_state.get("monitoramento_intervalo_min", 5))
                ultima = time.time()
                st.session_state["monitoramento_ultima_execucao"] = ultima
                st.session_state["monitoramento_proxima_execucao"] = ultima + intervalo_ref * 60
                _save_monitor_state(_session_monitor_state())
        except Exception as exc:
            st.error(
                "Falha ao executar ou persistir o pipeline. "
                "Verifique os dados e tente novamente. "
                f"Detalhe tecnico: {exc}"
            )

    st.markdown("---")
    monitoramento_ativo = bool(st.session_state.get("monitoramento_ativo", False))
    st.markdown("#### Agendamento de monitoramento")
    st.caption("Defina o intervalo e use o botao ao lado para iniciar ou parar o monitoramento automatico.")

    interval_options = [5, 15, 30]
    current_interval = int(st.session_state.get("monitoramento_intervalo_min", 5))
    interval_index = interval_options.index(current_interval) if current_interval in interval_options else 0
    intervalo_monitoramento = st.selectbox(
        "Intervalo de monitoramento (min)",
        interval_options,
        index=interval_index,
        key="monitoramento_intervalo_selector",
    )
    action_label = "Parar monitoramento" if monitoramento_ativo else "Iniciar monitoramento"
    if st.button(action_label, use_container_width=True):
        if monitoramento_ativo:
            st.session_state["monitoramento_ativo"] = False
        else:
            st.session_state["monitoramento_ativo"] = True
            st.session_state["monitoramento_intervalo_min"] = int(intervalo_monitoramento)
            st.session_state["monitoramento_ultima_execucao"] = 0.0
            st.session_state["monitoramento_proxima_execucao"] = time.time()
            st.session_state["monitoramento_scope"] = scope
            st.session_state["monitoramento_one_ticker"] = one_ticker
            st.session_state["monitoramento_data_mode"] = data_mode
        _save_monitor_state(_session_monitor_state())

    monitoramento_ativo = bool(st.session_state.get("monitoramento_ativo", False))
    intervalo_atual = int(st.session_state.get("monitoramento_intervalo_min", int(intervalo_monitoramento)))
    agora = time.time()

    if monitoramento_ativo and intervalo_atual != int(intervalo_monitoramento):
        st.session_state["monitoramento_intervalo_min"] = int(intervalo_monitoramento)
        intervalo_atual = int(intervalo_monitoramento)
        proxima_base = st.session_state.get("monitoramento_ultima_execucao", 0.0) or agora
        st.session_state["monitoramento_proxima_execucao"] = proxima_base + intervalo_atual * 60
        _save_monitor_state(_session_monitor_state())

    monitor_scope = str(st.session_state.get("monitoramento_scope", scope))
    monitor_one_ticker = str(st.session_state.get("monitoramento_one_ticker", one_ticker))
    monitor_data_mode = str(st.session_state.get("monitoramento_data_mode", data_mode))
    tickers = _resolve_tickers(scope, one_ticker)
    if monitoramento_ativo:
        tickers_monitoramento = _resolve_tickers(monitor_scope, monitor_one_ticker)
        proxima_execucao = float(st.session_state.get("monitoramento_proxima_execucao", 0.0))
        if proxima_execucao <= 0:
            proxima_execucao = agora
            st.session_state["monitoramento_proxima_execucao"] = proxima_execucao
            _save_monitor_state(_session_monitor_state())

        if agora >= proxima_execucao:
            try:
                _execute_pipeline(
                    tickers=tickers_monitoramento,
                    execution_mode="scheduled",
                    data_mode=monitor_data_mode,
                    one_ticker=monitor_one_ticker,
                )
                ultima = time.time()
                st.session_state["monitoramento_ultima_execucao"] = ultima
                st.session_state["monitoramento_proxima_execucao"] = ultima + intervalo_atual * 60
                _save_monitor_state(_session_monitor_state())
            except Exception as exc:
                st.error(f"Falha no ciclo de monitoramento: {exc}")

        ultima_execucao = float(st.session_state.get("monitoramento_ultima_execucao", 0.0))
        proxima_execucao = float(st.session_state.get("monitoramento_proxima_execucao", 0.0))
        ultima_txt = time.strftime("%H:%M:%S", time.localtime(ultima_execucao)) if ultima_execucao else "ainda nao executado"
        proxima_txt = time.strftime("%H:%M:%S", time.localtime(proxima_execucao)) if proxima_execucao else "-"
        st.info(
            f"Monitoramento ativo em sessao. Intervalo: {intervalo_atual} min. "
            f"Ultima execucao: {ultima_txt}. Proxima execucao: {proxima_txt}. "
            f"Escopo: {monitor_scope}. Ticker: {monitor_one_ticker}. Modo dados: {monitor_data_mode}."
        )
        _inject_auto_refresh(5)

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

        with st.expander("Evidencias do agente (por ticker)"):
            st.dataframe(
                _format_evidence_rows(result.recommendations),
                use_container_width=True,
            )
            ticker_options = [rec.ticker for rec in result.recommendations]
            selected_ticker = st.selectbox(
                "Detalhar evidence do ticker",
                ticker_options,
                index=0,
                key="evidence_ticker_select",
            )
            selected_rec = next((rec for rec in result.recommendations if rec.ticker == selected_ticker), None)
            if selected_rec is not None:
                evidence = dict(selected_rec.evidence or {})
                tab_resumo, tab_react, tab_llm, tab_tools = st.tabs(["Resumo", "ReAct", "LLM", "Ferramentas"])

                with tab_resumo:
                    resumo_cols = st.columns(4)
                    resumo_cols[0].metric("Ticker", selected_rec.ticker)
                    resumo_cols[1].metric("Recomendacao", selected_rec.recommendation)
                    resumo_cols[2].metric("Confianca", f"{float(selected_rec.confidence) * 100:.2f}%")
                    resumo_cols[3].metric("Execucao (ms)", int(evidence.get("execution_ms", 0)))
                    st.markdown(f"**Justificativa:** {selected_rec.rationale}")
                    st.caption(
                        f"Fonte decisao: {evidence.get('llm_decision_source', 'n/d')} | "
                        f"Fonte reflexao: {evidence.get('llm_source', 'n/d')} | "
                        f"Framework: {evidence.get('agent_framework', 'n/d')}"
                    )

                with tab_react:
                    react_trace = evidence.get("react_trace", [])
                    if isinstance(react_trace, list) and react_trace:
                        st.json(react_trace)
                    else:
                        st.info("Nao ha trilha ReAct registrada para este ticker.")

                with tab_llm:
                    llm_payload = {
                        "llm_decision_source": evidence.get("llm_decision_source", "n/d"),
                        "llm_source": evidence.get("llm_source", "n/d"),
                        "llm_reflection": evidence.get("llm_reflection", ""),
                        "llm_decision_raw": evidence.get("llm_decision_raw", ""),
                    }
                    st.json(llm_payload)

                with tab_tools:
                    legacy_not_applicable = bool(evidence.get("legacy_scores_not_applicable", False))
                    tool_payload = {
                        "tool_trace": evidence.get("tool_trace", []),
                        "technical_score": evidence.get("technical_score"),
                        "news_score": evidence.get("news_score"),
                        "total_score": evidence.get("total_score"),
                        "technical_factors": evidence.get("technical_factors", []),
                        "news_factors": evidence.get("news_factors", []),
                        "signal_breakers": evidence.get("signal_breakers", []),
                        "legacy_scores_not_applicable": legacy_not_applicable,
                        "legacy_scores_reason": evidence.get("legacy_scores_reason", ""),
                        "llm_inputs": evidence.get("llm_inputs", {}),
                    }
                    st.json(tool_payload)
                    if legacy_not_applicable:
                        st.info(
                            "Os campos technical_score/news_score/total_score pertencem ao motor legado de score. "
                            "No modo atual (decisao 100% LLM), eles nao sao calculados e podem aparecer como null."
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
            "data/daily_analysis.json, data/technical_snapshots.json, data/technical_history.json, "
            "data/news_items.json e data/ticker_statuses.json"
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
                metric_cols = st.columns(6)
                metric_cols[0].metric("Sinais", int(summary["total_signals"]))
                metric_cols[1].metric("Sinais avaliados", int(summary["evaluated_signals"]))
                metric_cols[2].metric("Acertos", int(summary["hits"]))
                metric_cols[3].metric("Taxa de acerto", f"{float(summary['hit_rate']) * 100:.2f}%")
                metric_cols[4].metric("Retorno medio estrategia", f"{float(summary['avg_strategy_return']) * 100:.2f}%")
                metric_cols[5].metric("Retorno medio Buy-and-Hold", f"{float(summary['avg_buy_hold_return']) * 100:.2f}%")
                st.caption(f"Alpha medio vs Buy-and-Hold: {float(summary['avg_alpha_vs_buy_hold']) * 100:.2f}%")

                metrics_report = backtest_result.get("metrics_report", {})
                with st.expander("Relatorio consolidado de metricas"):
                    st.json(metrics_report)

                with st.expander("Diagnostico do backtest"):
                    st.info(_format_backtest_diagnostic_message(diagnostics))
                    st.json(diagnostics)

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
            try:
                answer = explain_question(
                    question=user_question,
                    run_result=st.session_state["last_result"],
                    default_ticker=st.session_state.get("last_ticker", ""),
                )
            except Exception as exc:
                answer = (
                    "Erro ao gerar explicacao via LLM. "
                    "Corrija a configuracao/conectividade do Azure OpenAI e tente novamente. "
                    f"Detalhe: {exc}"
                )
            st.session_state["chat_messages"] = [
                {"role": "user", "content": user_question},
                {"role": "assistant", "content": answer},
            ]
            st.rerun()
