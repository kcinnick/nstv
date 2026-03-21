# NSTV Quick Task Checklist

Quick reference for common developer tasks - print this out or bookmark it!

---

## ⚡ One-Liners (Copy & Paste)

### Activate Virtual Environment
```powershell
cd C:\Users\Nick\PycharmProjects\nstv; .\venv\Scripts\Activate.ps1
```

### Process Downloads (Test First!)
```powershell
# DRY RUN - see what would happen
python manage.py process_downloads --dry-run

# ACTUALLY MOVE FILES
python manage.py process_downloads

# Just TV shows, verbose output
python manage.py process_downloads --media-type tv --verbose
```

### Sync Plex to Database
```powershell
# All: shows + episodes + movies
python manage.py process_downloads

# Or individually:
python -c "from nstv.plexController.add_shows_to_nstv import main; main()"
python -c "from nstv.plexController.add_episodes_to_show import main; main()"
python -c "from nstv.plexController.add_movies_to_nstv import main; main()"
```

### Django Shell (Interactive Database Access)
```powershell
python manage.py shell
```

Then in Python:
```python
from nstv.models import Show, Episode
Show.objects.count()
Show.objects.get(title='Breaking Bad').episodes.count()
```

### Start Development Server
```powershell
python manage.py runserver
# Visit: http://localhost:8000/nstv
```

### Run Tests
```powershell
pytest
pytest -v --tb=short
```

### Check for Issues
```powershell
python manage.py check
```

---

## 🔧 Setup & Configuration

### First Time Setup
```powershell
# 1. Activate venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Create .env file (see below)

# 4. Run migrations
python manage.py migrate

# 5. Start server
python manage.py runserver
```

### `.env` File Template
Location: `C:\Users\Nick\PycharmProjects\nstv\.env`

```dotenv
DJANGO_DB_PASSWORD=admin
PLEX_EMAIL=nicktucker4@gmail.com
PLEX_API_KEY=5GmbFhN1Mipz2bzRoBJy
PLEX_SERVER=http://192.168.1.101:32400
SHOW_FOLDER_PATH="Y:\Library\TV Shows"
PLEX_TV_SHOW_DIR="Z:\Library\TV Shows"
PLEX_MOVIES_DIR="Z:\Library\Movies"
NZBGET_COMPLETE_DIR=C:\ProgramData\NZBGet\complete
NZBGET_NZB_DIR=C:\ProgramData\NZBGet\nzb
TEMP_FOLDER_PATH=
```

### Network Drive Mapping
```powershell
# Map Y: drive (if not already done)
net use Y: \\192.168.1.101\Plex /persistent:yes

# Map Z: drive (if not already done)
net use Z: \\192.168.1.101\Plex2 /persistent:yes

# Verify
Test-Path Y:\Library\TV Shows
Test-Path Z:\Library\TV Shows
```

---

## 📺 Workflow: Process a New Download

**Scenario**: NZBGet finished downloading "Breaking Bad S05E16"

### Step 1: Test with Dry-Run (Optional but Recommended)
```powershell
python manage.py process_downloads --dry-run
```

**Expected Output**:
```
DRY RUN MODE - No files will be moved
Checking Plex server connection...
[OK] Plex server "http://192.168.1.101:32400" is accessible

================================================================================
Processing TV Shows
================================================================================
Found 1 items to process

[1/1] Processing: Breaking Bad S05E16.WEBRIP.1080p
  Organization: Breaking Bad/
  Size: 1.2 GB
  WOULD MOVE

================================================================================
SUMMARY
================================================================================
Would move: 1 items
```

### Step 2: Actually Process
```powershell
python manage.py process_downloads
```

**What Happens**:
1. ✅ Detects "S05E16" = TV show
2. ✅ Extracts "Breaking Bad" as show name
3. ✅ Moves file to: `Z:\Library\TV Shows\Breaking Bad\Breaking Bad S05E16.WEBRIP.1080p`
4. ✅ Plex auto-discovers it
5. ✅ Syncs to Django database: `Episode.on_disk = True`

### Step 3: Verify in Django
```powershell
python manage.py shell
```

```python
from nstv.models import Show, Episode
show = Show.objects.get(title='Breaking Bad')
episode = show.episodes.get(season_number=5, episode_number=16)
print(f"On Disk: {episode.on_disk}")  # Should be True
```

---

## 🔍 Workflow: Find & Fix Issues

### Issue: "TV directory not found: Z:\Library\TV Shows"

**Checklist**:
```powershell
# 1. Check drive mapping
Test-Path Z:\
Test-Path Z:\Library\TV Shows

# If False, map the drive
net use Z: \\192.168.1.101\Plex2 /persistent:yes

# 2. Check .env file
cat .env | grep PLEX_TV_SHOW_DIR

# 3. Verify path exists on NAS (ask your NAS provider or check manually)

# 4. Try again
python manage.py process_downloads --dry-run
```

### Issue: "Cannot connect to Plex server"

**Checklist**:
```powershell
# 1. Ping the Plex server
ping 192.168.1.101

# 2. Check PLEX_SERVER in .env
cat .env | grep PLEX_SERVER
# Should be: PLEX_SERVER=http://192.168.1.101:32400

# 3. Check PLEX_API_KEY is valid
cat .env | grep PLEX_API_KEY
# Get fresh key from Plex → Settings → Account → Remote Access

# 4. Test with curl (if curl available)
curl http://192.168.1.101:32400

# 5. Try again
python manage.py process_downloads --dry-run
```

### Issue: Episodes not showing up after moving files

**Checklist**:
```powershell
# 1. Verify files are on NAS
Test-Path Z:\Library\TV Shows\<ShowName>

# 2. Give Plex time to discover (wait 30-60 seconds)
# Then check Plex web UI at http://192.168.1.101:32400

# 3. Manually trigger sync
python -c "from nstv.plexController.add_episodes_to_show import main; main()"

# 4. Check if show exists in database
python manage.py shell
# Then: from nstv.models import Show; Show.objects.get(title='<ShowName>')

# 5. If show doesn't exist, might need SHOW_ALIASES
# Edit: nstv/plexController/add_episodes_to_show.py
```

---

## 📊 Database Management

### View Database Stats
```powershell
python manage.py shell
```

```python
from nstv.models import Show, Episode, Movie

print(f"Shows: {Show.objects.count()}")
print(f"Episodes: {Episode.objects.count()}")
print(f"Episodes on disk: {Episode.objects.filter(on_disk=True).count()}")
print(f"Episodes missing: {Episode.objects.filter(on_disk=False).count()}")
print(f"Movies: {Movie.objects.count()}")
```

### Fix Missing Episodes (Mark as on_disk)
```python
# After manually moving files to Plex
from nstv.plexController.add_episodes_to_show import main as sync_episodes
sync_episodes()
```

### Reset Database (CAREFUL!)
```powershell
# Drop all data and recreate schema
python manage.py migrate nstv zero  # Revert all migrations
python manage.py migrate            # Reapply all migrations
```

---

## 🧹 Maintenance Tasks

### Check for Duplicates
```powershell
# Find duplicate episodes
python manage.py audit_episode_duplicates

# Find duplicate movies
python -c "from nstv.plexController.find_duplicates import main; main()"
```

### Enrich Metadata (from TVDB)
```powershell
python manage.py enrich_from_tvdb
# Adds: overview, ratings, genres, cast from TVDB
```

### Normalize Movie Titles
```powershell
python manage.py fix_movie_titles
```

### Run Migrations
```powershell
# See pending migrations
python manage.py showmigrations

# Create new migration (after editing models.py)
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## 👨‍💻 Development Tasks

### Create a Management Command
```powershell
python manage.py startapp myapp  # Or add to existing app

# Create: nstv/management/commands/my_command.py
```

Template:
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'What this command does'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write('DRY RUN - nothing will happen')
        # Your logic here
        self.stdout.write(self.style.SUCCESS('✓ Done!'))
```

### Add a Database Field
```python
# 1. Edit nstv/models.py
class Show(models.Model):
    # ... existing fields ...
    my_new_field = models.CharField(max_length=100, default='')

# 2. Create migration
python manage.py makemigrations

# 3. Apply migration
python manage.py migrate

# 4. Update relevant sync scripts to populate the field
```

### Run Tests
```powershell
# All tests
pytest

# Specific file
pytest tests/test_models.py

# Specific test
pytest tests/test_models.py::test_episode_creation

# Verbose
pytest -v

# With coverage
pytest --cov=nstv
```

---

## 📁 Key File Locations

| What | Where |
|------|-------|
| Main App | `nstv/` |
| Settings | `djangoProject/settings.py` |
| Models | `nstv/models.py` |
| Download Processing | `nstv/management/commands/process_downloads.py` |
| Plex Syncing | `nstv/plexController/` |
| Web Templates | `templates/` |
| Tests | `tests/` |
| Documentation | `docs/` |
| Environment | `.env` (git-ignored) |
| CLI Instructions | `.claude_instructions` |

---

## 🆘 Emergency Commands

### "Something broke, I want to debug"
```powershell
# Activate and drop into shell
python manage.py shell

# Check database state
from django.db import connection
connection.ensure_connection()
print(connection.get_autocommit())  # Should be True

# Check Plex connection
from nstv.plexController.add_shows_to_nstv import get_plex_connection
plex = get_plex_connection()
print(plex.library.sections())
```

### "I want to undo the last process_downloads"
```powershell
# Check dry-run first (in case you run it again)
python manage.py process_downloads --dry-run

# Manually move files back to NZBGet dir
# OR use Plex API to delete:
python -c "from nstv.plexController.duplicate_deletion import main; main()"
```

### "PostgreSQL won't start"
```powershell
# Windows Services
Get-Service postgresql-x64*

# Or use pg_ctl
pg_ctl start

# Or restart via Services.msc
```

---

## 📞 Common Contacts/Resources

- **Plex Server**: http://192.168.1.101:32400
- **Django Admin**: http://localhost:8000/admin (after runserver)
- **NAS Share**: \\192.168.1.101\Plex and \\192.168.1.101\Plex2
- **Plex API Key**: Plex → Settings → Account → Remote Access

---

**Keep this handy! Print it out or save as bookmark. 🎬**

