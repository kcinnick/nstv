# PowerShell script to start PostgreSQL 12
# RUN THIS AS ADMINISTRATOR

# Verify admin status
$isAdmin = ([Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544')

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instructions:" -ForegroundColor Yellow
    Write-Host "1. Right-click PowerShell"
    Write-Host "2. Select 'Run as Administrator'"
    Write-Host "3. Navigate to: C:\Users\Nick\PycharmProjects\nstv"
    Write-Host "4. Run: .\scripts\START_PG12_NOW.ps1"
    Write-Host ""
    pause
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Start PostgreSQL 12
Write-Host "Starting PostgreSQL 12 service..." -ForegroundColor Cyan
net start postgresql-x64-12

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start service" -ForegroundColor Red
    Write-Host "  Error code: $LASTEXITCODE"
    pause
    exit 1
}

Write-Host "✓ Service started" -ForegroundColor Green
Write-Host "  Waiting for service to fully initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test connection
Write-Host ""
Write-Host "Testing connection..." -ForegroundColor Cyan
$psql = "C:\Program Files\PostgreSQL\12\bin\psql.exe"
& $psql -U postgres -h 127.0.0.1 -c "SELECT version();" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ SUCCESS: PostgreSQL 12 is running and accepting connections!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Open PowerShell in your project directory"
    Write-Host "2. Run: python scripts/upgrade_postgresql.py"
    Write-Host "3. Follow the backup and upgrade instructions"
} else {
    Write-Host ""
    Write-Host "⚠ Service started but connection test failed" -ForegroundColor Yellow
    Write-Host "  This might be a password authentication issue"
    Write-Host "  But the service should still be running"
}

Write-Host ""
pause

