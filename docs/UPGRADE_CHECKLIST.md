# PostgreSQL Upgrade Checklist

## Pre-Upgrade ✓

- [ ] You have the upgrade scripts ready (in `scripts/` folder)
- [ ] You understand the error: "PostgreSQL 14 or later is required (found 12.17)"
- [ ] You have PostgreSQL 12 and 16 installed
- [ ] Your data is important and you understand it will be migrated safely

## Running the Upgrade ✓

**PICK ONE METHOD:**

### Method A: Batch File (Easiest)
- [ ] Open File Explorer
- [ ] Navigate to: `C:\Users\Nick\PycharmProjects\nstv\scripts\`
- [ ] Right-click `UPGRADE_NOW.bat`
- [ ] Select "Run as Administrator"
- [ ] Click "Yes" when Windows asks
- [ ] Watch the process complete (1-2 minutes)
- [ ] Look for "UPGRADE COMPLETE!" message

### Method B: PowerShell Script
- [ ] Right-click PowerShell → "Run as Administrator"
- [ ] Click "Yes"
- [ ] Run: `& "C:\Users\Nick\PycharmProjects\nstv\scripts\upgrade_postgresql.ps1"`
- [ ] Watch the process complete

### Method C: Manual PowerShell
- [ ] Right-click PowerShell → "Run as Administrator"
- [ ] Click "Yes"
- [ ] Copy commands from `docs/POSTGRESQL_12_TO_16_URGENT_FIX.md` Option B
- [ ] Paste and run them line by line
- [ ] Watch the process complete

## Post-Upgrade Verification ✓

- [ ] Script shows "UPGRADE COMPLETE!" or version output with "PostgreSQL 16.13"
- [ ] No errors in the output
- [ ] PostgreSQL 16 service is running (check Windows Services if needed)

## Test Django ✓

- [ ] Open PyCharm
- [ ] Open Terminal
- [ ] Run: `python manage.py runserver`
- [ ] **ERROR GONE!** ✅ No more "PostgreSQL 14 or later is required" message
- [ ] Django server starts normally

## Troubleshooting ✓

If something goes wrong:
- [ ] Read `docs/POSTGRESQL_UPGRADE_STEP_BY_STEP.md` → "Troubleshooting" section
- [ ] Try running as Administrator again
- [ ] Make sure PostgreSQL 12 is actually stopped
- [ ] Wait a few seconds and retry

## Documentation Reference ✓

| File | When to Read |
|------|--------------|
| `POSTGRESQL_12_TO_16_URGENT_FIX.md` | Quick overview |
| `POSTGRESQL_UPGRADE_STEP_BY_STEP.md` | Detailed instructions & troubleshooting |
| `POSTGRESQL_UPGRADE.md` | Complete technical details |

---

**Status**: Ready to execute!
**Next Step**: Run the batch file as Administrator 🚀

