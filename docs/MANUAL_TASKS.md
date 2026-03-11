# Manual Tasks & Reminders

## Daily/Regular Tasks

### Process Downloads Manually
**Until**: NZBGet automation is fixed  
**Frequency**: After each download completes  
**Command**:
```powershell
cd C:\Users\Nick\nstv
.\.venv\Scripts\python.exe manage.py process_downloads
```

**Why**: NZBGet post-processing is currently disabled due to Python path issues

**Alternative**: Use web UI buttons:
- Visit http://127.0.0.1:8000/
- Find download section
- Click "Move to Plex" button

---

## Periodic Maintenance

### Check for Duplicate Media
**Frequency**: Weekly or after major downloads  
**URL**: http://127.0.0.1:8000/duplicates/  

**Steps**:
1. Click "Scan for Duplicates"
2. Review detected duplicates
3. Select lower-quality versions to delete
4. Confirm deletion

**Note**: Scanning ~100 shows takes about 2-3 minutes

---

### Sync Plex Database
**Frequency**: After manually moving files to Plex  
**Commands**:
```powershell
# Sync TV shows
.\.venv\Scripts\python.exe -c "from nstv.plexController.add_shows_to_nstv import main; main()"
.\.venv\Scripts\python.exe -c "from nstv.plexController.add_episodes_to_show import main; main()"

# Sync movies
.\.venv\Scripts\python.exe -c "from nstv.plexController.add_movies_to_nstv import main; main()"
```

**Or use management command**:
```powershell
# Just sync, don't move files
.\.venv\Scripts\python.exe manage.py process_downloads --no-move --sync-only
```

---

## Future Automation Opportunities

### Items That Could Be Automated

1. **Download Processing** (In Progress)
   - Current: Manual or NZBGet (disabled)
   - Future: Task Scheduler as backup (every 15 minutes)

2. **Duplicate Scanning**
   - Current: Manual web UI
   - Future: Weekly scheduled task + email report

3. **Plex Library Optimization**
   - Current: Manual in Plex
   - Future: Scheduled optimize-library command

4. **Database Backups**
   - Current: Manual
   - Future: Daily PostgreSQL backup script

---

## Quick Reference Commands

### Development Server
```powershell
python manage.py runserver
```

### Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Django Shell
```powershell
python manage.py shell
```

### Run Tests
```powershell
python manage.py test
```

### Create Superuser
```powershell
python manage.py createsuperuser
```
