# Market Data Cache Strategy

> **Document Version**: 1.0.0  
> **Status**: PRODUCTION CACHE STRATEGY  
> **Target Subsystem**: `packages/infrastructure/market_data/cache.py`

---

## 1. TTL Policy

The `ProviderManager` evaluates trading calendar market status in real time to calculate dynamic cache TTLs:

- **Live Market Hours (09:15 – 15:30 IST)**: `3-second TTL`
- **Market Closed / Off-Market Hours & Holidays**: `30-second TTL`

---

## 2. Immediate Cache Invalidation

Cache invalidation is triggered manually on request:

- **API Level**: `GET /market/{ticker}?refresh=true`
- **Internal Manager Level**: `ProviderManager.get_quote(ticker, force_refresh=True)` evicts stored entries prior to executing provider queries.
