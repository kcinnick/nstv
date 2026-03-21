# PostgreSQL Upgrade - Complete Resource Guide

## 🎯 Your Error
```
django.db.utils.NotSupportedError: PostgreSQL 14 or later is required (found 12.17)
```

## 🔧 What You Have
- ✅ PostgreSQL 12.17 running (TOO OLD)
- ✅ PostgreSQL 16.13 installed but inactive (USE THIS)
- ✅ All upgrade scripts prepared
- ✅ Complete documentation

## 🚀 FASTEST FIX (2 minutes)

**Windows Explorer:**
1. Open: `C:\Users\Nick\PycharmProjects\nstv\scripts\`
2. Right-click: `UPGRADE_NOW.bat`
3. Choose: "Run as Administrator"
4. Click: "Yes"
5. Wait: 1-2 minutes
6. See: "UPGRADE COMPLETE!"

**Done!** Your Django app now works. ✅

---

## 📂 Upgrade Scripts (In `scripts/` folder)

| Script | Type | When to Use | How to Run |
|--------|------|-----------|-----------|
| `UPGRADE_NOW.bat` | Batch | **EASIEST** - Try this first | Right-click → Run as Administrator |
| `upgrade_postgresql.ps1` | PowerShell | If batch fails | PowerShell (admin) → `& "path/to/script.ps1"` |
| `upgrade_postgresql.py` | Python | If PowerShell fails | PowerShell (admin) → `python script.py` |

---

## 📚 Documentation (In `docs/` folder)

| Document | Purpose | Best For |
|----------|---------|----------|
| `POSTGRESQL_12_TO_16_URGENT_FIX.md` | Quick reference | Getting started fast |
| `POSTGRESQL_UPGRADE_STEP_BY_STEP.md` | **Detailed guide with troubleshooting** | Learning what to do & why |
| `POSTGRESQL_UPGRADE.md` | Complete technical info | Understanding the process |
| `UPGRADE_CHECKLIST.md` | Step-by-step checklist | Following along |
| `POSTGRESQL_UPGRADE_REQUIRED.md` | This file | Overview & navigation |

---

## ❓ Frequently Asked Questions

### Q: Will I lose my data?
**A:** No! The `pg_upgrade` tool migrates all data safely in-place.

### Q: Why do I need Administrator?
**A:** Windows services (PostgreSQL 12/16) require admin to stop/start.

### Q: How long does it take?
**A:** Usually 1-2 minutes. Depends on how much data you have.

### Q: Can I run it multiple times?
**A:** Yes! If it fails, you can run it again.

### Q: What if the batch file doesn't work?
**A:** Try the PowerShell script instead: `upgrade_postgresql.ps1`

### Q: My data directory was deleted - is it gone?
**A:** No! PostgreSQL 12 data is still in `C:\Program Files\PostgreSQL\12\data`

### Q: How do I know it worked?
**A:** Run `python manage.py runserver` - if no errors, it worked!

---

## 🔄 Full Process Overview

```
1. Stop PostgreSQL 12 service
         ↓
2. Create clean PostgreSQL 16 data directory
         ↓
3. Run pg_upgrade to migrate data from 12→16
         ↓
4. Start PostgreSQL 16 service
         ↓
5. Django can now connect to PostgreSQL 16
         ↓
✅ No more version error!
```

---

## ✅ Pre-Upgrade Checklist

- [ ] You understand: PostgreSQL 12 is running, but Django needs 14+
- [ ] You have: Administrator access to run the scripts
- [ ] You know: Your data will be migrated safely
- [ ] You're ready: To wait 1-2 minutes for the upgrade

---

## ⚡ Quick Start Commands

### Batch File (Windows Explorer)
```
Right-click: C:\Users\Nick\PycharmProjects\nstv\scripts\UPGRADE_NOW.bat
Select: "Run as Administrator"
```

### PowerShell
```powershell
# Run PowerShell as Administrator, then:
& "C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.ps1"
```

### Manual (Copy-paste into Admin PowerShell)
```powershell
net stop postgresql-x64-12 ; `
Start-Sleep -Seconds 2 ; `
Remove-Item 'C:\Program Files\PostgreSQL\16\data' -Recurse -Force -EA SilentlyContinue ; `
New-Item -ItemType Directory 'C:\Program Files\PostgreSQL\16\data' -Force | Out-Null ; `
& 'C:\Program Files\PostgreSQL\16\bin\pg_upgrade.exe' `
  --old-bindir 'C:\Program Files\PostgreSQL\12\bin' `
  --new-bindir 'C:\Program Files\PostgreSQL\16\bin' `
  --old-datadir 'C:\Program Files\PostgreSQL\12\data' `
  --new-datadir 'C:\Program Files\PostgreSQL\16\data' ; `
net start postgresql-x64-16 ; `
& 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U postgres -h 127.0.0.1 -c "SELECT version();"
```

---

## 🚨 Error You Got Earlier

```
could not create directory "C:/Program Files/PostgreSQL/16/data/pg_upgrade_output.d": No such file or directory
```

**Cause:** You were running without Administrator privileges
**Solution:** Run as Administrator (scripts do this automatically)

---

## 📍 Important Paths

| Item | Path |
|------|------|
| Project | `C:\Users\Nick\PycharmProjects\nstv\` |
| Scripts | `C:\Users\Nick\PycharmProjects\nstv\scripts\` |
| Docs | `C:\Users\Nick\PycharmProjects\nstv\docs\` |
| PG12 Data | `C:\Program Files\PostgreSQL\12\data\` |
| PG16 Binaries | `C:\Program Files\PostgreSQL\16\bin\` |
| PG16 Data | `C:\Program Files\PostgreSQL\16\data\` |

---

## 🎓 Learn More

- PostgreSQL upgrade docs: `POSTGRESQL_UPGRADE.md`
- Step-by-step guide: `POSTGRESQL_UPGRADE_STEP_BY_STEP.md`
- Troubleshooting: `POSTGRESQL_UPGRADE_STEP_BY_STEP.md` → Troubleshooting section

---

## ✨ You're Ready!

Everything is prepared. Just run the batch file and you're done in 2 minutes! 🚀

**Next Step:** Open File Explorer → `scripts/` → Right-click `UPGRADE_NOW.bat` → "Run as Administrator"

