# Market Intelligence Architecture & Production Provider Specification

## 1. Executive Summary

This document specifies the production architecture for the **Market Intelligence Layer** of **MONEYYYYYY**. The design replaces all mock providers, temporary stubs, and simulated data sources with a provider-agnostic, production-grade infrastructure powered by **OpenBB** as the primary data backend.

The architecture strictly adheres to **Clean Architecture** and **Domain-Driven Design (DDD)** principles:
- The core Domain Layer (`packages/domain/`) remains 100% pure and untouched.
- The Application Layer (`packages/application/`) consumes abstract Outbound Ports (`MarketDataPort`).
- Third-party data models (OpenBB SDK outputs, Pydantic DTOs, dataframes) are strictly isolated inside the Infrastructure Layer (`packages/infrastructure/market_data/` & `packages/infrastructure/openbb/`).

---

## 2. End-to-End Data Pipeline

Every market intelligence query flows through a deterministic 5-stage pipeline:

```
[ Provider ] ──► [ Response Validation ] ──► [ Ticker/Value Normalization ] ──► [ Domain Mapping ] ──► [ Domain / Infrastructure Models ]
```

1. **Provider Execution**: Provider executes query (e.g. `OpenBBMarketDataProvider`).
2. **Response Validation**: Generic `ResponseValidator` filters (e.g., `QuoteValidator`, `FundamentalValidator`, `NewsValidator`, `MacroValidator`, `CorporateActionValidator`) verify that payload structures are complete, non-corrupted, and numeric before any transformation.
3. **Normalization**: `TickerNormalizer`, `CurrencyNormalizer`, `ExchangeNormalizer`, and `TimeframeNormalizer` convert vendor-specific codes (`RELIANCE.NS`, `$`, `NSE`, `1D`) into standard domain representations (`RELIANCE.NSE`, `INR`, `NSE`, `1D`).
4. **Domain Mapping**: Dedicated mappers (`QuoteMapper`, `FundamentalMapper`, `NewsMapper`, `MacroMapper`, `CorporateMapper`) transform raw payloads into immutable domain value objects (`Price`, `Candle`, `OHLCV`, `Company`, `NewsArticleModel`, `MacroDataSeriesModel`, `CorporateAction`).
5. **Domain Return**: Clean domain/infrastructure objects return to Application use cases.

---

## 3. Category-Specific Provider Registries

To prevent single-registry bottlenecking and enable independent provider hot-swapping per data domain, `packages/infrastructure/market_data/registries/` implements six category registries:

- **`QuoteProviderRegistry`**: Manages real-time prices, quotes snapshot, and historical OHLCV candle feeds.
- **`FundamentalProviderRegistry`**: Manages company profiles, balance sheets, income statements, cash flow statements, and key metrics.
- **`NewsProviderRegistry`**: Manages real-time news headlines, full articles, and market sentiment scores.
- **`MacroProviderRegistry`**: Manages central bank interest rates, CPI inflation, yield curves, and economic calendars.
- **`CorporateActionProviderRegistry`**: Manages dividend payouts, stock splits, bonus issues, and rights issues.
- **`ETFProviderRegistry`**: Manages ETF NAV, AUM, category benchmarks, and constituent holdings.

Each category registry inherits from `BaseProviderRegistry[T]` and supports dynamic runtime `register()`, `unregister()`, `lookup()`, and `provider_metadata()` discovery.

---

## 4. Provider Capability Discovery & Metadata

Every market data provider exposes a `ProviderMetadata` descriptor detailing capability flags:

```json
{
  "provider_name": "OpenBB",
  "provider_version": "4.1.0",
  "supported_markets": ["IN", "US", "UK"],
  "supported_exchanges": ["NSE", "BSE", "NYSE", "NASDAQ"],
  "capabilities": {
    "supports_quotes": true,
    "supports_history": true,
    "supports_fundamentals": true,
    "supports_news": true,
    "supports_macro": true,
    "supports_corporate_actions": true,
    "supports_etf": true
  }
}
```

If an operation is attempted on a provider lacking capability, the system explicitly raises `FeatureNotSupportedError` or `ProviderCapabilityError` (never returning silent `None` or swallowing errors).

---

## 5. Reliability & Observability

### Retry Policy & Exponential Backoff (`retry.py`)
`RetryPolicy` intercepts transient network glitches, HTTP 5xx server errors, and API connection timeouts with exponential backoff and jitter. Non-transient errors (such as payload validation failures, bad parameters, or unsupported capabilities) fail fast without retrying.

### Telemetry & Metrics (`telemetry.py`)
`MarketDataTelemetry` logs granular request events:
- `provider`: Identity of backend provider (e.g. `OpenBB`).
- `operation`: Name of operation (`get_quote`, `get_historical_candles`, `get_company_profile`, etc.).
- `ticker`: Asset ticker symbol.
- `latency_ms`: Request execution duration in milliseconds.
- `cache_hit`: Boolean flag indicating whether response was served from cache.
- `success`: Boolean execution status.
- `failure_reason`: Error detail string if failed.
- `request_id`: Unique UUID correlation identifier.

### Caching (`cache/`)
Short-term memory caching (`MarketDataCache`) buffers quotes and OHLCV candles to eliminate redundant network roundtrips.

---

## 6. Future Provider Extension Strategy

Adding a new market data vendor (e.g., Polygon, FMP, AlphaVantage, NSE Direct, BSE) requires only three steps without modifying Application or Domain layers:

1. **Implement Provider**: Inherit `MarketDataProvider` in `packages/infrastructure/market_data/providers/new_provider.py`.
2. **Add Symbol Rules**: Extend `TickerNormalizer` with vendor-specific symbol formatting rules.
3. **Register Provider**: Register the provider in the target category registry:
   ```python
   quote_registry.register("polygon", PolygonProvider(), polygon_metadata)
   ```

---

## 7. Migration Summary

- **Removed Mocks**: Removed/replaced `MockMarketDataProvider`, `MockFundamentalProvider`, `MockNewsProvider`, `MockMacroProvider`, `MockCorporateActionsProvider`, `MockCompanyProfileProvider`, `MockEconomicCalendarProvider`, `MockETFProvider`, `MockSectorProvider`, `MockExchangeProvider`, `MockHistoricalDataProvider`, `MockQuoteProvider`, and fake stubs.
- **Production Primary**: OpenBB (`OpenBBMarketDataProvider` & `OpenBBMarketDataAdapter`) is fully integrated across Quotes, OHLCV, Company Profiles, Financial Statements, News, Macro Series, and Corporate Actions.
