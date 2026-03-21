# Troubleshooting: "could not create directory" Error

## Error Message You Got

```
could not create directory "C:/Program Files/PostgreSQL/16/data/pg_upgrade_output.d": No such file or directory
Failure, exiting
The postgresql-x64-16 - PostgreSQL Server 16 service is starting.
The postgresql-x64-16 - PostgreSQL Server 16 service could not be started.
The service did not report an error.
```

## Root Cause

This error occurs because:
1. **Insufficient permissions** - The terminal wasn't running as Administrator
2. **Data directory not properly prepared** - Directory didn't exist or wasn't writable
3. **PostgreSQL 12 service still running** - pg_upgrade couldn't lock the old database

## Solution: Run as Administrator

### The Error Means:
- ❌ You ran the script without Administrator rights
- ❌ pg_upgrade couldn't write to `C:\Program Files\PostgreSQL\16\data\`
- ❌ PostgreSQL 16 service failed to start because upgrade was incomplete

### The Fix:
You need to use one of these **Administrator-level** methods:

---

## ✅ Fix Option 1: Batch File (Recommended)

**Batch files automatically detect and run with admin privileges!**

1. **Open File Explorer**
2. **Navigate to:** `C:\Users\Nick\PycharmProjects\nstv\scripts\`
3. **Right-click** `UPGRADE_NOW.bat`
4. **Select:** "Run as Administrator"
5. **Click "Yes"** when prompted
6. **Wait 1-2 minutes**
7. **Success!** You should see: `UPGRADE COMPLETE!`

---

## ✅ Fix Option 2: PowerShell as Administrator

**PowerShell must be explicitly run as Administrator:**

1. **Search for:** "PowerShell" (in Windows Start menu)
2. **Right-click** on PowerShell
3. **Select:** "Run as Administrator"
4. **Click "Yes"** when prompted by User Account Control
5. **Verify it says** "Administrator" in the title bar
6. **Run this command:**
   ```powershell
   & "C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.ps1"
   ```
7. **Wait 1-2 minutes**
8. **Look for success messages**

---

## ✅ Fix Option 3: Manual Commands in Admin PowerShell

If the script doesn't work, run these commands manually:

1. **Open PowerShell as Administrator** (same as Option 2)
2. **Copy and paste each line** (one at a time):

```powershell
# Step 1: Stop PostgreSQL 12
net stop postgresql-x64-12

# Step 2: Wait a moment
Start-Sleep -Seconds 2

# Step 3: Stop PostgreSQL 16 (in case it's running)
net stop postgresql-x64-16

# Step 4: Remove old data directory
Remove-Item 'C:\Program Files\PostgreSQL\16\data' -Recurse -Force -ErrorAction SilentlyContinue

# Step 5: Wait
Start-Sleep -Seconds 1

# Step 6: Create fresh empty data directory
New-Item -ItemType Directory -Path 'C:\Program Files\PostgreSQL\16\data' -Force

# Step 7: Run pg_upgrade (IMPORTANT: No line breaks in this command!)
& 'C:\Program Files\PostgreSQL\16\bin\pg_upgrade.exe' --old-bindir 'C:\Program Files\PostgreSQL\12\bin' --new-bindir 'C:\Program Files\PostgreSQL\16\bin' --old-datadir 'C:\Program Files\PostgreSQL\12\data' --new-datadir 'C:\Program Files\PostgreSQL\16\data'

# Step 8: Start PostgreSQL 16
net start postgresql-x64-16

# Step 9: Wait for startup
Start-Sleep -Seconds 3

# Step 10: Verify upgrade (may need password)
& 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U postgres -h 127.0.0.1 -c "SELECT version();"
```

---

## ✅ How to Verify You're Running as Administrator

**Look for these signs in PowerShell:**
- Title bar says **"Administrator: Windows PowerShell"** ✅
- You can run the `net start` and `net stop` commands without errors ✅
- Commands in `C:\Program Files\` work without "Access Denied" ✅

**NOT Administrator (will fail):**
- Title bar just says **"Windows PowerShell"** ❌
- You get "Access Denied" errors ❌
- You can't stop/start services ❌

---

## ✅ If pg_upgrade Still Fails

**Check these things:**

### 1. Is PostgreSQL 12 actually stopped?
```powershell
Get-Service postgresql-x64-12
# Should show: Status : Stopped
```

If not stopped, run: `net stop postgresql-x64-12`

### 2. Is the data directory really empty?
```powershell
# Should list nothing or just show "." 
Get-ChildItem 'C:\Program Files\PostgreSQL\16\data'
```

If not empty, run:
```powershell
Remove-Item 'C:\Program Files\PostgreSQL\16\data\*' -Recurse -Force
```

### 3. Are the paths correct?
```powershell
# Verify PG12 data exists:
Test-Path 'C:\Program Files\PostgreSQL\12\data'  # Should be: True

# Verify PG16 binaries exist:
Test-Path 'C:\Program Files\PostgreSQL\16\bin'  # Should be: True
```

### 4. Are there any locked files?
Sometimes Windows locks files if:
- PostgreSQL 12 is still running (shouldn't be)
- A file explorer window is open in the data directory (close it!)
- An antivirus is scanning (temporarily disable if safe)

---

## ✅ Success Indicators

After running the upgrade, you should see:

✅ **In the script output:**
- `UPGRADE COMPLETE!` message
- OR version output showing `PostgreSQL 16.13`
- NO error messages

✅ **In Windows Services:**
- `postgresql-x64-12` = Stopped
- `postgresql-x64-16` = Running

✅ **When testing Django:**
```powershell
python manage.py runserver
```
- No "PostgreSQL 14 or later required" error
- Django server starts normally

---

## ⚠️ If NOTHING Works

1. **Restart your computer** - Clears service locks
2. **Use the Batch File** - It's specifically designed to handle permissions
3. **Check Windows Event Viewer** - May show specific errors:
   - Press `Win + R`
   - Type: `eventvwr.msc`
   - Look under: Windows Logs → System
   - Filter by: `postgresql-x64-16`

---

## 📞 Summary

| Problem | Solution |
|---------|----------|
| "Access Denied" | Run as Administrator |
| "can't create directory" | Run as Administrator |
| pg_upgrade fails | Verify PG12 is stopped, try again as Admin |
| Service won't start | Check Windows Event Viewer for error code |
| Still seeing old version | Restart PyCharm or terminal after upgrade |

---

## ✨ Next Steps

1. **Try the batch file first** - It's the easiest and most reliable
2. **If that doesn't work,** try PowerShell script
3. **If that doesn't work,** run commands manually
4. **If commands fail,** restart computer and try batch file again

You'll get it! The batch file is very robust. ✅

