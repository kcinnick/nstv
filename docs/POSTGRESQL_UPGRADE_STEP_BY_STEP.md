# PostgreSQL Upgrade - Step-by-Step Guide

## Problem Summary
You got this error when running pg_upgrade:
```
could not create directory "C:/Program Files/PostgreSQL/16/data/pg_upgrade_output.d": No such file or directory
```

This happens because:
1. PostgreSQL 16 service is trying to start but the data directory wasn't properly prepared
2. We need **Administrator privileges** to:
   - Stop PostgreSQL 12 service
   - Clean the PostgreSQL 16 data directory
   - Run pg_upgrade
   - Start PostgreSQL 16 service

## ✅ Solution - Run as Administrator

### Method 1: Use the Batch File (EASIEST)

1. **Navigate to folder**: Open File Explorer
2. **Go to**: `C:\Users\Nick\PycharmProjects\nstv\scripts\`
3. **Find file**: `UPGRADE_NOW.bat`
4. **Right-click** on it → Select **"Run as Administrator"**
5. **Click "Yes"** when prompted
6. **Wait for it to complete** (1-2 minutes)
7. **Check output** for `UPGRADE COMPLETE!`

---

### Method 2: Run PowerShell Commands (If batch doesn't work)

1. **Open PowerShell** (search for "PowerShell")
2. **Right-click** → Select **"Run as administrator"**
3. **Click "Yes"** to allow
4. **Copy and paste** the following line-by-line:

```powershell
# Make sure PostgreSQL 12 is stopped
net stop postgresql-x64-12

# Wait a moment
Start-Sleep -Seconds 2

# Stop PG16 if it's running
net stop postgresql-x64-16 2>$null

# Clean the data directory
Remove-Item 'C:\Program Files\PostgreSQL\16\data' -Recurse -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Create fresh directory
New-Item -ItemType Directory -Path 'C:\Program Files\PostgreSQL\16\data' -Force | Out-Null

# Run upgrade (this may take 1-2 minutes)
& 'C:\Program Files\PostgreSQL\16\bin\pg_upgrade.exe' `
  --old-bindir 'C:\Program Files\PostgreSQL\12\bin' `
  --new-bindir 'C:\Program Files\PostgreSQL\16\bin' `
  --old-datadir 'C:\Program Files\PostgreSQL\12\data' `
  --new-datadir 'C:\Program Files\PostgreSQL\16\data'

# Start PG16
net start postgresql-x64-16

# Wait for startup
Start-Sleep -Seconds 3

# Verify
& 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U postgres -h 127.0.0.1 -c "SELECT version();"
```

5. **Watch for output**
6. **You should see**: `PostgreSQL 16.13` in the version output

---

### Method 3: Use Python Script (If PowerShell doesn't work)

1. **Open PowerShell as Administrator** (right-click → Run as administrator)
2. **Navigate to project**:
   ```powershell
   cd C:\Users\Nick\PycharmProjects\nstv
   ```
3. **Run**:
   ```powershell
   python scripts/upgrade_postgresql.py
   ```

---

## ⚠️ Important Notes

- **You MUST run as Administrator** - nothing will work without this
- The process takes **1-2 minutes**
- **Your data is safe** - pg_upgrade preserves all data
- **Don't close the window** until it completes

---

## ✅ After Upgrade - Verification

Once the upgrade completes:

1. **Open PyCharm** (or your IDE)
2. **Open Terminal** in PyCharm
3. **Run**:
   ```powershell
   python manage.py runserver
   ```

4. **You should NOT see**:
   ```
   django.db.utils.NotSupportedError: PostgreSQL 14 or later is required (found 12.17)
   ```

5. **Instead, you should see** the Django development server starting

---

## 🆘 Troubleshooting

### "Access denied" errors
- Make sure PowerShell is running as Administrator
- Right-click PowerShell icon → "Run as administrator"

### pg_upgrade still fails
- Check that PostgreSQL 12 is actually stopped: 
  ```powershell
  Get-Service postgresql-x64-12
  ```
  Should show: `Status: Stopped`

### PostgreSQL 16 won't start after upgrade
- Try starting manually:
  ```powershell
  net start postgresql-x64-16
  ```
- If it fails, check Windows Event Viewer for error details

### Port 5432 still not responding
- Wait a few seconds after starting the service
- The service may take time to fully start

---

## File Locations (For Reference)

| Item | Path |
|------|------|
| **Batch Script** | `C:\Users\Nick\PycharmProjects\nstv\scripts\UPGRADE_NOW.bat` |
| **PowerShell Script** | `C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.ps1` |
| **Python Script** | `C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.py` |
| **PG12 Data** | `C:\Program Files\PostgreSQL\12\data` |
| **PG16 Binaries** | `C:\Program Files\PostgreSQL\16\bin` |
| **PG16 Data** | `C:\Program Files\PostgreSQL\16\data` |

---

**Status**: Ready to execute - Just run the batch file as Administrator!

