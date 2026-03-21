@echo off
REM Start PostgreSQL 12 service
REM This allows pg_dump to create a backup before upgrading to PG16

echo Starting PostgreSQL 12 service...
net start postgresql-x64-12

if %ERRORLEVEL% neq 0 (
    echo ERROR: Could not start service
    echo You may need to run as Administrator
    exit /b 1
)

echo.
echo PostgreSQL 12 service started.
echo Waiting for service to be ready...
timeout /t 3 /nobreak

echo.
echo Testing connection...
"C:\Program Files\PostgreSQL\12\bin\psql.exe" -U postgres -h 127.0.0.1 -c "SELECT version();" 2>&1

if %ERRORLEVEL% eq 0 (
    echo.
    echo ✓ PostgreSQL 12 is running and accepting connections
    echo You can now run: python scripts/upgrade_postgresql.py
) else (
    echo.
    echo ⚠ PostgreSQL is running but connection test failed
    echo This might be a password issue
)

pause

