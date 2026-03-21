# PowerShell script to upgrade PostgreSQL from 12 to 16
# This needs to be run as Administrator

# Function to check if running as admin
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $admin = [Security.Principal.WindowsBuiltInRole]::Administrator
    return $principal.IsInRole($admin)
}

if (-not (Test-Administrator)) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again"
    exit 1
}

$pg12DataDir = "C:\Program Files\PostgreSQL\12\data"
$pg16DataDir = "C:\Program Files\PostgreSQL\16\data"
$pg12BinDir = "C:\Program Files\PostgreSQL\12\bin"
$pg16BinDir = "C:\Program Files\PostgreSQL\16\bin"

Write-Host "PostgreSQL Upgrade from 12 to 16" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Step 1: Stop PG12 service
Write-Host "Step 1: Stopping PostgreSQL 12 service..." -ForegroundColor Yellow
try {
    Stop-Service "postgresql-x64-12" -Force -ErrorAction Stop
    Start-Sleep -Seconds 2
    Write-Host "✓ PostgreSQL 12 service stopped" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to stop PostgreSQL 12 service: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Backup PG12 data (optional but recommended)
$backupDir = "C:\Program Files\PostgreSQL\12\data_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "Step 2: Backing up PostgreSQL 12 data to $backupDir..." -ForegroundColor Yellow
try {
    Copy-Item -Path $pg12DataDir -Destination $backupDir -Recurse -Force
    Write-Host "✓ Backup completed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Backup failed (non-fatal): $_" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Clear PG16 data directory
Write-Host "Step 3: Clearing PostgreSQL 16 data directory..." -ForegroundColor Yellow
try {
    Remove-Item -Path $pg16DataDir -Recurse -Force -ErrorAction Stop
    New-Item -ItemType Directory -Path $pg16DataDir -Force | Out-Null
    Write-Host "✓ PostgreSQL 16 data directory cleared" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to clear data directory: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Run pg_upgrade
Write-Host "Step 4: Running pg_upgrade..." -ForegroundColor Yellow
$pgUpgrade = Join-Path $pg16BinDir "pg_upgrade.exe"

try {
    & $pgUpgrade `
        --old-bindir $pg12BinDir `
        --new-bindir $pg16BinDir `
        --old-datadir $pg12DataDir `
        --new-datadir $pg16DataDir `
        2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ pg_upgrade completed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ pg_upgrade failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Exception running pg_upgrade: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Start PG16 service
Write-Host "Step 5: Starting PostgreSQL 16 service..." -ForegroundColor Yellow
try {
    Start-Service "postgresql-x64-16" -ErrorAction Stop
    Start-Sleep -Seconds 3
    Write-Host "✓ PostgreSQL 16 service started" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to start PostgreSQL 16 service: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 6: Verify
Write-Host "Step 6: Verifying upgrade..." -ForegroundColor Yellow
try {
    $psql = Join-Path $pg16BinDir "psql.exe"
    $versionOutput = & $psql -U postgres -h 127.0.0.1 -c "SELECT version();" 2>&1
    Write-Host $versionOutput -ForegroundColor Cyan
    Write-Host "✓ Verification successful" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not verify: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "PostgreSQL upgrade completed!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

