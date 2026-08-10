<#
.SYNOPSIS
    Starts the MONEYYYYYY FastAPI Backend server natively on Windows.
.DESCRIPTION
    Launches FastAPI on port 8000 without Docker or containers.
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " MONEYYYYYY — Starting FastAPI Backend (Native Windows)   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Verify uv is installed
$uvPath = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvPath) {
    Write-Host "[WARN] 'uv' not found in PATH. Checking fallback python..." -ForegroundColor Yellow
}

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "[INFO] Loading environment variables from .env..." -ForegroundColor Green
    Get-Content .env | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $varName = $parts[0].Trim()
            $varVal = $parts[1].Trim()
            [System.Environment]::SetEnvironmentVariable($varName, $varVal, [System.EnvironmentVariableTarget]::Process)
        }
    }
} else {
    Write-Host "[WARN] .env file not found. Falling back to default environment settings." -ForegroundColor Yellow
}

$port = if ($env:PORT) { $env:PORT } else { "8000" }

Write-Host "[INFO] Starting FastAPI application on http://localhost:$port" -ForegroundColor Green
Write-Host "[INFO] Swagger Docs: http://localhost:$port/docs" -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to terminate." -ForegroundColor Gray
Write-Host ""

if ($uvPath) {
    uv run fastapi dev packages/api/main.py --port $port
} else {
    python -m uvicorn packages.api.main:app --reload --port $port
}
