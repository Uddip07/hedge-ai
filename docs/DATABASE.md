# MONEYYYYYY Historical Market Data Platform - Database Schema TDD

The MONEYYYYYY Historical Market Data Platform uses PostgreSQL as the single source of truth for historical daily and intraday prices, corporate actions, fundamental metadata, market indices, quantitative feature caches, backtest runs, and execution logs.

---

## Database Architecture Overview

```
                      +-------------------+
                      |     companies     |
                      +-------------------+
                                | 1
                                |
                                | *
                      +-------------------+
                      | price_history_... |
                      +-------------------+
                                |
                                | (company_id, date) Unique Index
```

### Table Index

1. **`companies`**: Primary registry of corporate entities listed on Indian exchanges (NSE/BSE).
2. **`symbols`**: Fast ticker lookup and mapping repository for equities, indices, and derivatives.
3. **`price_history_daily`**: High-performance OHLCV historical time-series storage.
4. **`market_indices`**: Daily index values (NIFTY50, BANKNIFTY, NIFTYMIDCAP).
5. **`corporate_actions`**: Corporate event repository (Bonuses, Rights, Buybacks).
6. **`dividends`**: Dividend payout records (Interim, Final, Special).
7. **`splits`**: Stock split history with split ratios for price adjustments.
8. **`market_calendar`**: Exchange trading day schedule and holiday calendar.
9. **`feature_cache`**: Extensible versioned feature store for pre-computed quantitative signals.
10. **`import_jobs`**: Tracking engine for bulk CSV dataset import jobs.
11. **`import_logs`**: Per-file execution log for resumable ingestion workflows.
12. **`backtest_runs`**: Persistence repository for backtest strategy executions.
13. **`backtest_trades`**: Detailed trade execution ledger for strategy backtests.
14. **`strategy_results`**: Performance metrics breakdown (Sharpe, Drawdown, CAGR).
15. **`system_metadata`**: Dynamic key-value store for global platform metadata.

---

## Detailed Table Definitions

### 1. `companies`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Unique UUID identifier |
| `symbol` | VARCHAR(50) | UNIQUE, NOT NULL | NSE/BSE primary ticker |
| `company_name` | VARCHAR(255) | NOT NULL | Registered corporate name |
| `exchange` | VARCHAR(20) | NOT NULL | Default exchange ('NSE', 'BSE') |
| `sector` | VARCHAR(100) | INDEX | Industry sector classification |
| `industry` | VARCHAR(100) | INDEX | Specific sub-industry classification |
| `isin` | VARCHAR(20) | UNIQUE | International Securities Identification Number |
| `market_cap_category` | VARCHAR(50) | NULLABLE | Large Cap / Mid Cap / Small Cap |
| `listing_status` | VARCHAR(20) | NOT NULL | 'ACTIVE', 'SUSPENDED', 'DELISTED' |
| `index_membership` | JSON | NOT NULL | Array of index memberships |

### 2. `price_history_daily`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Unique UUID identifier |
| `company_id` | VARCHAR(36) | FOREIGN KEY (companies.id) | Referenced company entity |
| `date` | DATE | NOT NULL, INDEX | Price candle timestamp |
| `open` | FLOAT | NOT NULL | Opening price |
| `high` | FLOAT | NOT NULL | Highest price |
| `low` | FLOAT | NOT NULL | Lowest price |
| `close` | FLOAT | NOT NULL | Closing price |
| `adjusted_close` | FLOAT | NULLABLE | Split/dividend adjusted close |
| `volume` | INTEGER | NOT NULL | Traded quantity |
| `vwap` | FLOAT | NULLABLE | Volume Weighted Average Price |
| `delivery_quantity` | INTEGER | NULLABLE | Delivery volume |
| `turnover` | FLOAT | NULLABLE | Total traded turnover value |

**Constraints & Indexes**:
- `UNIQUE(company_id, date)`
- `INDEX(date)`
- `INDEX(company_id)`
- `INDEX(company_id, date)`

---

## Optimization Techniques

1. **Composite Indexing**: Dual B-Tree index on `(company_id, date)` enables point-in-time range queries with zero table scans.
2. **Bulk Ingestion**: Direct PostgreSQL dialect `ON CONFLICT DO NOTHING` or COPY stream for inserting millions of rows in seconds.
3. **Partitioning**: Designed for PostgreSQL range partitioning on `date` (yearly/monthly chunks) as data grows into hundreds of millions of records.
