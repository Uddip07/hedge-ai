# Good-Till-Triggered (GTT) Orders Guide

## Overview

Good-Till-Triggered (GTT) orders are persistent trigger rules hosted on Zerodha's servers that remain active for up to 1 year until triggered or cancelled.

`MONEYYYYYY` supports:
- **Single Trigger GTT**: Used for placing target or stop-loss orders.
- **Two-Leg (OCO) GTT**: One-Cancels-Other orders combining both target profit and stop-loss triggers.

---

## GTT Trigger Types

### 1. Single Trigger GTT
Triggers a single order when price crosses a threshold.
```json
{
  "type": "single",
  "condition": {
    "exchange": "NSE",
    "tradingsymbol": "INFY",
    "trigger_values": [1400.0],
    "last_price": 1450.0
  },
  "orders": [
    {
      "transaction_type": "SELL",
      "quantity": 10,
      "product": "CNC",
      "order_type": "LIMIT",
      "price": 1400.0
    }
  ]
}
```

### 2. Two-Leg (OCO) GTT
Contains 2 triggers (Leg 1: Stop-loss, Leg 2: Target profit). Triggering one automatically cancels the other.
```json
{
  "type": "two-leg",
  "condition": {
    "exchange": "NSE",
    "tradingsymbol": "INFY",
    "trigger_values": [1350.0, 1600.0],
    "last_price": 1450.0
  },
  "orders": [
    {
      "transaction_type": "SELL",
      "quantity": 10,
      "product": "CNC",
      "order_type": "LIMIT",
      "price": 1350.0
    },
    {
      "transaction_type": "SELL",
      "quantity": 10,
      "product": "CNC",
      "order_type": "LIMIT",
      "price": 1600.0
    }
  ]
}
```

---

## Code Example

```python
from packages.infrastructure.brokers.zerodha import ZerodhaClient, ZerodhaGTTService

client = ZerodhaClient(api_key="...", access_token="...")
gtt_service = ZerodhaGTTService(client)

# Create an OCO GTT rule for INFY
res = gtt_service.create_gtt(
    trigger_type="two-leg",
    tradingsymbol="INFY",
    exchange="NSE",
    trigger_values=[1350.0, 1600.0],
    last_price=1450.0,
    orders=[
        {
            "transaction_type": "SELL",
            "quantity": 10,
            "product": "CNC",
            "order_type": "LIMIT",
            "price": 1350.0,
        },
        {
            "transaction_type": "SELL",
            "quantity": 10,
            "product": "CNC",
            "order_type": "LIMIT",
            "price": 1600.0,
        },
    ],
)

print("Created GTT Trigger ID:", res.get("trigger_id"))
```
