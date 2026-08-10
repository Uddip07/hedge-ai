# ==============================================================================
# MONEYYYYYY - Native Windows n8n Automation Engine Launcher
# Starts n8n natively on Windows (NO Docker, NO Containers)
# ==============================================================================

[CmdletBinding()]
param(
    [string]$Port = "5678",
    [string]$HostName = "localhost",
    [string]$Protocol = "http"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MONEYYYYYY — Native Windows n8n Automation Orchestrator   " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verify Node.js
try {
    $nodeVer = & node -v 2>$null
    Write-Host "[OK] Node.js is installed: $nodeVer" -ForegroundColor Green
} catch {
    Write-Error "[FAIL] Node.js is not installed or not found on PATH. Please install Node.js (v18+ or v20+) from https://nodejs.org/"
    exit 1
}

# 2. Verify n8n is installed
$n8nCmd = Get-Command n8n -ErrorAction SilentlyContinue
if (-not $n8nCmd) {
    # Check common npm global path on Windows
    $npmPrefix = & npm config get prefix 2>$null
    $npmN8n = Join-Path $npmPrefix "n8n.cmd"
    if (Test-Path $npmN8n) {
        $env:PATH = "$npmPrefix;$env:PATH"
        $n8nCmd = Get-Command n8n -ErrorAction SilentlyContinue
    }
}

if (-not $n8nCmd) {
    Write-Host ""
    Write-Host "[ERROR] n8n is not installed globally on this system." -ForegroundColor Red
    Write-Host "To install n8n natively on Windows, run the following command in PowerShell:" -ForegroundColor Yellow
    Write-Host "    npm install -g n8n" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation completes, re-run this script." -ForegroundColor Yellow
    exit 1
}

$n8nVersion = & n8n --version 2>$null
Write-Host "[OK] n8n is installed: v$n8nVersion" -ForegroundColor Green

# 3. Load .env if present
$envFile = Join-Path $PSScriptRoot "..\\.env"
if (Test-Path $envFile) {
    Write-Host "[INFO] Loading configuration from .env..." -ForegroundColor Cyan
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $varName = $parts[0].Trim()
            $varVal = $parts[1].Trim()
            [System.Environment]::SetEnvironmentVariable($varName, $varVal, [System.EnvironmentVariableTarget]::Process)
        }
    }
}

# Set Default n8n Environment Variables if not provided
if (-not $env:N8N_PORT) { $env:N8N_PORT = $Port }
if (-not $env:N8N_HOST) { $env:N8N_HOST = $HostName }
if (-not $env:N8N_PROTOCOL) { $env:N8N_PROTOCOL = $Protocol }
if (-not $env:N8N_DIAGNOSTICS_ENABLED) { $env:N8N_DIAGNOSTICS_ENABLED = "false" }
if (-not $env:N8N_DEFAULT_TIMEZONE) { $env:N8N_DEFAULT_TIMEZONE = "Asia/Kolkata" }

$localUrl = "$($env:N8N_PROTOCOL)://$($env:N8N_HOST):$($env:N8N_PORT)"

# 4. Check FastAPI Connectivity (Informational)
$fastApiUrl = if ($env:FASTAPI_BASE_URL) { $env:FASTAPI_BASE_URL } else { "http://localhost:8000" }
Write-Host "[INFO] Checking FastAPI backend at $fastApiUrl/health..." -ForegroundColor Cyan
try {
    $resp = Invoke-RestMethod -Uri "$fastApiUrl/health" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
    Write-Host "[OK] FastAPI is reachable and running ($($resp.status))." -ForegroundColor Green
} catch {
    Write-Host "[WARN] FastAPI is not currently reachable at $fastApiUrl. Ensure FastAPI is running on port 8000." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting n8n Automation Engine...                         " -ForegroundColor Green
Write-Host "  Dashboard URL : $localUrl                                " -ForegroundColor Yellow
Write-Host "  Workflows Dir : $PSScriptRoot\..\n8n\workflows            " -ForegroundColor White
Write-Host "  Press Ctrl+C to stop n8n                                  " -ForegroundColor DarkGray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Launch n8n natively
& n8n
