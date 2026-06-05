from app.tools import news_tool


class _FakeEntry:
    def __init__(self, title: str, summary: str = "") -> None:
        self.title = title
        self.summary = summary


class _FakeFeed:
    def __init__(self, entries, bozo=False) -> None:
        self.entries = entries
        self.bozo = bozo


def test_news_signal_real_positive_consensus(monkeypatch) -> None:
    def fake_parse(url: str):
        if "infomoney" in url:
            return _FakeFeed([
                _FakeEntry("VALE3 sobe com lucro recorde"),
                _FakeEntry("Vale tem melhora operacional"),
            ])
        if "b3" in url:
            return _FakeFeed([_FakeEntry("VALE3 em alta")])
        return _FakeFeed([])

    monkeypatch.setattr(news_tool.feedparser, "parse", fake_parse)

    signal, status, notes = news_tool.get_news_signal_with_status("VALE3", data_mode="real")
    assert status in {"ok_real", "warning_real_partial"}
    assert notes in {"live_feeds", ""} or notes.startswith("failed_sources=")
    assert signal.consensus == "positive"
    assert signal.positive >= 1


def test_news_signal_real_all_sources_failed(monkeypatch) -> None:
    def fake_parse(url: str):
        return _FakeFeed([], bozo=True)

    monkeypatch.setattr(news_tool.feedparser, "parse", fake_parse)

    signal, status, notes = news_tool.get_news_signal_with_status("PETR4", data_mode="real")
    assert status == "error_real_fallback"
    assert notes == "all_sources_failed"
    assert signal.consensus == "neutral"
    assert signal.neutral == 1


def test_news_signal_mock_mode() -> None:
    signal, status, notes = news_tool.get_news_signal_with_status("ITUB4", data_mode="mock")
    assert status == "ok_mock"
    assert notes == "mock_data"
    assert signal.ticker == "ITUB4"


def test_news_signal_real_ticker_feed_match(monkeypatch) -> None:
    def fake_parse(url: str):
        if "search?q=" in url and "itub4" in url.lower():
            return _FakeFeed([_FakeEntry("ITUB4 em alta com melhora de recomendacao")])
        return _FakeFeed([])

    monkeypatch.setattr(news_tool.feedparser, "parse", fake_parse)

    signal, status, notes = news_tool.get_news_signal_with_status("ITUB4", data_mode="real")
    assert status == "ok_real"
    assert notes == "live_feeds"
    assert signal.consensus == "positive"
    assert signal.positive >= 1
