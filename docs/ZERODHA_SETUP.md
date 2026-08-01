# Zerodha Personal API Integration Setup Guide

## Overview

`MONEYYYYYY` integrates Zerodha exclusively as a **Trading & Execution Layer**. Because the **Personal (Free)** Zerodha plan does not include market data or historical OHLC APIs:

- **Yahoo Finance** remains the sole market data provider for quotes, candles, profiles, financials, and news.
- **Zerodha API** handles authentication, order management, holdings, positions, margins, funds, GTT orders, and alerts.

---

## Step 1: Create Zerodha Developer App

1. Visit the [Zerodha Developer Console](https://kite.trade/).
2. Log in with your Zerodha Kite credentials.
3. Click **Create new app**.
4. Set the following properties:
   - **App Name**: `MONEYYYYYY-AI-HedgeFund`
   - **Redirect URL**: `http://127.0.0.1:8000/api/v1/zerodha/callback` (or your backend callback endpoint)
   - **Description**: `Trading Layer Integration for MONEYYYYYY AI Hedge Fund`
5. Note your generated **API Key** and **API Secret**.

---

## Step 2: Environment Variables

Add the following environment variables to your `.env` file or deployment configuration:

```env
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret
ZERODHA_REDIRECT_URL=http://127.0.0.1:8000/api/v1/zerodha/callback
ZERODHA_TOKEN_STORE_PATH=~/.moneyyyyyy/zerodha_session.json
```

---

## Step 3: Daily Login & Token Generation Flow

Zerodha Personal API requires generating a fresh `access_token` once per trading day:

1. **Get Authorization URL**:
   Call `auth_service.get_login_url()` to generate the login link:
   `https://kite.zerodha.com/connect/login?v=3&api_key=YOUR_API_KEY`
2. **User Authorization**:
   Open the URL in your browser, log in with your Kite credentials and 2FA TOTP code.
3. **Receive Request Token**:
   Zerodha redirects your browser to the configured Redirect URL with a `request_token` parameter:
   `http://127.0.0.1:8000/api/v1/zerodha/callback?request_token=XXXXXX&status=success`
4. **Exchange for Access Token**:
   The `ZerodhaAuthService` calculates a SHA-256 checksum:
   `sha256(api_key + request_token + api_secret)`
   and calls Zerodha's `/session/token` endpoint.
5. **Token Caching**:
   The returned `access_token` is automatically cached in `~/.moneyyyyyy/zerodha_session.json`.

---

## Step 4: Python Code Example

```python
from packages.infrastructure.brokers.zerodha import ZerodhaAuthService, ZerodhaClient

# Initialize authentication service
auth_service = ZerodhaAuthService(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")

# 1. Load existing session if valid
if not auth_service.validate_session():
    print("Login URL:", auth_service.get_login_url())
    # User logs in and gets request_token from callback redirect
    request_token = "RECEIVED_REQUEST_TOKEN"
    auth_service.generate_session(request_token)

print("Session validated successfully!")
```
