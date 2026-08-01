# Order Execution Flow & Risk Control Architecture

## Overview

In `MONEYYYYYY`, AI agent recommendations **never auto-place live market trades**. Every trade must traverse an explicit 5-phase execution pipeline before routing to Zerodha REST APIs.

---

## The 5-Phase Execution Pipeline

```
  ┌───────────────────────┐
  │  AI Recommendation    │  (Based on Yahoo Finance market data)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │  User Approval Gate   │  (Human-in-the-loop explicit approval)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │     Order Builder     │  (Quantity, Price, CNC/MIS/NRML, LIMIT/SL)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │      Risk Checks      │  (Order size, max quantity, margin check)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │   Zerodha Order API   │  (POST /orders/regular)
  └───────────────────────┘
```

---

## Order Types & Product Types Supported

| Order Type | Zerodha Enum | Description |
|---|---|---|
| `MARKET` | `MARKET` | Instant execution at best available price |
| `LIMIT` | `LIMIT` | Execute at specified limit price or better |
| `STOP_LOSS` | `SL` | Trigger limit order when stop price is reached |
| `STOP_LOSS_MARKET` | `SL-M` | Trigger market order when stop price is reached |

| Product Type | Zerodha Enum | Description |
|---|---|---|
| `CNC` | `CNC` | Cash and Carry (Equity Delivery holdings) |
| `MIS` | `MIS` | Margin Intraday Squareoff (Intraday leverage) |
| `NRML` | `NRML` | Normal (F&O / Overnight derivatives) |

---

## Code Example

```python
from packages.application.execution import (
    ExecutionPipeline,
    ExecutionMode,
    TradeRecommendation,
    UserApprovalRequest,
)
from packages.infrastructure.brokers.zerodha import ZerodhaOrderService, ZerodhaClient

# 1. Initialize Zerodha order service
client = ZerodhaClient(api_key="...", access_token="...")
order_service = ZerodhaOrderService(client)
pipeline = ExecutionPipeline(zerodha_order_service=order_service)

# 2. AI generates recommendation from Yahoo Finance data
recommendation = TradeRecommendation(
    ticker="RELIANCE.NS",
    action="BUY",
    target_quantity=10,
    order_type="LIMIT",
    suggested_price=2450.0,
)

# 3. User grants explicit approval via UI/CLI
approval = UserApprovalRequest(
    recommendation_id="rec-101",
    approved=True,
    approved_by_user_id="user-01",
    product_type="CNC",
    execution_mode=ExecutionMode.LIVE_ZERODHA,
)

# 4. Process execution through risk check & Zerodha API
placed_order = pipeline.process_execution(
    recommendation=recommendation,
    user_approval=approval,
    portfolio_id="port-01",
    broker_account_id="zerodha-acc-01",
    available_margin=100000.0,
)

print(f"Placed Zerodha Order ID: {placed_order.id}")
```
