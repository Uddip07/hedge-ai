# API Quick Start Guide

## 1. Running the API Server Locally

```bash
# Start FastAPI application with Uvicorn
python -m uvicorn packages.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 2. Interactive API Documentation

Once the server is running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 3. Sample cURL Commands

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### Market Quote Lookup
```bash
curl -X GET "http://localhost:8000/market/RELIANCE.NSE"
```

### End-to-End Company Research Report
```bash
curl -X GET "http://localhost:8000/company-intelligence/INFY.NSE"
```

### Intelligent Committee Evaluation
```bash
curl -X POST "http://localhost:8000/committee/evaluate" \
     -H "Content-Type: application/json" \
     -d '{
       "ticker": "SBIN.NSE",
       "horizon": "LONG_TERM",
       "style": "VALUE",
       "user_query": "Execute comprehensive investment analysis."
     }'
```
