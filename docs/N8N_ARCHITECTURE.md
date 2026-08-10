# MONEYYYYYY — n8n Automation & Orchestration Architecture

This document defines the system topology, boundaries, and communication patterns for **n8n** operating as the native automation and orchestration layer for the MONEYYYYYY institutional investment platform.

---

## 1. Core Architectural Principle

> [!IMPORTANT]
> **n8n is strictly the Automation and Orchestration Layer.**
> - n8n sits **BESIDE** the application architecture.
> - n8n **DOES NOT** contain quantitative business logic, financial models, valuation math, order routing, or database connection bypasses.
> - n8n triggers existing FastAPI endpoints via authenticated HTTP and Webhooks.
> - FastAPI owns all integrations (Yahoo Finance, Zerodha, PostgreSQL, Redis, and AI Multi-Agent Committee).

---

## 2. System Topology

```
                              ┌───────────────────────────────────┐
                              │            n8n Engine             │
                              │     Native Windows : Port 5678    │
                              │   (Scheduler & Orchestration)     │
                              └─────────────────┬─────────────────┘
                                                │ HTTP / Webhook
                                                │ (Protected with X-API-Key)
                                                ▼
┌──────────────────┐                  ┌───────────────────────────────────┐
│ React / Vite UI  │─────────────────▶│       FastAPI Application         │
│   (Frontend)     │                  │          (Port 8000)              │
└──────────────────┘                  └─────────────────┬─────────────────┘
                                                        │
                    ┌───────────────────────────────────┼───────────────────────────────────┐
                    ▼                                   ▼                                   ▼
         ┌─────────────────────┐             ┌─────────────────────┐             ┌─────────────────────┐
         │  Market Data Layer  │             │   Execution Layer   │             │   AI Core Layer     │
         │  (Yahoo Finance /   │             │  (Zerodha Gateway / │             │ (Multi-Agent Com. / │
         │   NSE Replay)       │             │   Order Manager)    │             │  Research / RAG)    │
         └──────────┬──────────┘             └──────────┬──────────┘             └──────────┬──────────┘
                    │                                   │                                   │
                    └───────────────────────────────────┼───────────────────────────────────┘
                                                        ▼
                                             ┌─────────────────────┐
                                             │  Persistence Layer  │
                                             │ (PostgreSQL / Redis)│
                                             └─────────────────────┘
```

---

## 3. Communication Patterns

### Pattern A: Scheduled Automation (Time-Driven)
```
[ n8n Cron Trigger ] ──▶ [ HTTP Request (X-API-Key) ] ──▶ [ FastAPI Router ] ──▶ [ Domain/Infra Service ] ──▶ [ PostgreSQL ]
                                                                   │
                                                                   ▼
                                                            [ JSON Response ] ──▶ [ n8n Verification & Alerting ]
```

### Pattern B: Event-Driven Webhooks (Event-Driven)
```
[ External Client / Webhook ] ──▶ [ n8n Secured Webhook ] ──▶ [ Schema Validation ] ──▶ [ FastAPI /backtest/run ]
                                                                                               │
                                                                                               ▼
                                                                                   [ Persisted BacktestRun ]
```

---

## 4. Separation of Responsibilities

| Responsibility | Handled By | Description |
| :--- | :--- | :--- |
| **Workflow Scheduling** | `n8n` | Cron schedules for market close, trading hours news, periodic health probes. |
| **API Orchestration** | `n8n` | Sequence and coordinate multi-step workflows, retry backoffs, and alerts. |
| **Market Data Fetching** | `FastAPI (YahooProvider)` | Live ticker quotes, OHLCV bars, corporate actions, and sector performance. |
| **Data Validation & Deduplication**| `FastAPI (Services)` | Ensure OHLCV consistency, date sequence integrity, and article deduplication. |
| **Order Placement & Broker API**| `FastAPI (BrokerPort)` | Encapsulate Zerodha Kite Connect SDK, token lifecycles, and risk controls. |
| **AI Committee Evaluation** | `FastAPI (AI Layer)` | Multi-agent reasoning, evidence weighting, judge verdicts, and consensus. |
| **Historical Data Storage** | `FastAPI (PostgreSQL)` | Idempotent upserts to `price_history_daily`, `companies`, and `symbols`. |

---

## 5. Idempotency & Fault Tolerance

1. **Market Data Sync**: If an ingestion workflow is triggered multiple times for the same date/symbol, PostgreSQL unique constraints (`uq_price_history_company_date`) prevent duplicate rows.
2. **News Pipeline**: Articles are identified by unique URL and content hash to eliminate duplicates across polling intervals.
3. **Backtest Trigger**: Every backtest execution receives an immutable `run_id` (UUIDv4) with start and completion timestamps.
4. **Broker Monitoring**: Read-only order and session checks that never initiate unrequested trading operations or duplicate orders.
