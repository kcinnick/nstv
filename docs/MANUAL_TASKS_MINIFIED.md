## ⚠️ Windows PowerShell Only
Use PowerShell commands only. Unix equivalents: `cat` → `Get-Content` | `ls -la` → `Get-ChildItem -Force` | `cp` → `Copy-Item` | `rm -rf` → `Remove-Item -Recurse -Force`

Full reference: `POWERSHELL_COMMAND_REFERENCE.md`

# Maintenance Tasks

## Daily
**Process Downloads** (Until NZBGet fixed)
- Frequency: After downloads complete
- Command: `python manage.py process_downloads`
- Alternative: Web UI → Download section → Click "Move to Plex"

## Weekly
**Check Duplicates**
- URL: http://127.0.0.1:8000/duplicates/
- Steps: Click "Scan for Duplicates" → Review → Select lower-quality → Delete
- Time: ~2-3 min for 100 shows

## As Needed
**Sync Plex**
```powershell
python manage.py process_downloads --no-move --sync-only
```

## Quick Commands
```powershell
python manage.py runserver              # Dev server
python manage.py migrate                # Database
python manage.py shell                  # Django shell
python manage.py test                   # Run tests
python manage.py createsuperuser        # Admin user
python -m pytest nstv/tests -q          # Pytest
```

## Future Automation
- Download Processing: Task Scheduler (every 15 min)
- Duplicate Scanning: Weekly scheduled + email
- Plex Optimization: Scheduled library optimization
- Database Backups: Daily PostgreSQL backups

