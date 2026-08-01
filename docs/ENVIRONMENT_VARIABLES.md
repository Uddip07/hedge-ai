# Environment Variables Reference Manual

## Overview
This document specifies all environment variables controlling runtime behavior, market data provider selection, logging, and security settings across Development, Testing, and Production.

---

## Variable Specifications

| Variable Name | Purpose | Required | Default Value | Dev | Test | Prod | Security Notes |
|---|---|---|---|---|---|---|---|
| `ENV` / `ENVIRONMENT` | Runtime environment mode | No | `development` | `development` | `testing` | `production` | Production mode strictly prohibits mock providers. |
| `API_PORT` | FastAPI HTTP listener port | No | `8000` | `8000` | `8000` | `8000` | Ensure firewall rules restrict access. |
| `API_HOST` | FastAPI bind host interface | No | `0.0.0.0` | `0.0.0.0` | `127.0.0.1` | `0.0.0.0` | Bind to localhost or private VPC interfaces. |
| `OPENBB_API_KEY` | OpenBB provider authentication token | In Prod | `""` | Optional | Optional | Mandatory | Keep secret. Never commit to source code. |
| `NSE_API_KEY` | NSE Direct API key | Optional | `""` | Optional | Optional | Optional | Encrypt at rest in secret manager. |
| `YAHOO_FINANCE_API_KEY` | Yahoo Finance fallback API key | Optional | `""` | Optional | Optional | Optional | Encrypt at rest. |
| `GEMINI_API_KEY` | Google Gemini LLM API key | In Prod | `""` | Optional | Optional | Mandatory | Restrict key permissions to model inference. |
| `LOG_LEVEL` | Application logging verbosity | No | `INFO` | `DEBUG` | `INFO` | `INFO` | Keep `INFO` or `WARNING` in production. |
| `ALLOWED_ORIGINS` | CORS allowed origins JSON list | No | `["*"]` | `["*"]` | `["*"]` | Restricted URLs | Specify exact frontend domain origins in production. |
