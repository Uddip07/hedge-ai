<#
.SYNOPSIS
    Health and connectivity check script for MONEYYYYYY Native Stack.
.DESCRIPTION
    Probes FastAPI backend and n8n engine natively.
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " MONEYYYYYY — Native Stack Health Diagnostics            " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. FastAPI Detailed Health Check
Write-Host "`n[1/2] Probing FastAPI Backend (http://localhost:8000)..." -ForegroundColor Yellow
try {
    $resp = Invoke-RestMethod -Uri "http://localhost:8000/health/detailed" -Method Get -TimeoutSec 5
    Write-Host "  FastAPI Status     : " -NoNewline
    Write-Host "$($resp.status.ToUpper())" -ForegroundColor Green
    Write-Host "  Database Status    : $($resp.components.database.status) ($($resp.components.database.latency_ms)ms)"
    Write-Host "  Yahoo Provider     : $($resp.components.yahoo_provider.status)"
    Write-Host "  Market Data Stored : $($resp.components.data_freshness.total_daily_prices) rows across $($resp.components.data_freshness.total_companies) companies"
} catch {
    Write-Host "  FastAPI Status     : " -NoNewline
    Write-Host "UNREACHABLE / OFFLINE ($($_.Exception.Message))" -ForegroundColor Red
}

# 2. n8n Engine Health Check
Write-Host "`n[2/2] Probing n8n Automation Engine (http://localhost:5678)..." -ForegroundColor Yellow
try {
    $n8nResp = Invoke-WebRequest -Uri "http://localhost:5678" -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($n8nResp.StatusCode -eq 200) {
        Write-Host "  n8n Engine Status  : " -NoNewline
        Write-Host "ONLINE / ACTIVE (HTTP 200)" -ForegroundColor Green
        Write-Host "  Dashboard URL      : http://localhost:5678"
    } else {
        Write-Host "  n8n Engine Status  : HTTP $($n8nResp.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  n8n Engine Status  : " -NoNewline
    Write-Host "OFFLINE ($($_.Exception.Message))" -ForegroundColor Red
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
