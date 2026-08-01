# Financial Statements Data Strategy (Yahoo Finance)

> **Document Version**: 1.0.0  
> **Status**: PRODUCTION LIVE FINANCIAL STATEMENTS  
> **Target Subsystem**: `packages/infrastructure/market_data/providers/yahoo_provider.py`

---

## 1. Income Statement Field Mapping

- `Revenue` ← `Total Revenue`
- `Cost of Revenue` ← `Cost Of Revenue`
- `Gross Profit` ← `Gross Profit`
- `Operating Income` ← `Operating Income`
- `Net Income` ← `Net Income`
- `EBIT` ← `EBIT`
- `EBITDA` ← `EBITDA`
- `EPS` ← `Basic EPS`
- `Interest Expense` ← `Interest Expense`
- `Tax Expense` ← `Tax Provision`

---

## 2. Balance Sheet Field Mapping

- `Cash` ← `Cash And Cash Equivalents`
- `Current Assets` ← `Current Assets`
- `Total Assets` ← `Total Assets`
- `Current Liabilities` ← `Current Liabilities`
- `Total Liabilities` ← `Total Liabilities Net Minority Interest`
- `Shareholder Equity` ← `Stockholders Equity`
- `Debt` ← `Total Debt`
- `Working Capital` ← `Working Capital`

---

## 3. Cash Flow Statement Field Mapping

- `Operating Cash Flow` ← `Operating Cash Flow`
- `Investing Cash Flow` ← `Investing Cash Flow`
- `Financing Cash Flow` ← `Financing Cash Flow`
- `Free Cash Flow` ← `Free Cash Flow`
- `Capital Expenditure` ← `Capital Expenditure`

---

## 4. Financial Statement Cache Strategy

Financial statements (Income Statement, Balance Sheet, Cash Flow) are cached with a `24-hour (86,400s) TTL` in `MarketDataCache` to prevent redundant network requests.
