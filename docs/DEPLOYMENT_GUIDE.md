# Native Production Deployment & Service Guide

## 1. Overview
This guide provides instructions for deploying the **MONEYYYYYY** platform natively using Python Uvicorn workers, native PostgreSQL, optional Redis, and native n8n automation without Docker or container runtimes.

---

## 2. Architecture & Native Stack Components

| Layer | Component | Native Runtime | Local Default |
| :--- | :--- | :--- | :--- |
| **Frontend** | React / Vite SPA | Node.js (v20+) | `http://localhost:5173` |
| **Backend** | FastAPI REST Gateway | Python (v3.12+) / Uvicorn | `http://localhost:8000` |
| **Automation**| n8n Workflow Engine | Node.js / npm (`npm i -g n8n`) | `http://localhost:5678` |
| **Database** | PostgreSQL | PostgreSQL 16+ Service | `localhost:5432` |
| **Cache** | Redis (Optional) | Redis 7+ Service | `localhost:6379` |

---

## 3. Native Service Execution

### A. FastAPI Backend
```powershell
# Using uv runner
uv run uvicorn packages.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using the PowerShell launcher
.\scripts\start-backend.ps1
```

### B. Frontend Web Client
```powershell
cd frontend
npm run build
# Serve using native preview or static file server
npm run preview -- --port 5173

# Or for local development
.\scripts\start-frontend.ps1
```

### C. n8n Automation Engine
```powershell
# Native Windows startup
.\scripts\start-n8n.ps1

# Or direct CLI
n8n
```

---

## 4. PostgreSQL Native Configuration
The application reads PostgreSQL connection parameters dynamically from environment variables:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=moneyyyyyy
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
```

---

## 5. Redis Native Configuration (Optional)
```bash
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

---

## 6. Environment Variables for Production
Set the following mandatory configuration keys:
- `ENVIRONMENT=production`
- `APP_API_AUTOMATION_KEY=<secure-internal-api-key>`
- `N8N_ENCRYPTION_KEY=<secure-32-char-key>`
- `JWT_SECRET_KEY=<secure-jwt-signing-key>`
- `LOG_LEVEL=INFO`
