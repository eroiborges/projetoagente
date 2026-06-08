import json
from datetime import date
from pathlib import Path

from app.domain.models import RecommendationRecord, TechnicalHistoryPoint


def load_recommendation_records(path: str) -> list[RecommendationRecord]:
    target = Path(path)
    if not target.exists():
        return []

    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Arquivo de recomendacoes invalido: {path}") from exc
    return [RecommendationRecord(**row) for row in raw]


def load_technical_history(path: str) -> list[TechnicalHistoryPoint]:
    target = Path(path)
    if not target.exists():
        return []

    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Arquivo de historico tecnico invalido: {path}") from exc
    return [TechnicalHistoryPoint(**row) for row in raw]


def build_backtest_rows(
    recommendation_records: list[RecommendationRecord],
    technical_history: list[TechnicalHistoryPoint],
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    filtered_records = _filter_records_by_window(recommendation_records, start_date=start_date, end_date=end_date)
    deduped_records, _ = _dedupe_records_by_ticker_day(filtered_records)

    history_by_key: dict[tuple[str, str], list[TechnicalHistoryPoint]] = {}
    for point in technical_history:
        key = (point.ticker, point.data_mode)
        history_by_key.setdefault(key, []).append(point)

    for rows in history_by_key.values():
        rows.sort(key=lambda item: item.date)

    backtest_rows: list[dict] = []
    for record in deduped_records:
        key = (record.ticker, record.data_mode)
        rows = history_by_key.get(key, [])
        if not rows:
            continue

        signal_date = record.generated_at[:10]
        entry = _find_entry_row(rows, signal_date)
        next_point = _find_next_row(rows, signal_date)
        if entry is None or next_point is None or entry.close == 0:
            continue

        realized_return = (next_point.close - entry.close) / entry.close
        strategy_return = _strategy_return(record.recommendation, realized_return)
        buy_hold_return = realized_return
        outcome = _classify_outcome(record.recommendation, realized_return)

        backtest_rows.append(
            {
                "ticker": record.ticker,
                "recommendation": record.recommendation,
                "signal_date": signal_date,
                "next_date": next_point.date,
                "entry_close": entry.close,
                "next_close": next_point.close,
                "realized_return": round(realized_return, 4),
                "strategy_return": round(strategy_return, 4),
                "buy_hold_return": round(buy_hold_return, 4),
                "alpha_vs_buy_hold": round(strategy_return - buy_hold_return, 4),
                "outcome": outcome,
            }
        )

    return backtest_rows


def summarize_backtest(rows: list[dict]) -> dict[str, float | int]:
    total_signals = len(rows)
    evaluated_rows = [row for row in rows if row["recommendation"] in {"COMPRAR", "VENDER"}]
    hits = sum(1 for row in evaluated_rows if row["outcome"] == "acerto")
    hit_rate = hits / len(evaluated_rows) if evaluated_rows else 0.0
    avg_strategy_return = sum(float(row["strategy_return"]) for row in rows) / total_signals if rows else 0.0
    avg_buy_hold_return = sum(float(row["buy_hold_return"]) for row in rows) / total_signals if rows else 0.0
    avg_alpha_vs_buy_hold = avg_strategy_return - avg_buy_hold_return

    return {
        "total_signals": total_signals,
        "evaluated_signals": len(evaluated_rows),
        "hits": hits,
        "hit_rate": round(hit_rate, 4),
        "avg_strategy_return": round(avg_strategy_return, 4),
        "avg_buy_hold_return": round(avg_buy_hold_return, 4),
        "avg_alpha_vs_buy_hold": round(avg_alpha_vs_buy_hold, 4),
    }


def summarize_backtest_by_ticker(rows: list[dict]) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(str(row["ticker"]), []).append(row)

    return {ticker: summarize_backtest(ticker_rows) for ticker, ticker_rows in grouped.items()}


def run_backtest_from_files(
    recommendations_path: str,
    technical_history_path: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, object]:
    errors = _validate_window_dates(start_date=start_date, end_date=end_date)
    if errors:
        empty_summary = summarize_backtest([])
        return {
            "rows": [],
            "summary": empty_summary,
            "by_ticker": {},
            "metrics_report": build_metrics_report(summary=empty_summary, by_ticker={}),
            "window": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "errors": errors,
        }

    try:
        recommendation_records = load_recommendation_records(recommendations_path)
        technical_history = load_technical_history(technical_history_path)
    except ValueError as exc:
        empty_summary = summarize_backtest([])
        return {
            "rows": [],
            "summary": empty_summary,
            "by_ticker": {},
            "metrics_report": build_metrics_report(summary=empty_summary, by_ticker={}),
            "window": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "errors": [str(exc)],
        }

    rows = build_backtest_rows(
        recommendation_records,
        technical_history,
        start_date=start_date,
        end_date=end_date,
    )
    diagnostics = analyze_backtest_inputs(
        recommendation_records,
        technical_history,
        start_date=start_date,
        end_date=end_date,
    )
    summary = summarize_backtest(rows)
    by_ticker = summarize_backtest_by_ticker(rows)
    metrics_report = build_metrics_report(summary=summary, by_ticker=by_ticker)
    return {
        "rows": rows,
        "summary": summary,
        "by_ticker": by_ticker,
        "metrics_report": metrics_report,
        "diagnostics": diagnostics,
        "window": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "errors": [],
    }


def _find_entry_row(rows: list[TechnicalHistoryPoint], signal_date: str) -> TechnicalHistoryPoint | None:
    candidates = [row for row in rows if row.date <= signal_date]
    if not candidates:
        return None
    return candidates[-1]


def _find_next_row(rows: list[TechnicalHistoryPoint], signal_date: str) -> TechnicalHistoryPoint | None:
    for row in rows:
        if row.date > signal_date:
            return row
    return None


def _strategy_return(recommendation: str, realized_return: float) -> float:
    if recommendation == "COMPRAR":
        return realized_return
    if recommendation == "VENDER":
        return -realized_return
    return 0.0


def _classify_outcome(recommendation: str, realized_return: float) -> str:
    if recommendation == "COMPRAR":
        return "acerto" if realized_return > 0 else "erro"
    if recommendation == "VENDER":
        return "acerto" if realized_return < 0 else "erro"
    return "neutro"


def _filter_records_by_window(
    recommendation_records: list[RecommendationRecord],
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[RecommendationRecord]:
    filtered: list[RecommendationRecord] = []
    for record in recommendation_records:
        signal_date = record.generated_at[:10]
        if start_date and signal_date < start_date:
            continue
        if end_date and signal_date > end_date:
            continue
        filtered.append(record)
    return filtered


def analyze_backtest_inputs(
    recommendation_records: list[RecommendationRecord],
    technical_history: list[TechnicalHistoryPoint],
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, int]:
    filtered_records = _filter_records_by_window(recommendation_records, start_date=start_date, end_date=end_date)
    deduped_records, duplicates_discarded = _dedupe_records_by_ticker_day(filtered_records)

    history_by_key: dict[tuple[str, str], list[TechnicalHistoryPoint]] = {}
    for point in technical_history:
        key = (point.ticker, point.data_mode)
        history_by_key.setdefault(key, []).append(point)

    for rows in history_by_key.values():
        rows.sort(key=lambda item: item.date)

    stats = {
        "records_total": len(recommendation_records),
        "records_in_window": len(filtered_records),
        "records_after_dedup": len(deduped_records),
        "duplicate_same_day_discarded": duplicates_discarded,
        "rows_generated": 0,
        "missing_history_group": 0,
        "missing_entry_or_next": 0,
        "entry_close_zero": 0,
    }

    for record in deduped_records:
        key = (record.ticker, record.data_mode)
        rows = history_by_key.get(key, [])
        if not rows:
            stats["missing_history_group"] += 1
            continue

        signal_date = record.generated_at[:10]
        entry = _find_entry_row(rows, signal_date)
        next_point = _find_next_row(rows, signal_date)
        if entry is None or next_point is None:
            stats["missing_entry_or_next"] += 1
            continue
        if entry.close == 0:
            stats["entry_close_zero"] += 1
            continue

        stats["rows_generated"] += 1

    return stats


def _dedupe_records_by_ticker_day(records: list[RecommendationRecord]) -> tuple[list[RecommendationRecord], int]:
    # Mantem apenas o registro mais recente por ticker+data para evitar inflar sinais.
    by_key: dict[tuple[str, str], RecommendationRecord] = {}
    for record in records:
        key = (record.ticker, record.generated_at[:10])
        current = by_key.get(key)
        if current is None or record.generated_at >= current.generated_at:
            by_key[key] = record

    deduped = sorted(by_key.values(), key=lambda item: item.generated_at)
    discarded = len(records) - len(deduped)
    return deduped, discarded


def _validate_window_dates(start_date: str | None, end_date: str | None) -> list[str]:
    errors: list[str] = []
    start_ok = _is_valid_iso_date(start_date)
    end_ok = _is_valid_iso_date(end_date)

    if start_date and not start_ok:
        errors.append("Data inicial invalida. Use o formato YYYY-MM-DD.")
    if end_date and not end_ok:
        errors.append("Data final invalida. Use o formato YYYY-MM-DD.")
    if start_date and end_date and start_ok and end_ok and start_date > end_date:
        errors.append("Janela de backtest invalida: data inicial maior que data final.")

    return errors


def _is_valid_iso_date(value: str | None) -> bool:
    if not value:
        return True
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def build_metrics_report(summary: dict[str, float | int], by_ticker: dict[str, dict[str, float | int]]) -> dict[str, object]:
    ranked_alpha = sorted(
        (
            {
                "ticker": ticker,
                "hit_rate": float(metrics.get("hit_rate", 0.0)),
                "avg_strategy_return": float(metrics.get("avg_strategy_return", 0.0)),
                "avg_buy_hold_return": float(metrics.get("avg_buy_hold_return", 0.0)),
                "avg_alpha_vs_buy_hold": float(metrics.get("avg_alpha_vs_buy_hold", 0.0)),
            }
            for ticker, metrics in by_ticker.items()
        ),
        key=lambda item: item["avg_alpha_vs_buy_hold"],
        reverse=True,
    )

    return {
        "consolidado": {
            "sinais": int(summary.get("total_signals", 0)),
            "sinais_avaliados": int(summary.get("evaluated_signals", 0)),
            "acertos": int(summary.get("hits", 0)),
            "taxa_acerto": float(summary.get("hit_rate", 0.0)),
            "retorno_medio_estrategia": float(summary.get("avg_strategy_return", 0.0)),
            "retorno_medio_buy_hold": float(summary.get("avg_buy_hold_return", 0.0)),
            "alpha_medio_vs_buy_hold": float(summary.get("avg_alpha_vs_buy_hold", 0.0)),
        },
        "ranking_alpha": ranked_alpha,
    }