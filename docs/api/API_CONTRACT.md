# MONEYYYYYY API Contract (Version 1.0.0-rc1)

## 1. Overview
This document specifies the frozen API Contract for the **MONEYYYYYY** AI Investment Operating System backend REST API (v1.0.0-rc1).

- **Protocol**: HTTP/1.1 over TLS (HTTPS)
- **Base URL**: `https://api.moneyyyyyy.internal/v1`
- **Data Format**: JSON (`application/json`)
- **Character Encoding**: UTF-8

---

## 2. Global Request & Response Envelopes

### Success Response Envelope
All API endpoints return JSON payloads matching OpenAPI v3 specifications.

### Standard Error Response Envelope
```json
{
  "error": {
    "code": "VALIDATION_ERROR | BUSINESS_RULE_VIOLATION | UNAUTHENTICATED | UNAUTHORIZED | PROVIDER_ERROR | INTERNAL_SERVER_ERROR",
    "message": "Human-readable summary message.",
    "details": {}
  }
}
```

---

## 3. Endpoints Overview

| Method | Endpoint Path | Summary | Auth | Status Codes |
|---|---|---|---|---|
| `GET` | `/` | Root Status | None | 200 |
| `GET` | `/health` | Health Check | None | 200 |
| `GET` | `/version` | Software Version Metadata | None | 200 |
| `POST` | `/analyze` | Single Stock Investment Research | Optional API Key | 200, 400, 422, 500 |
| `GET` | `/market/{ticker}` | Market Data Quote & Venue Status | Optional API Key | 200, 422, 500 |
| `GET` | `/company-intelligence/{ticker}` | End-to-End Company Research Report | Optional API Key | 200, 422, 500 |
| `POST` | `/committee/evaluate` | Multi-Agent Committee Decision | Optional API Key | 200, 400, 422, 500 |
