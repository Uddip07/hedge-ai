# Backend Troubleshooting & Diagnostics Guide

## Common Issues & Resolution Steps

### 1. `ProviderCapabilityError` / `ProviderConnectionError`
- **Symptom**: API returns 502/504 provider error status code.
- **Cause**: Upstream OpenBB or Yahoo provider connection timeout.
- **Fix**: Check `OPENBB_API_KEY` validity and network access. In testing/dev, switch `ENVIRONMENT=development` to allow fallback strategy mocks.

### 2. `ValidationError`: Ticker Symbol Format
- **Symptom**: API returns 422 Unprocessable Entity error.
- **Cause**: Ticker symbol invalid or exceeds length bounds (e.g. `INVALID_SYMBOL_LONG`).
- **Fix**: Format ticker symbols as `SYMBOL.EXCHANGE` (e.g. `RELIANCE.NSE`, `INFY.BSE`).

### 3. `ModuleNotFoundError`: packages import error
- **Symptom**: Python fails to locate `packages` module on startup.
- **Fix**: Install package in editable mode via `pip install -e .` or ensure `PYTHONPATH=.` is set.
