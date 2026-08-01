# Market Data Provider Architecture

> **Document Version**: 2.0.0  
> **Status**: APPROVED PRODUCTION ARCHITECTURE  
> **Target Subsystem**: `packages/infrastructure/market_data/`

---

## 1. Subsystem Architecture

The Market Data Provider Architecture manages multi-provider resolution, caching, status checking, and fallback execution.

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

## 2. Health Monitoring & Retries

- **Retry Policy**: Structured retry loop with exponential backoff (`RetryPolicy`).
- **Telemetry**: Records operation latency, provider source (`openbb`, `yahoo`, `nse`, `cache`), and error context (`MarketDataTelemetry`).
- **Structured Error Handling**: All provider failures degrade to stale cache or return structured domain error payloads (`ProviderConnectionError`).
