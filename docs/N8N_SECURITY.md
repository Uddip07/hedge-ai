# MONEYYYYYY — n8n Security, Authentication & Isolation

This document outlines the security architecture, credential management, webhook protection, and trading safety mechanisms for the n8n automation layer.

---

## 1. Authentication Architecture

All communication between **n8n** and **FastAPI** is authenticated using cryptographic API keys passed via HTTP request headers:

```
[ n8n HTTP Request Node ]
       │
       │ Header: X-API-Key: <APP_API_AUTOMATION_KEY>
       ▼
[ FastAPI verify_automation_key Dependency ]
```

### Security Rules:
1. All automation endpoints verify the `X-API-Key` or `Authorization: Bearer` header.
2. In unauthorized requests, FastAPI immediately returns `401 Unauthorized` without executing downstream services.
3. The API key is stored exclusively in environment variables (`APP_API_AUTOMATION_KEY`), never hardcoded in git.

---

## 2. Webhook Protection & Validation

Workflows exposed via Webhook (`Backtest Trigger`, `AI Committee`, `Alert Handler`) enforce multi-layer validation:

1. **Payload Schema Validation**:
   - `Backtest Trigger` checks required fields (`symbols`, `start_date`, `end_date`), verifying `start_date < end_date` and `initial_capital > 0`.
   - Malformed requests are rejected with a structured `422 Unprocessable Entity` or warning alert.
2. **Method Enforcement**:
   - Webhook nodes only accept `POST` requests.
3. **Secret Token Header**:
   - In production, n8n Webhook URLs can require the `X-Webhook-Secret` header matching `N8N_WEBHOOK_SECRET`.

---

## 3. Zerodha & Broker Safety Controls

> [!CAUTION]
> Under **NO circumstances** does n8n directly place discretionary or automated orders without going through the protected application layer.

1. **Read-Only Monitoring**: The Zerodha monitoring workflow strictly calls `GET /broker/health`, which queries account state and order book without triggering order modifications.
2. **No Credential Exposure**: Zerodha API keys, API secrets, and access tokens remain isolated inside the backend `ZerodhaClient`. They are **never** passed to or stored inside n8n workflow nodes.
3. **Bounded Retries**: n8n workflows will never blindly retry financial order requests upon failure.

---

## 4. Encryption & Secret Management

1. **n8n Encryption Key**:
   - Set `N8N_ENCRYPTION_KEY` in `.env` to a 32-character high-entropy secret.
   - This encrypts all credentials, webhooks, and workflow states stored in n8n's SQLite/PostgreSQL metadata.
2. **Repository Protection**:
   - `.env` is listed in `.gitignore`.
   - Workflows stored in `n8n/workflows/` reference environment variables (`$env.APP_API_AUTOMATION_KEY`, `$env.FASTAPI_BASE_URL`) rather than hardcoded credentials.
