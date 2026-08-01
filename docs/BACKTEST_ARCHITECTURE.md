# MONEYYYYYY Backtest Data Architecture

The backtesting architecture is engineered to guarantee zero future leakage (lookahead bias) and high-performance feature access during quantitative simulations.

---

## Key Principles

1. **Point-In-Time Guardrails**:
   All replay queries enforce `date <= target_date` strict constraints.
   A backtest running on date `T` cannot access data from `T + 1` under any circumstances.

2. **Decoupled Feature Store**:
   Technical features (SMA, EMA, RSI, MACD, Returns, Volatility) are computed and versioned in `feature_cache`.
   Strategies query feature vectors as of date `T` without recomputing raw indicators on every tick.

3. **Repository Pattern Abstraction**:
   - `SQLMarketDataRepository`: Accesses historical candles, rolling windows, and market snapshots.
   - `SQLBacktestDataRepository`: Persists backtest runs, executed trades, and performance metrics.
