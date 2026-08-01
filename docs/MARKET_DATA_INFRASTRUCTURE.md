# Production Live Market Data Infrastructure Architecture

> **Document Version**: 2.0.0  
> **Status**: PRODUCTION LIVE PIPELINE  
> **Target Subsystem**: Market Data Infrastructure (`packages/infrastructure/market_data/`)

---

## 1. Provider Hierarchy & Automatic Failover Engine

The MONEYYYYYY platform utilizes a multi-tiered provider abstraction managed by `ProviderManager` (`packages/infrastructure/market_data/provider_manager.py`).

```
                              ┌───────────────────────────┐
                              │     ProviderManager       │
                              └─────────────┬─────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
   ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
   │ OpenBBMarketData      │   │ YahooMarketData       │   │ NSEMarketData         │
   │ Provider (Primary)    │──►│ Provider (Fallback 1) │──►│ Provider (Fallback 2) │
   └───────────────────────┘   └───────────────────────┘   └───────────────────────┘
               │                            │                            │
               └────────────────────────────┼────────────────────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │ MarketDataCache         │
                               │ (Stale Cache Fallback)  │
                               └─────────────────────────┘
```

---

## 2. Adaptive Caching Policy

The market data caching layer (`packages/infrastructure/market_data/cache.py`) enforces real-time adaptive TTLs based on Indian Stock Exchange (NSE/BSE) trading session hours:

- **Live Market Hours (09:15 – 15:30 IST)**: `3-second TTL`
- **Off-Market / Post-Market Hours & Holidays**: `300-second (5 min) TTL`
- **Manual Cache Invalidation**: Immediate eviction via `GET /market/{ticker}?refresh=true`

---

## 3. Supported Exchanges & Asset Ticker Normalization

All tickers are normalized using `TickerNormalizer` (`packages/infrastructure/market_data/normalizers/ticker.py`):

- **NSE (National Stock Exchange of India)**: e.g. `RELIANCE.NSE`, `TCS.NSE`, `INFY.NSE`, `HDFCBANK.NSE`, `SBIN.NSE`, `NIFTY.NSE`
- **BSE (Bombay Stock Exchange)**: e.g. `SENSEX.BSE`
- **Bare Tickers**: Automatically resolved to `.NSE` (e.g. `RELIANCE` -> `RELIANCE.NSE`)
