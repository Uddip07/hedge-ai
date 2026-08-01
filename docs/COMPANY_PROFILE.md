# Company Profile Data Strategy (Yahoo Finance)

> **Document Version**: 1.0.0  
> **Status**: PRODUCTION LIVE COMPANY PROFILE  
> **Target Subsystem**: `packages/infrastructure/market_data/providers/yahoo_provider.py`

---

## 1. Supported Company Metadata Fields

`YahooMarketDataProvider.get_company_profile()` maps Yahoo Finance `info` parameters into the `Company` domain entity:

- **`company_name`**: `info.get('longName')` or `info.get('shortName')`
- **`symbol`**: Ticker symbol
- **`sector`**: `MarketSegment` (e.g. `LARGE_CAP`, `MID_CAP`)
- **`industry`**: Sector/Industry string
- **`market_cap`**: Corporate market capitalization (`float`)
- **`enterprise_value`**: Enterprise valuation (`float`)
- **`employees`**: Full-time employee count (`int`)
- **`country`**: Country of incorporation (e.g., `"India"`)
- **`currency`**: Operating currency (e.g., `"INR"`)
- **`website`**: Official corporate URL
- **`long_business_summary`**: Detailed business operation overview
- **`beta`**: Historical market beta
- **`trailing_pe`**: Trailing Price-to-Earnings ratio
- **`forward_pe`**: Forward Price-to-Earnings ratio
- **`book_value`**: Book value per share
- **`price_to_book`**: Price-to-Book ratio
- **`dividend_yield`**: Dividend yield ratio
- **`fifty_two_week_high`**: 52-week high price
- **`fifty_two_week_low`**: 52-week low price
- **`average_volume`**: 3-month average daily trading volume
- **`shares_outstanding`**: Total shares outstanding

Zero fabricated defaults (`"LARGE_CAP"` generic string, `ticker + " Limited"`) are used. Unavailable values default to `None` / `null`.

---

## 2. Cache TTL Policy

Company profiles are cached for **24 hours (86,400s)** in `MarketDataCache`.
