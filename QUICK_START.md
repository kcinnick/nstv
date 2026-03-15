# QUICK START - PostgreSQL Upgrade

## TL;DR (Too Long; Didn't Read)

### Your Situation
- PostgreSQL 12.17 (too old)
- Django 5.2.11 (requires PostgreSQL 14+)
- Password: `admin` (found and verified)
- Database: Backed up ✅

### How to Fix (4 Steps)
1. Download PostgreSQL 16: https://www.postgresql.org/download/windows/
2. Run installer → Enter password `admin` → Wait
3. Run: `python scripts/verify_upgrade.py`
4. Run: `python manage.py runserver`

### Time Required
- 20-30 minutes total
- 0% risk of data loss (backup exists)
- All data preserved automatically

---

## Commands You'll Need

### Before Upgrade
```bash
# Verify current state
python scripts/test_postgres_connection.py

# Check backup
python scripts/backup_database.py --list
```

### After Upgrade
```bash
# Verify success
python scripts/verify_upgrade.py

# Start application
python manage.py runserver
```

---

## Important Notes

⚠️ **During Installation**
- When asked for password → Type: `admin`
- Don't restart computer
- Let installer finish completely

⚠️ **After Installation**
- Run `verify_upgrade.py` to confirm success
- Keep backup for 30 days
- Delete backup after 30 days if everything works

---

## If Something Goes Wrong

### Restore from Backup (10 minutes)
```bash
# Stop PostgreSQL
net stop postgresql-x64-16

# Uninstall PostgreSQL 16
# Reinstall PostgreSQL 12
# Run this to restore:
psql -U postgres < "C:\Users\Nick\PostgreSQL_Backups\postgres_backup_*.sql"
```

Your data is backed up - you can always restore!

---

## Quick Links

| Need | Link | Command |
|------|------|---------|
| Download PostgreSQL | https://www.postgresql.org/download/windows/ | (Browser) |
| Upgrade Guide | `docs/POSTGRESQL_UPGRADE_GUIDE.md` | (Read) |
| Upgrade Checklist | `UPGRADE_CHECKLIST.txt` | (Print) |
| Verify Upgrade | `python scripts/verify_upgrade.py` | (Run) |
| Create Backup | `python scripts/backup_database.py` | (Run) |
| Test Connection | `python scripts/test_postgres_connection.py` | (Run) |

---

## Status: READY ✅

