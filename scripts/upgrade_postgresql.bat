@echo off
REM PostgreSQL 12 to 16 Upgrade Script
REM Run this as Administrator
REM This script will upgrade PostgreSQL from version 12 to version 16

echo Stopping PostgreSQL 12 service...
net stop postgresql-x64-12
if %ERRORLEVEL% neq 0 (
    echo Failed to stop PostgreSQL 12 service
    exit /b 1
)

echo PostgreSQL 12 service stopped.
echo.

REM Remove old data from PG16 to make room for upgrade
echo Removing old PostgreSQL 16 data directory...
rmdir /s /q "C:\Program Files\PostgreSQL\16\data"
mkdir "C:\Program Files\PostgreSQL\16\data"

echo Running pg_upgrade...
cd /d "C:\Program Files\PostgreSQL\16\bin"
pg_upgrade.exe ^
  --old-bindir "C:\Program Files\PostgreSQL\12\bin" ^
  --new-bindir "C:\Program Files\PostgreSQL\16\bin" ^
  --old-datadir "C:\Program Files\PostgreSQL\12\data" ^
  --new-datadir "C:\Program Files\PostgreSQL\16\data"

if %ERRORLEVEL% neq 0 (
    echo Upgrade failed!
    exit /b 1
)

echo.
echo Starting PostgreSQL 16 service...
net start postgresql-x64-16
if %ERRORLEVEL% neq 0 (
    echo Failed to start PostgreSQL 16 service
    exit /b 1
)

echo.
echo PostgreSQL upgrade completed successfully!
echo Verifying installation...
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h 127.0.0.1 -c "SELECT version();"

pause

