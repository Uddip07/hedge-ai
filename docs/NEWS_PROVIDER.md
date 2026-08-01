# News Data Strategy (Yahoo Finance)

> **Document Version**: 1.0.0  
> **Status**: PRODUCTION LIVE NEWS PIPELINE  
> **Target Subsystem**: `packages/infrastructure/market_data/providers/yahoo_provider.py`

---

## 1. Mapped Fields

`YahooMarketDataProvider.get_news()` maps `yfinance.Ticker.news` into `NewsArticleModel`:

- **`title`**: Article headline
- **`content`**: Article summary or full content
- **`source`**: Publisher name (e.g. `"Reuters"`, `"Bloomberg"`)
- **`published_at`**: Publication timestamp in ISO format
- **`url`**: Article web URL
- **`sentiment_score`**: Analytical sentiment metric

Articles are deduplicated by headline and sorted newest first. Zero synthetic news items are generated.

---

## 2. Cache TTL Policy

News feeds are cached for **5 minutes (300s)** in `MarketDataCache`.
