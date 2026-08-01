# Frontend Integration Guide for MONEYYYYYY

## 1. Overview & Handoff Vision
This document provides complete instructions, API client design patterns, state management recommendations, and response schemas for frontend engineering teams building production React/TypeScript web workbenches or mobile applications for **MONEYYYYYY**.

---

## 2. API Endpoints for Frontend Integration

### A. Market Quote Snapshot
- **Endpoint**: `GET /market/{ticker}`
- **Usage**: Live price ticker headers, watchlist panels.

### B. Intelligent Committee Decision
- **Endpoint**: `POST /committee/evaluate`
- **Request Body**:
  ```json
  {
    "ticker": "RELIANCE.NSE",
    "horizon": "LONG_TERM",
    "style": "VALUE",
    "user_query": "Execute comprehensive investment analysis."
  }
  ```
- **Usage**: Committee evaluation dashboard, multi-agent vote breakdown, consensus score card.

### C. End-to-End Company Research Report
- **Endpoint**: `GET /company-intelligence/{ticker}`
- **Usage**: Institutional research report viewer, financial charts, RAG filing evidence attribution snippets.

---

## 3. Recommended Frontend Architecture (React + TypeScript)

### Recommended Folder Structure
```
frontend/
├── src/
│   ├── api/                          # Typed API Client (Axios / Fetch)
│   │   ├── client.ts                 # Base HTTP client with interperors
│   │   ├── committeeApi.ts           # Committee endpoints
│   │   └── marketApi.ts              # Market data endpoints
│   ├── components/                   # React Workbench UI Components
│   │   ├── charts/                   # Financial & OHLCV charts
│   │   ├── committee/                # Agent opinion cards, critic findings
│   │   └── report/                   # Research report sections
│   ├── hooks/                        # Custom React Query / SWR hooks
│   │   ├── useCompanyIntelligence.ts
│   │   └── useCommitteeEvaluation.ts
│   ├── types/                        # TypeScript API DTO interfaces
│   └── store/                        # Zustand / Redux state stores
```

### Recommended State Management & Caching
- **Server State**: Use `@tanstack/react-query` or `swr` with a 15-second refetch interval for quote data and infinite cache for historical reports.
- **Client UI State**: Use `zustand` for local workbench parameters (selected ticker, investment horizon filter, active tab).
