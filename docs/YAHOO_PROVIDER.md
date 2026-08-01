# Yahoo Finance Market Data Provider

> **Document Version**: 1.0.0  
> **Status**: PRODUCTION LIVE PROVIDER  
> **Target Subsystem**: Market Data Infrastructure (`packages/infrastructure/market_data/providers/yahoo_provider.py`)

---

## 1. Overview & Capabilities

The `YahooMarketDataProvider` integrates Yahoo Finance via `yfinance` into the MONEYYYYYY market data pipeline to resolve real-time quotes, OHLCV prices, and historical candles for Indian equities (NSE & BSE) and market indices.

### Supported Equities & Indices
- **NSE Blue-Chip Equities**: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `SBIN.NS`, `ICICIBANK.NS`, `ITC.NS`, `LT.NS`
- **Indian Market Indices**:
  - `NIFTY 50` / `NIFTY.NSE` -> `^NSEI`
  - `BANKNIFTY` / `BANKNIFTY.NSE` -> `^NSEBANK`
  - `SENSEX` / `SENSEX.BSE` -> `^BSESN`
- **Any Valid NSE/BSE Ticker**: Dynamic suffix mapping to `.NS` for NSE and `.BO` for BSE.

---

## 2. MarketQuote Normalization

Raw `yfinance` payloads are validated through `QuoteValidator` and mapped into the normalized `MarketQuote` domain model:

```python
MarketQuote(
    ticker=Ticker("RELIANCE.NSE"),
    exchange=ExchangeType.NSE,
    price=Price(money=Money(amount=Decimal("2579.00"), currency=Currency("INR"))),
    change=Decimal("15.50"),
    change_percent=Decimal("0.61"),
    volume=Decimal("1250000.00"),
    open=Decimal("2565.00"),
    high=Decimal("2585.00"),
    low=Decimal("2560.00"),
    previous_close=Decimal("2563.50"),
    currency="INR",
    timestamp=Timestamp.now_utc(),
    market_status=MarketStatus.OPEN,
)
```
