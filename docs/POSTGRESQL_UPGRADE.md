# PostgreSQL 12 to 16 Upgrade Guide

## Problem
Django requires PostgreSQL 14 or later, but the installed database cluster is version 12.17.
- PostgreSQL 16 client tools are installed: `C:\Program Files\PostgreSQL\16\bin\`
- PostgreSQL 12 server is running: `C:\Program Files\PostgreSQL\12\`
- PostgreSQL 16 service exists but is stopped

## Solution

### Important: This requires Administrator privileges

You have two options:

## Option 1: In-Place Upgrade (Recommended - Preserves exact data)

1. Right-click on PowerShell and select "Run as Administrator"
2. Navigate to the script directory and run:
   ```powershell
   C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.ps1
   ```

This script will:
- Stop PostgreSQL 12 service
- Backup PostgreSQL 12 data
- Run pg_upgrade to migrate the data
- Start PostgreSQL 16 service
- Verify the upgrade was successful

## Option 2: Manual Command-Line Upgrade

If the script fails, follow these manual steps (as Administrator):

```powershell
# Step 1: Stop PostgreSQL 12
net stop postgresql-x64-12

# Step 2: Remove old PG16 data (if any)
Remove-Item "C:\Program Files\PostgreSQL\16\data" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory "C:\Program Files\PostgreSQL\16\data" -Force

# Step 3: Run pg_upgrade
& "C:\Program Files\PostgreSQL\16\bin\pg_upgrade.exe" `
  --old-bindir "C:\Program Files\PostgreSQL\12\bin" `
  --new-bindir "C:\Program Files\PostgreSQL\16\bin" `
  --old-datadir "C:\Program Files\PostgreSQL\12\data" `
  --new-datadir "C:\Program Files\PostgreSQL\16\data"

# Step 4: Start PostgreSQL 16
net start postgresql-x64-16

# Step 5: Verify
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h 127.0.0.1 -c "SELECT version();"
```

## Option 3: If You Don't Have Admin Access

Extract database using pg_dump from v12, then restore to v16:

```powershell
# Export the database from PG12
& "C:\Program Files\PostgreSQL\12\bin\pg_dump.exe" -U postgres -h 127.0.0.1 `
  -F c postgres > "C:\temp\postgres_backup.dump"

# Restore to PG16
& "C:\Program Files\PostgreSQL\16\bin\pg_restore.exe" -U postgres -h 127.0.0.1 `
  -d postgres "C:\temp\postgres_backup.dump"
```

## Verification

After upgrade, run from your Django project:
```powershell
python manage.py runserver
```

You should no longer see the error:
```
django.db.utils.NotSupportedError: PostgreSQL 14 or later is required (found 12.17)
```

## Troubleshooting

### Cannot stop service: "Access denied"
- Right-click PowerShell and select "Run as Administrator"

### pg_upgrade fails with "server is still running"
- Make sure you've stopped the PostgreSQL 12 service: `net stop postgresql-x64-12`
- Wait a few seconds before running pg_upgrade

### Connection refused after upgrade
- Check PostgreSQL 16 service is running: `Get-Service postgresql-x64-16`
- If not running: `net start postgresql-x64-16`

### Lost connection
- Check if PostgreSQL is listening on localhost:5432: `& "C:\Program Files\PostgreSQL\16\bin\pg_isready.exe" -h 127.0.0.1 -p 5432`

