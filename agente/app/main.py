import sys
from pathlib import Path

import streamlit as st

# Garantia de import absoluto do pacote app ao executar via "streamlit run app/main.py".
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import settings
from app.pipelines.run_analysis import run_pipeline_with_details
from app.storage.json_store import (
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


st.set_page_config(page_title="Projeto Agente - Sprint 1", page_icon="📈", layout="wide")
st.title("Projeto Agente - Sprint 1")
st.caption("Pipeline unico com disparo on-demand/agendavel, com dados mock ou reais e fallback seguro.")

left, right = st.columns(2)

with left:
    execution_mode = st.selectbox("Modo de execucao", ["on_demand", "scheduled"], index=0)
    data_mode = st.selectbox("Modo de dados", ["mock", "real"], index=0)

with right:
    scope = st.selectbox("Escopo", ["all", "single"], index=0)
    one_ticker = st.selectbox("Ticker (quando escopo = single)", ["VALE3", "PETR4", "BBAS3", "ITUB4"], index=0)

if st.button("Executar pipeline"):
    tickers = _resolve_tickers(scope, one_ticker)
    result = run_pipeline_with_details(
        tickers=tickers,
        execution_mode=execution_mode,
        data_mode=data_mode,
    )

    append_recommendations("data/recommendations.json", result.recommendations)
    append_technical_snapshots("data/technical_snapshots.json", result.technical_snapshots)
    append_technical_history("data/technical_history.json", result.technical_history)
    append_ticker_statuses("data/ticker_statuses.json", result.ticker_statuses)

    st.success(f"Pipeline executado para {len(tickers)} ticker(s).")
    rec_rows = []
    for r in result.recommendations:
        row = r.__dict__.copy()
        row["tradingview_url"] = _tradingview_symbol_url(r.ticker)
        rec_rows.append(row)

    st.dataframe(
        rec_rows,
        use_container_width=True,
        column_config={
            "tradingview_url": st.column_config.LinkColumn("TradingView", display_text="Abrir"),
        },
    )

    with st.expander("Status por ticker"):
        st.dataframe([s.__dict__ for s in result.ticker_statuses], use_container_width=True)

    st.caption(
        "Resultados adicionados em data/recommendations.json, data/technical_snapshots.json, "
        "data/technical_history.json e data/ticker_statuses.json"
    )
