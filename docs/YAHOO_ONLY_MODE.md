# Yahoo Finance Only Mode Documentation

> **Document Version**: 1.0.0  
> **Status**: ACTIVE EXPERIMENTAL STABILIZATION  
> **Target Subsystem**: Market Data Infrastructure (`packages/infrastructure/market_data/`)

---

## 1. Rationale for Yahoo Finance Only Mode

To eliminate any ambiguity and verify end-to-end data pipeline correctness, `YahooMarketDataProvider` has been configured as the primary runtime market quote provider in `ProviderManager`. OpenBB remains preserved in the codebase and acts as an fallback adapter without architectural modifications.

---

## 2. Infrastructure Wiring & Fallback Execution

The `ProviderManager` maintains the existing multi-provider fallback hierarchy while prioritizing live `yfinance` resolution:

```
                              ┌───────────────────────────┐
                              │     ProviderManager       │
                              └─────────────┬─────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
   ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
   │ YahooMarketData       │   │ OpenBBMarketData      │   │ NSEMarketData         │
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

## 3. How to Re-enable OpenBB as Primary Provider

To re-enable `OpenBBMarketDataProvider` as the primary provider:

1. Open `packages/infrastructure/market_data/provider_manager.py`.
2. Revert the `__init__` provider assignment:
   ```python
   self.primary: Any = primary_provider or OpenBBMarketDataProvider()
   self.fallbacks: list[Any] = (
       fallback_providers
       if fallback_providers is not None
       else [YahooMarketDataProvider(), NSEMarketDataProvider()]
   )
   ```
3. Restart the backend API application.

---

## 4. Diagnostics & Validation Procedure

A dedicated development endpoint is provided for payload comparison:

- **Endpoint**: `GET /debug/provider/{ticker}` (e.g., `GET /debug/provider/RELIANCE.NS`, `GET /debug/provider/^NSEI`)
- **Payload Structure**:
  ```json
  {
    "provider": "YahooFinance",
    "requested_symbol": "RELIANCE.NS",
    "resolved_symbol": "RELIANCE.NS",
    "raw_payload": {
      "last_price": "2579.50",
      "previous_close": "2565.00",
      "open": "2568.00",
      "day_high": "2582.00",
      "day_low": "2560.00",
      "last_volume": "1450000.0",
      "currency": "INR",
      "long_name": "Reliance Industries Limited",
      "quote_type": "EQUITY",
      "market_state": "REGULAR"
    },
    "normalized_quote": {
      "ticker": "RELIANCE.NSE",
      "price": "2579.50",
      "currency": "INR",
      "change_24h": "14.50",
      "volume_24h": "1450000.0"
    },
    "normalization_log": [
      "Successfully fetched raw yfinance.fast_info and info metadata.",
      "Normalized quote constructed successfully via YahooMarketDataProvider."
    ]
  }
  ```
