from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment_news: str = "gpt-5.4-mini"
    azure_openai_deployment_trading: str = "gpt-5.4-mini"
    azure_openai_api_version: str = "2024-12-01-preview"

    app_default_data_mode: str = "mock"
    app_default_execution_mode: str = "on_demand"
    app_default_tickers: str = "VALE3,PETR4,BBAS3,ITUB4"
    app_market_period: str = "6mo"
    app_news_limit_per_ticker: int = 30

    app_feed_infomoney: str = "https://www.infomoney.com.br/feed/"
    app_feed_b3: str = "https://news.google.com/rss/search?q=B3+site:b3.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    app_feed_reuters: str = "https://news.google.com/rss/search?q=site:reuters.com+business+stocks&hl=en-US&gl=US&ceid=US:en"
    app_feed_google_news_ticker_template: str = (
        "https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    )
    app_tradingview_symbol_base: str = "https://br.tradingview.com/symbols/BMFBOVESPA"


settings = Settings()
