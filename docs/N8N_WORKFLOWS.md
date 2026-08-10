# MONEYYYYYY — n8n Workflows Specification

This document details the 8 production automation workflows created for the MONEYYYYYY platform.

---

## Workflow Inventory

| # | Workflow Name | Trigger | Target Endpoint | Description |
| :- | :--- | :--- | :--- | :--- |
| **1** | `MONEYYYYYY — Market Data Ingestion` | Cron (16:00 IST M-F) | `POST /api/v1/market-data/sync` | Ingests and persists daily OHLCV bars from Yahoo Finance into PostgreSQL. |
| **2** | `MONEYYYYYY — Market Data Health` | Interval (Every 15m) | `GET /health/detailed` | Probes DB, Redis, Yahoo provider, and market data freshness. |
| **3** | `MONEYYYYYY — Daily Market Summary` | Cron (15:45 IST M-F) | `GET /market/summary/daily` | Compiles NIFTY, benchmarks, sector performance, gainers/losers. |
| **4** | `MONEYYYYYY — News Pipeline` | Cron (Every 30m M-F) | `POST /market/news/ingest` | Fetches, deduplicates, and evaluates news sentiment for tracked stocks. |
| **5** | `MONEYYYYYY — AI Investment Committee` | Webhook / Weekly Cron | `POST /committee/evaluate` | Triggers multi-agent reasoning, consensus evaluation, and decision summary. |
| **6** | `MONEYYYYYY — Backtest Trigger` | Secured Webhook | `POST /api/v1/backtest/run` | Validates parameters, executes simulation on historical data, and saves run. |
| **7** | `MONEYYYYYY — Zerodha Monitoring` | Cron (Every 5m M-F) | `GET /broker/health` | Checks Zerodha authentication, session health, order book, and rejections. |
| **8** | `MONEYYYYYY — Alert Handler` | Webhook / Sub-workflow | `POST /api/v1/alerts/dispatch` | Centralized gateway for severity-based alerting and persistence. |

---

## Detailed Workflow Breakdown

### 1. MONEYYYYYY — Market Data Ingestion
- **File**: [`n8n/workflows/MONEYYYYYY — Market Data Ingestion.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20Market%20Data%20Ingestion.json)
- **Schedule**: `30 10 * * 1-5` (16:00 IST / 10:30 UTC, Monday–Friday)
- **FastAPI Endpoint**: `POST /api/v1/market-data/sync`
- **Request Payload**:
  ```json
  {
    "symbols": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "LT"],
    "days": 30
  }
  ```
- **Idempotency**: Existing prices for `(company_id, date)` are safely skipped or updated without generating duplicate records.
- **Alert Trigger**: Dispatches `IMPORT_FAILURE` alert if status is not `COMPLETED`.

---

### 2. MONEYYYYYY — Market Data Health
- **File**: [`n8n/workflows/MONEYYYYYY — Market Data Health.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20Market%20Data%20Health.json)
- **Schedule**: Interval every 15 minutes.
- **FastAPI Endpoint**: `GET /health/detailed`
- **Verification**:
  - PostgreSQL live `SELECT 1` ping and latency.
  - Redis ping (if configured).
  - Live Yahoo provider quote query on `RELIANCE.NSE`.
  - Database market data freshness and record counts.
- **Alert Trigger**: Emits `CRITICAL` alert if database query fails or Yahoo provider is unreachable.

---

### 3. MONEYYYYYY — Daily Market Summary
- **File**: [`n8n/workflows/MONEYYYYYY — Daily Market Summary.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20Daily%20Market%20Summary.json)
- **Schedule**: `15 10 * * 1-5` (15:45 IST / 10:15 UTC, Monday–Friday)
- **FastAPI Endpoint**: `GET /market/summary/daily`
- **Output**:
  - NIFTY 50, BANK NIFTY, SENSEX closing quotes and % change.
  - Major sector movements from `YahooMarketDataProvider.get_sector_performance()`.
  - Top 5 gainers and losers.
  - Market breadth (advances vs declines).
  - Automatically persisted to `system_metadata` under key `market_summary_YYYY_MM_DD`.

---

### 4. MONEYYYYYY — News Pipeline
- **File**: [`n8n/workflows/MONEYYYYYY — News Pipeline.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20News%20Pipeline.json)
- **Schedule**: `*/30 3-11 * * 1-5` (Every 30 mins during Indian market session)
- **FastAPI Endpoint**: `POST /market/news/ingest`
- **Deduplication**: Filters duplicate articles using URL and title identifiers.
- **Sentiment Policy**: True sentiment evaluated only if AI models are available; otherwise returns `sentiment_score = None` and `sentiment_label = "UNAVAILABLE"`. No mock numbers.

---

### 5. MONEYYYYYY — AI Investment Committee
- **File**: [`n8n/workflows/MONEYYYYYY — AI Investment Committee.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20AI%20Investment%20Committee.json)
- **Trigger**: Webhook (`POST /webhook/committee-evaluate`) or Weekly Schedule.
- **FastAPI Endpoint**: `POST /committee/evaluate`
- **Request Payload**:
  ```json
  {
    "ticker": "RELIANCE",
    "horizon": "MEDIUM_TERM",
    "style": "BALANCED",
    "user_query": "Evaluate institutional positioning and risk parameters"
  }
  ```
- **Orchestration**: Triggers multi-agent specialist analysis, judicial evaluation, and consensus verdict in FastAPI.

---

### 6. MONEYYYYYY — Backtest Trigger
- **File**: [`n8n/workflows/MONEYYYYYY — Backtest Trigger.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20Backtest%20Trigger.json)
- **Trigger**: Secured Webhook (`POST /webhook/backtest-trigger`)
- **FastAPI Endpoint**: `POST /api/v1/backtest/run`
- **Validation**: Rejects invalid payloads missing symbols or with `start_date >= end_date`.
- **Response**: Return %, Sharpe Ratio, Max Drawdown %, and executed trades list.

---

### 7. MONEYYYYYY — Zerodha Monitoring
- **File**: [`n8n/workflows/MONEYYYYYY — Zerodha Monitoring.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20Zerodha%20Monitoring.json)
- **Schedule**: `*/5 3-10 * * 1-5` (Every 5 mins during trading hours)
- **FastAPI Endpoint**: `GET /broker/health`
- **Safety**: Strictly read-only; never triggers orders or modifies active positions.
- **Alert Trigger**: Emits `ORDER_REJECTION` warning if rejected orders are found, and `BROKER_FAILURE` critical alert if session expires.

---

### 8. MONEYYYYYY — Alert Handler
- **File**: [`n8n/workflows/MONEYYYYYY — Alert Handler.json`](file:///d:/OneDrive/Desktop/hedge%20ai/n8n/workflows/MONEYYYYYY%20%E2%80%94%20Alert%20Handler.json)
- **Trigger**: Webhook (`POST /webhook/alert-dispatcher`)
- **FastAPI Endpoint**: `POST /api/v1/alerts/dispatch`
- **Categories**: `MARKET_DATA_FAILURE`, `YAHOO_FAILURE`, `BROKER_FAILURE`, `AI_FAILURE`, `IMPORT_FAILURE`, `BACKTEST_COMPLETED`, `ORDER_REJECTION`, `CRITICAL_SYSTEM_FAILURE`.
