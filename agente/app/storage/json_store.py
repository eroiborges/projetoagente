import json
from pathlib import Path

from app.domain.models import Recommendation, TechnicalHistoryPoint, TechnicalSnapshot, TickerRunStatus


def append_recommendations(path: str, recommendations: list[Recommendation]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict] = []
    if target.exists():
        existing = json.loads(target.read_text(encoding="utf-8"))

    existing.extend([r.__dict__ for r in recommendations])
    target.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def append_technical_snapshots(path: str, snapshots: list[TechnicalSnapshot]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict] = []
    if target.exists():
        existing = json.loads(target.read_text(encoding="utf-8"))

    merged: dict[tuple[str, str, str], dict] = {}

    for row in existing:
        key = (str(row.get("ticker", "")), str(row.get("date", "")), str(row.get("data_mode", "")))
        merged[key] = row

    for snap in snapshots:
        row = snap.__dict__
        key = (str(row.get("ticker", "")), str(row.get("date", "")), str(row.get("data_mode", "")))
        merged[key] = row

    target.write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=2), encoding="utf-8")


def append_technical_history(path: str, history_rows: list[TechnicalHistoryPoint]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict] = []
    if target.exists():
        existing = json.loads(target.read_text(encoding="utf-8"))

    merged: dict[tuple[str, str, str], dict] = {}

    for row in existing:
        key = (str(row.get("ticker", "")), str(row.get("date", "")), str(row.get("data_mode", "")))
        merged[key] = row

    for h in history_rows:
        row = h.__dict__
        key = (str(row.get("ticker", "")), str(row.get("date", "")), str(row.get("data_mode", "")))
        merged[key] = row

    target.write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=2), encoding="utf-8")


def append_ticker_statuses(path: str, statuses: list[TickerRunStatus]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict] = []
    if target.exists():
        existing = json.loads(target.read_text(encoding="utf-8"))

    existing.extend([s.__dict__ for s in statuses])
    target.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
