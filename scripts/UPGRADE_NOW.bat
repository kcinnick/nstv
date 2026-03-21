@echo off
REM PostgreSQL 12 to 16 Upgrade - ADMIN BATCH SCRIPT
REM RIGHT-CLICK THIS FILE AND SELECT "RUN AS ADMINISTRATOR"

setlocal enabledelayedexpansion

echo.
echo ============================================
echo PostgreSQL 12 to 16 Upgrade Script
echo ============================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Please right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

echo [OK] Running as Administrator
echo.

REM Define paths
set PG12_BIN=C:\Program Files\PostgreSQL\12\bin
set PG16_BIN=C:\Program Files\PostgreSQL\16\bin
set PG12_DATA=C:\Program Files\PostgreSQL\12\data
set PG16_DATA=C:\Program Files\PostgreSQL\16\data

echo Checking paths...
if not exist "%PG12_DATA%" (
    echo ERROR: PostgreSQL 12 data not found at %PG12_DATA%
    pause
    exit /b 1
)
echo [OK] PostgreSQL 12 data found

if not exist "%PG16_BIN%" (
    echo ERROR: PostgreSQL 16 binaries not found at %PG16_BIN%
    pause
    exit /b 1
)
echo [OK] PostgreSQL 16 binaries found
echo.

REM Step 1: Stop PG12
echo Step 1: Stopping PostgreSQL 12 service...
net stop postgresql-x64-12
if %errorlevel% neq 0 (
    echo WARNING: Could not stop service (may already be stopped)
)
timeout /t 2 /nobreak
echo.

REM Step 2: Stop PG16 (if running)
echo Step 2: Stopping PostgreSQL 16 service (if running)...
net stop postgresql-x64-16 >nul 2>&1
timeout /t 1 /nobreak
echo.

REM Step 3: Clean PG16 data directory
echo Step 3: Cleaning PostgreSQL 16 data directory...
if exist "%PG16_DATA%" (
    echo   Removing old data...
    rmdir /s /q "%PG16_DATA%"
    timeout /t 1 /nobreak
)

echo   Creating fresh data directory...
mkdir "%PG16_DATA%"
if %errorlevel% neq 0 (
    echo ERROR: Could not create data directory!
    pause
    exit /b 1
)
echo [OK] Data directory created
echo.

REM Step 4: Run pg_upgrade
echo Step 4: Running pg_upgrade (this may take 1-2 minutes)...
echo.
"%PG16_BIN%\pg_upgrade.exe" ^
  --old-bindir "%PG12_BIN%" ^
  --new-bindir "%PG16_BIN%" ^
  --old-datadir "%PG12_DATA%" ^
  --new-datadir "%PG16_DATA%"

if %errorlevel% neq 0 (
    echo ERROR: pg_upgrade failed with error code %errorlevel%
    echo Please check the output above for details
    pause
    exit /b 1
)
echo [OK] pg_upgrade completed successfully
echo.

REM Step 5: Start PG16
echo Step 5: Starting PostgreSQL 16 service...
net start postgresql-x64-16
if %errorlevel% neq 0 (
    echo ERROR: Could not start PostgreSQL 16 service
    pause
    exit /b 1
)
timeout /t 3 /nobreak
echo [OK] PostgreSQL 16 service started
echo.

REM Step 6: Verify
echo Step 6: Verifying installation...
"%PG16_BIN%\psql.exe" -U postgres -h 127.0.0.1 -c "SELECT version();"
if %errorlevel% neq 0 (
    echo WARNING: Could not verify with psql (password may be needed)
) else (
    echo [OK] Verification successful
)
echo.

echo ============================================
echo UPGRADE COMPLETE!
echo ============================================
echo.
echo Your PostgreSQL cluster has been upgraded from version 12 to 16.
echo Your Django application should now work without version errors.
echo.
pause

