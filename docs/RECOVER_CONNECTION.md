# PostgreSQL Connection Issue - Recovery Steps

## The Problem

```
pg_dump: error: connection to server at "127.0.0.1", port 5432 failed
Connection refused (0x0000274D/10061)
```

**Cause:** Both PostgreSQL 12 and PostgreSQL 16 services are stopped!

This happened because:
1. Earlier batch file stopped PostgreSQL 12
2. PostgreSQL 16 failed to start (permission/directory issue)
3. Now no database is running

---

## Solution: Start PostgreSQL 12 and Retry

### Option 1: Use the Batch File (EASIEST)

I've created: `scripts/START_PG12.bat`

**Steps:**
1. **Right-click**: `scripts/START_PG12.bat`
2. **Select**: "Run as Administrator"
3. **Click**: "Yes"
4. **Wait**: Service starts (should take 3 seconds)
5. **Result**: "PostgreSQL 12 is running and accepting connections" ✓

### Option 2: Manual Command (If Option 1 doesn't work)

**Run in Administrator PowerShell:**
```powershell
net start postgresql-x64-12
Start-Sleep -Seconds 3
& "C:\Program Files\PostgreSQL\12\bin\psql.exe" -U postgres -h 127.0.0.1 -c "SELECT version();"
```

---

## After PostgreSQL 12 Starts

### Step 1: Verify Connection
```powershell
psql -U postgres -h 127.0.0.1 -c "SELECT version();"
```

Should output:
```
PostgreSQL 12.17, compiled by...
```

### Step 2: Run the Upgrade Script Again
```powershell
python scripts/upgrade_postgresql.py
```

This will:
- ✓ Create backup successfully
- ✓ Show upgrade steps
- ✓ Provide rollback plan

### Step 3: Choose Upgrade Method

The script will show you three options:
- **Option A (Recommended)**: PostgreSQL installer
- **Option B**: pg_upgrade command
- **Option C**: Restore from backup if something fails

---

## What's Happening

```
CURRENT STATE (Both stopped):
├─ PostgreSQL 12: STOPPED ❌
├─ PostgreSQL 16: STOPPED ❌
└─ Result: Connection refused ❌

AFTER START_PG12.bat:
├─ PostgreSQL 12: RUNNING ✓
├─ PostgreSQL 16: STOPPED (temporarily OK)
└─ Result: Can backup database ✓

AFTER UPGRADE:
├─ PostgreSQL 12: STOPPED
├─ PostgreSQL 16: RUNNING ✓
└─ Result: Django works ✓
```

---

## Timeline

```
NOW: Run START_PG12.bat as Administrator (1 minute)
  ↓
PostgreSQL 12 starts (3 seconds)
  ↓
Run upgrade_postgresql.py (2 minutes - creates backup)
  ↓
Choose and execute upgrade option (2-5 minutes)
  ↓
PostgreSQL 16 running, Django works (instant)
  ↓
✅ DONE! (5-10 minutes total)
```

---

## Quick Reference

| Action | Command | Time |
|--------|---------|------|
| Start PG12 | `START_PG12.bat` (as admin) | 1 min |
| Test connection | `psql -U postgres -h 127.0.0.1 -c "SELECT version();"` | 5 sec |
| Create backup | `python upgrade_postgresql.py` | 2 min |
| Upgrade database | Follow script instructions | 5 min |
| Total | All steps | 10 min |

---

## ⚠️ Important

- **START_PG12.bat must run as Administrator** (right-click → "Run as Administrator")
- **Do NOT run upgrade_postgresql.py yet** - wait until PostgreSQL 12 is running
- **Your data is safe** - the Python script only reads it, doesn't modify

---

## Next Actions

1. **Open File Explorer**
2. **Navigate to**: `C:\Users\Nick\PycharmProjects\nstv\scripts\`
3. **Right-click**: `START_PG12.bat`
4. **Select**: "Run as Administrator"
5. **Click**: "Yes"
6. **Wait**: 3 seconds
7. **Result**: See "PostgreSQL 12 is running..."

---

## Files Created for You

| File | Purpose |
|------|---------|
| `START_PG12.bat` | Start PostgreSQL 12 service |
| `upgrade_postgresql.py` | Create backup & show upgrade options |
| (others) | Upgrade scripts & documentation |

---

**Status:** Ready to recover and upgrade
**Next Step:** Run START_PG12.bat as Administrator
**Then:** Run upgrade_postgresql.py
**Result:** Full backup + upgrade path!

