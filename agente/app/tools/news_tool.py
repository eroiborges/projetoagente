from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
from typing import Tuple

import feedparser

from app.config.settings import settings
from app.domain.models import NewsItem, NewsSignal


MOCK_NEWS = {
    "VALE3": {"positive": 3, "negative": 2, "neutral": 1},
    "PETR4": {"positive": 2, "negative": 2, "neutral": 0},
    "BBAS3": {"positive": 1, "negative": 1, "neutral": 2},
    "ITUB4": {"positive": 1, "negative": 3, "neutral": 1},
}

TICKER_TERMS = {
    "VALE3": ["vale3", "vale", "mineracao", "mineração"],
    "PETR4": ["petr4", "petrobras", "petroleo", "petróleo"],
    "BBAS3": ["bbas3", "banco do brasil", "bb"],
    "ITUB4": ["itub4", "itau", "itaú", "itau unibanco", "itaú unibanco"],
}

POSITIVE_WORDS = {
    "alta",
    "subiu",
    "lucro",
    "recorde",
    "positivo",
    "crescimento",
    "compra",
    "valorizacao",
    "valorização",
    "melhora",
}

NEGATIVE_WORDS = {
    "queda",
    "caiu",
    "prejuizo",
    "prejuízo",
    "negativo",
    "rebaixamento",
    "venda",
    "desvalorizacao",
    "desvalorização",
    "piora",
}


def _consensus(positive: int, negative: int, neutral: int) -> str:
    # Se positivo == negativo, não há consenso direcional: classifica como neutro.
    if positive == negative:
        return "neutral"

    winner = max(("positive", positive), ("negative", negative), ("neutral", neutral), key=lambda x: x[1])[0]
    return winner


def get_news_signal(ticker: str, data_mode: str = "mock") -> NewsSignal:
    signal, _, _ = get_news_signal_with_status(ticker=ticker, data_mode=data_mode)
    return signal


def get_news_signal_with_status(ticker: str, data_mode: str = "mock") -> Tuple[NewsSignal, str, str]:
    signal, status, notes, _ = get_news_signal_with_details(ticker=ticker, data_mode=data_mode)
    return signal, status, notes


def get_news_signal_with_details(ticker: str, data_mode: str = "mock") -> Tuple[NewsSignal, str, str, int]:
    signal, status, notes, matched, _ = get_news_analysis(ticker=ticker, data_mode=data_mode)
    return signal, status, notes, matched


def get_news_analysis(ticker: str, data_mode: str = "mock") -> Tuple[NewsSignal, str, str, int, list[NewsItem]]:
    if data_mode != "real":
        signal = _get_mock_signal(ticker)
        items = _mock_news_items(ticker=ticker, signal=signal)
        return signal, "ok_mock", "mock_data", len(items), items

    return _get_real_signal(ticker)


def _get_mock_signal(ticker: str) -> NewsSignal:
    raw = MOCK_NEWS.get(ticker, {"positive": 0, "negative": 0, "neutral": 1})
    return NewsSignal(
        ticker=ticker,
        positive=int(raw["positive"]),
        negative=int(raw["negative"]),
        neutral=int(raw["neutral"]),
        consensus=_consensus(raw["positive"], raw["negative"], raw["neutral"]),
    )


def _get_real_signal(ticker: str) -> Tuple[NewsSignal, str, str, int, list[NewsItem]]:
    feeds = {
        "infomoney": settings.app_feed_infomoney,
        "b3": settings.app_feed_b3,
        "reuters": settings.app_feed_reuters,
        "google_news_ticker": _ticker_feed_url(ticker),
    }

    items, failed_sources = _extract_news_items_real(ticker=ticker, feeds=feeds)
    positive = sum(1 for item in items if item.sentiment_label == "positive")
    negative = sum(1 for item in items if item.sentiment_label == "negative")
    neutral = sum(1 for item in items if item.sentiment_label == "neutral")
    matched = len(items)

    if matched == 0:
        signal = NewsSignal(ticker=ticker, positive=0, negative=0, neutral=1, consensus="neutral")
        if len(failed_sources) == len(feeds):
            return signal, "error_real_fallback", "all_sources_failed", 0, []
        return signal, "warning_real_no_match", "no_matching_news", 0, []

    signal = NewsSignal(
        ticker=ticker,
        positive=positive,
        negative=negative,
        neutral=neutral,
        consensus=_consensus(positive, negative, neutral),
    )

    if failed_sources:
        return signal, "warning_real_partial", f"failed_sources={','.join(failed_sources)}", matched, items
    return signal, "ok_real", "live_feeds", matched, items


def _extract_news_items_real(ticker: str, feeds: dict[str, str]) -> tuple[list[NewsItem], list[str]]:
    items: list[NewsItem] = []
    failed_sources: list[str] = []
    seen: set[str] = set()

    for source, url in feeds.items():
        parsed = feedparser.parse(url)
        if getattr(parsed, "bozo", False):
            failed_sources.append(source)
            continue

        entries = list(getattr(parsed, "entries", []))[: settings.app_news_limit_per_ticker]
        for entry in entries:
            text = _entry_text(entry)
            if not _is_ticker_related(ticker, text):
                continue

            label = _classify_sentiment(text)
            score = _sentiment_score(label)
            published_at = _entry_published_at(entry)
            item = NewsItem(
                ticker=ticker,
                source=source,
                published_at=published_at,
                title=str(getattr(entry, "title", "") or "").strip(),
                url=str(getattr(entry, "link", "") or "").strip(),
                summary=str(getattr(entry, "summary", "") or "").strip(),
                sentiment_label=label,
                sentiment_score=score,
                impact_score=_impact_score(ticker=ticker, text=text, published_at=published_at),
                data_mode="real",
            )

            key = _news_item_key(item)
            if key in seen:
                continue
            seen.add(key)
            items.append(item)

    return items, failed_sources


def _entry_text(entry: object) -> str:
    title = getattr(entry, "title", "") or ""
    summary = getattr(entry, "summary", "") or ""
    return f"{title} {summary}".strip().lower()


def _entry_published_at(entry: object) -> str:
    # Aceita variações comuns de data do RSS e normaliza para ISO UTC.
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(str(raw))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            continue

    return datetime.now(timezone.utc).isoformat()


def _is_ticker_related(ticker: str, text: str) -> bool:
    terms = TICKER_TERMS.get(ticker, [ticker.lower()])
    return any(term in text for term in terms)


def _ticker_feed_url(ticker: str) -> str:
    terms = TICKER_TERMS.get(ticker, [ticker.lower()])
    keywords = [ticker.lower(), *terms[:3], "acoes"]
    query = quote_plus(" OR ".join(dict.fromkeys(keywords)))
    return settings.app_feed_google_news_ticker_template.format(query=query)


def _sentiment_score(label: str) -> float:
    if label == "positive":
        return 1.0
    if label == "negative":
        return -1.0
    return 0.0


def _impact_score(ticker: str, text: str, published_at: str) -> float:
    score = 0.4

    ticker_mentions = text.count(ticker.lower())
    if ticker_mentions:
        score += min(0.2, 0.05 * ticker_mentions)

    high_impact_terms = {
        "lucro",
        "prejuizo",
        "prejuízo",
        "guidance",
        "dividend",
        "dividendo",
        "resultado",
        "fusao",
        "fusão",
        "aquisicao",
        "aquisição",
    }
    if any(term in text for term in high_impact_terms):
        score += 0.2

    try:
        dt = datetime.fromisoformat(published_at)
        age_hours = max(0.0, (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 3600)
        if age_hours <= 24:
            score += 0.2
        elif age_hours <= 72:
            score += 0.1
    except Exception:
        pass

    return max(0.0, min(1.0, score))


def _news_item_key(item: NewsItem) -> str:
    if item.url:
        return f"url:{item.url}|mode:{item.data_mode}"
    return f"fallback:{item.ticker}|{item.source}|{item.published_at}|{item.title}|{item.data_mode}"


def _mock_news_items(ticker: str, signal: NewsSignal) -> list[NewsItem]:
    labels = (
        ["positive"] * max(0, signal.positive)
        + ["negative"] * max(0, signal.negative)
        + ["neutral"] * max(0, signal.neutral)
    )
    now = datetime.now(timezone.utc).isoformat()
    items: list[NewsItem] = []
    for i, label in enumerate(labels):
        items.append(
            NewsItem(
                ticker=ticker,
                source="mock",
                published_at=now,
                title=f"Mock news {i + 1} for {ticker}",
                url=f"mock://{ticker}/{i + 1}",
                summary="Generated mock news item",
                sentiment_label=label,
                sentiment_score=_sentiment_score(label),
                impact_score=0.3,
                data_mode="mock",
            )
        )
    return items


def _classify_sentiment(text: str) -> str:
    clean = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", text.lower())
    tokens = set(clean.split())

    pos = len(tokens & POSITIVE_WORDS)
    neg = len(tokens & NEGATIVE_WORDS)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"
