# Portfolio, Holdings & Margin Synchronization Guide

## Overview

Zerodha Personal API provides full portfolio visibility including long-term holdings, intraday/overnight positions, available cash, and margin utilization. `MONEYYYYYY` maps these responses directly into domain entities (`Holding`, `Position`).

---

## Domain Normalization Architecture

```
Zerodha API Endpoints                 MONEYYYYYY Domain Models
--------------------                 ------------------------
GET /portfolio/holdings  ───────►    Holding(ticker, quantity, avg_buy_price, current_price)
GET /portfolio/positions ───────►    Position(ticker, position_type, quantity, entry_price)
GET /user/margins        ───────►    Margin & Funds Summary
```

---

## Key Features

1. **Long-Term CNC Holdings**:
   Fetched from `/portfolio/holdings`. Sums settled quantity and `t1_quantity` (T+1 pending delivery).
2. **Positions (Net & Day)**:
   Fetched from `/portfolio/positions`. Correctly identifies `LONG` vs `SHORT` directional positions based on net quantity.
3. **Margins & Risk Pre-checks**:
   Fetched from `/user/margins` or `/margins/orders` before submitting trades.

---

## Code Example

```python
from packages.infrastructure.brokers.zerodha import (
    ZerodhaClient,
    ZerodhaPortfolioService,
    ZerodhaMarginService,
)

client = ZerodhaClient(api_key="...", access_token="...")
portfolio_service = ZerodhaPortfolioService(client)
margin_service = ZerodhaMarginService(client)

# Fetch normalized holdings
holdings = portfolio_service.get_holdings()
for h in holdings:
    print(
        f"Holding: {h.ticker.symbol} | Qty: {h.quantity.value} | Avg: ₹{h.average_buy_price.value}"
    )

# Fetch positions
positions = portfolio_service.get_positions()
print("Net Positions count:", len(positions["net"]))

# Check available margin
cash = margin_service.get_equity_available_cash()
print(f"Available Cash: ₹{cash:,.2f}")
```
