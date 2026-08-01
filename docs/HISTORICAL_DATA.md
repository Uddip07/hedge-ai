# Historical Market Data Strategy (Yahoo Finance)

> **Document Version**: 1.0.0  
> **Status**: PRODUCTION LIVE HISTORICAL PIPELINE  
> **Target Subsystem**: `packages/infrastructure/market_data/providers/yahoo_provider.py`

---

## 1. Supported Intervals & Granularities

`YahooMarketDataProvider` queries Yahoo Finance via `yfinance` to fetch historical OHLCV candles. Supported timeframes and mappings:

- `Timeframe.MINUTE_1`: Interval `1m` (Period: `1d`)
- `Timeframe.MINUTE_5`: Interval `5m` (Period: `5d`)
- `Timeframe.MINUTE_15`: Interval `15m` (Period: `1mo`)
- `Timeframe.MINUTE_30`: Interval `30m` (Period: `1mo`)
- `Timeframe.HOUR_1`: Interval `60m` (Period: `2mo`)
- `Timeframe.DAY_1`: Interval `1d` (Period: `1y`)
- `Timeframe.WEEK_1`: Interval `1wk` (Period: `2y`)
- `Timeframe.MONTH_1`: Interval `1mo` (Period: `5y`)

---

## 2. Candle Normalization

Raw `yfinance` DataFrames are parsed and mapped via `QuoteValidator` & `QuoteMapper` into canonical `Candle` objects:

- `timestamp`: UTC Timestamp
- `open`: Open price Decimal
- `high`: High price Decimal
- `low`: Low price Decimal
- `close`: Closing price Decimal
- `volume`: Int trading volume

Zero synthetic or placeholder candles are generated if data is unavailable.
