<#
.SYNOPSIS
    Starts the MONEYYYYYY Frontend development server natively on Windows.
.DESCRIPTION
    Launches Vite dev server on port 5173 without Docker or containers.
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " MONEYYYYYY — Starting Frontend Dev Server (Native)       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$frontendDir = Join-Path $PSScriptRoot "..\frontend"
if (-not (Test-Path $frontendDir)) {
    Write-Host "[ERROR] Frontend directory not found at $frontendDir" -ForegroundColor Red
    exit 1
}

# Verify npm is installed
$npmPath = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmPath) {
    Write-Host "[ERROR] 'npm' was not found in PATH. Please install Node.js." -ForegroundColor Red
    exit 1
}

Push-Location $frontendDir

try {
    Write-Host "[INFO] Starting Vite development server..." -ForegroundColor Green
    Write-Host "[INFO] App URL: http://localhost:5173" -ForegroundColor Green
    Write-Host "[INFO] Press Ctrl+C to terminate." -ForegroundColor Gray
    Write-Host ""

    npm run dev
} finally {
    Pop-Location
}
