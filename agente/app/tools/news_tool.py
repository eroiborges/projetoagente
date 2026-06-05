from __future__ import annotations

import re
from urllib.parse import quote_plus
from typing import Tuple

import feedparser

from app.config.settings import settings
from app.domain.models import NewsSignal


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
    if data_mode != "real":
        signal = _get_mock_signal(ticker)
        return signal, "ok_mock", "mock_data", signal.positive + signal.negative + signal.neutral

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


def _get_real_signal(ticker: str) -> Tuple[NewsSignal, str, str, int]:
    feeds = {
        "infomoney": settings.app_feed_infomoney,
        "b3": settings.app_feed_b3,
        "reuters": settings.app_feed_reuters,
        "google_news_ticker": _ticker_feed_url(ticker),
    }

    positive = 0
    negative = 0
    neutral = 0
    matched = 0
    failed_sources: list[str] = []

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

            matched += 1
            label = _classify_sentiment(text)
            if label == "positive":
                positive += 1
            elif label == "negative":
                negative += 1
            else:
                neutral += 1

    if matched == 0:
        signal = NewsSignal(ticker=ticker, positive=0, negative=0, neutral=1, consensus="neutral")
        if len(failed_sources) == len(feeds):
            return signal, "error_real_fallback", "all_sources_failed", 0
        return signal, "warning_real_no_match", "no_matching_news", 0

    signal = NewsSignal(
        ticker=ticker,
        positive=positive,
        negative=negative,
        neutral=neutral,
        consensus=_consensus(positive, negative, neutral),
    )

    if failed_sources:
        return signal, "warning_real_partial", f"failed_sources={','.join(failed_sources)}", matched
    return signal, "ok_real", "live_feeds", matched


def _entry_text(entry: object) -> str:
    title = getattr(entry, "title", "") or ""
    summary = getattr(entry, "summary", "") or ""
    return f"{title} {summary}".strip().lower()


def _is_ticker_related(ticker: str, text: str) -> bool:
    terms = TICKER_TERMS.get(ticker, [ticker.lower()])
    return any(term in text for term in terms)


def _ticker_feed_url(ticker: str) -> str:
    terms = TICKER_TERMS.get(ticker, [ticker.lower()])
    keywords = [ticker.lower(), *terms[:3], "acoes"]
    query = quote_plus(" OR ".join(dict.fromkeys(keywords)))
    return settings.app_feed_google_news_ticker_template.format(query=query)


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
