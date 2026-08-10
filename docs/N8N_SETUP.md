# MONEYYYYYY — Native Windows n8n Setup & Installation Guide

This guide walks through the installation, environment configuration, local startup, and management of **n8n** natively on Windows (no Docker, no containers).

---

## 1. Prerequisites

- **Windows 10 / 11** or **Windows Server 2022+**
- **Node.js**: v18.17.0+ or v20.x / v24.x ([Download Node.js](https://nodejs.org/))
- **Python**: 3.12+ with `uv` package manager
- **PowerShell**: 5.1+ or PowerShell 7+

---

## 2. Global n8n Installation

Open PowerShell and install n8n globally:

```powershell
npm install -g n8n
```

Verify installation and version:

```powershell
n8n --version
```

---

## 3. Environment Configuration

Configure n8n environment variables in your project `.env` file (copied from `.env.example`):

```bash
# ==============================================================================
# n8n Native Automation & Orchestration Configuration (Windows)
# ==============================================================================
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_ENCRYPTION_KEY=replace-with-secure-32-char-encryption-key
N8N_WEBHOOK_SECRET=replace-with-secure-webhook-secret
N8N_DIAGNOSTICS_ENABLED=false
N8N_DEFAULT_TIMEZONE=Asia/Kolkata
FASTAPI_BASE_URL=http://localhost:8000
APP_API_AUTOMATION_KEY=replace-with-internal-automation-api-key
```

> [!IMPORTANT]
> - `N8N_ENCRYPTION_KEY` must be a secure, persistent key so workflow credentials remain valid across restarts.
> - `APP_API_AUTOMATION_KEY` must match between `.env` and n8n HTTP Request headers (`X-API-Key`).

---

## 4. Local Development Startup

We provide a PowerShell launcher script in `scripts/start-n8n.ps1`.

### Option A: Using the PowerShell Startup Script (Recommended)

```powershell
.\scripts\start-n8n.ps1
```

The script will:
1. Verify Node.js and n8n installations.
2. Load environment variables from `.env`.
3. Check if the FastAPI backend is running on `http://localhost:8000`.
4. Launch n8n natively on `http://localhost:5678`.

### Option B: Starting n8n Directly from CLI

```powershell
n8n
```

Open your browser to:
[http://localhost:5678](http://localhost:5678)

---

## 5. Starting the Complete Local MONEYYYYYY Stack

To run the complete platform locally:

### Terminal 1: Start FastAPI Backend
```powershell
uv run fastapi dev packages/api/main.py --port 8000
```
- API Base URL: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/health/detailed`

### Terminal 2: Start n8n Automation Engine
```powershell
.\scripts\start-n8n.ps1
```
- n8n Dashboard: `http://localhost:5678`

### Terminal 3: Start Frontend (if developing UI)
```powershell
cd frontend
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

## 6. Importing MONEYYYYYY Workflows into n8n

### Option 1: Automatic Import via CLI
```powershell
n8n import:workflow --input="n8n/workflows"
```

### Option 2: Web UI Import
1. Navigate to `http://localhost:5678/workflows`.
2. Click **Add Workflow** -> **Import from File...**
3. Select any `.json` workflow file from `n8n/workflows/`.
4. Click **Save** and toggle to **Active**.
