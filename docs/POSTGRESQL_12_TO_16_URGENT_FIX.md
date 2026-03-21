# 🚨 CRITICAL: PostgreSQL Upgrade Required

## Status
- **ERROR**: `django.db.utils.NotSupportedError: PostgreSQL 14 or later is required (found 12.17)`
- **Current**: PostgreSQL 12.17 server is running
- **Available**: PostgreSQL 16.13 client tools installed
- **PostgreSQL 16** service exists (but stopped)

## Root Cause
You have PostgreSQL 12 installed and running, but Django requires version 14+.
PostgreSQL 16 binaries are installed, but the service is not started and data hasn't been migrated.

## ONE-TIME FIX (Requires Admin)

### ⚠️ IMPORTANT: You MUST Run as Administrator

**NOTE**: The simple one-liner may fail due to permissions. **RECOMMENDED**: Use the batch script instead.

### Option A: EASIEST - Run the Batch File

1. **Open File Explorer** and navigate to: `C:\Users\Nick\PycharmProjects\nstv\scripts\`
2. **Right-click** `UPGRADE_NOW.bat` → Select **"Run as Administrator"**
3. **Click "Yes"** when prompted by Windows
4. **Wait 1-2 minutes** for completion
5. **Look for**: `UPGRADE COMPLETE!` message

### Option B: PowerShell Commands

1. **Right-click PowerShell.exe** and select "Run as Administrator"
2. **Click "Yes"** to allow
3. **Paste and run this command**:

```powershell
# Stop PG12, upgrade to PG16, and start PG16
net stop postgresql-x64-12 ; `
Remove-Item 'C:\Program Files\PostgreSQL\16\data' -Recurse -Force -EA SilentlyContinue ; `
& 'C:\Program Files\PostgreSQL\16\bin\pg_upgrade.exe' `
  --old-bindir 'C:\Program Files\PostgreSQL\12\bin' `
  --new-bindir 'C:\Program Files\PostgreSQL\16\bin' `
  --old-datadir 'C:\Program Files\PostgreSQL\12\data' `
  --new-datadir 'C:\Program Files\PostgreSQL\16\data' ; `
net start postgresql-x64-16 ; `
& 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U postgres -h 127.0.0.1 -c "SELECT version();"
```

3. **Wait for it to complete** (should take 1-2 minutes)
4. **Verify the output shows**: `PostgreSQL 16.13`

## IF That Doesn't Work

### Alternative: Run the PowerShell Script

```powershell
# Run as Administrator:
& "C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.ps1"
```

## IF Still Having Issues

### Use the Python Script

```powershell
# Run as Administrator in project directory:
python C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.py
```

## After Upgrade

Run Django again:
```powershell
python manage.py runserver
```

✅ Error should be gone!

## FAQ

**Q: Will I lose my data?**
A: No. pg_upgrade preserves all data in-place.

**Q: Can I run this without admin?**
A: No. You need admin to stop/start Windows services.

**Q: What if it fails halfway?**
A: PostgreSQL 12 is still running. Try again, it should resume.

**Q: Where can I find the upgrade scripts?**
A: `C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.*`

---

**Created**: 2026-03-21
**Status**: Ready to execute

