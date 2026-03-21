# NSTV Developer Guide

A comprehensive guide for working with the NSTV project - a Django-based Plex media library manager.

## Quick Navigation

- **[Project Overview](#project-overview)** - What this project does
- **[Architecture](#architecture)** - How it's structured
- **[Environment Setup](#environment-setup)** - Getting started
- **[Common Tasks](#common-tasks)** - Day-to-day workflows
- **[Database & Models](#database--models)** - Data structure
- **[Plex Integration](#plex-integration)** - How Plex sync works
- **[Troubleshooting](#troubleshooting)** - Common issues

---

## Project Overview

**NSTV** = **N**etflix-**S**tyle **T**V manager - A personal media library interface built on Django.

### What It Does

1. **Syncs** TV shows, episodes, and movies from your Plex server
2. **Enriches** metadata from TVDB (The Movie Database)
3. **Tracks** episode availability on disk
4. **Processes** downloads automatically from NZBGet
5. **Detects & removes** duplicate media based on quality
6. **Provides** a web interface to browse your library

### Key Features

- 📺 TV show tracking with episode-level granularity
- 🎬 Movie library management
- 🔄 Automatic download processing and file movement
- 🧹 Duplicate detection and deletion with quality ranking
- 👥 Cast member tracking
- 🏷️ Genre and director filtering
- 📊 Visual episode availability tracking
- 🎭 Anime detection

---

## Architecture

### Directory Structure

```
nstv/
├── djangoProject/          # Django project configuration
│   ├── settings.py         # Main settings (env variables, databases, installed apps)
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # Production WSGI server
│   └── asgi.py             # Async WSGI
│
├── nstv/                   # Main Django app
│   ├── models.py           # Database models (Show, Episode, Movie, CastMember)
│   ├── views.py            # Web interface views
│   ├── admin.py            # Django admin configuration
│   ├── forms.py            # Form definitions
│   ├── tables.py           # django-tables2 configurations
│   │
│   ├── management/commands/    # Django management commands
│   │   ├── process_downloads.py        # Core: Move files from NZBGet to Plex
│   │   ├── audit_episode_duplicates.py # Detect duplicate episodes
│   │   ├── enrich_from_tvdb.py         # Enrich metadata from TVDB
│   │   └── fix_movie_titles.py         # Movie title corrections
│   │
│   ├── plexController/         # Plex integration logic
│   │   ├── add_shows_to_nstv.py        # Sync shows from Plex → Django
│   │   ├── add_episodes_to_show.py     # Sync episodes from Plex → Django
│   │   ├── add_movies_to_nstv.py       # Sync movies from Plex → Django
│   │   ├── find_duplicates.py          # Duplicate detection algorithm
│   │   ├── duplicate_deletion.py       # Remove duplicates via Plex API
│   │   ├── quality_analyzer.py         # Rank duplicate quality
│   │   └── plexDance.py                # Utility functions
│   │
│   ├── get_info_from_tvdb/     # TVDB metadata enrichment
│   ├── kissasian/              # External scraper (legacy?)
│   ├── dramacool/              # External scraper (legacy?)
│   └── tests/                  # Unit & integration tests
│
├── templates/              # HTML templates
│   ├── base.html           # Main layout
│   ├── show_list.html      # TV show browser
│   ├── movie_list.html     # Movie browser
│   └── static/             # CSS, JS, images
│
├── docs/                   # Documentation (this file, architecture, etc.)
├── scripts/                # Utility scripts
├── .env                    # Environment variables (NOT in git)
├── manage.py               # Django CLI
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Python dependencies
```

### Data Flow

```
NZBGet Download Directory
    ↓
[process_downloads command]
    ↓
Move to Z:\Library\{TV Shows|Movies}
    ↓
[Plex auto-discovery]
    ↓
Plex Library (on NAS)
    ↓
[Plex API] → [add_shows_to_nstv, add_episodes_to_show, add_movies_to_nstv]
    ↓
Django Database (PostgreSQL)
    ↓
[Enrich from TVDB] + [Detect duplicates] + [Track availability]
    ↓
Web UI (Django views + templates)
```

### Key Models

```python
Show
  ├── title (required)
  ├── tvdb_id
  ├── anime (boolean)
  ├── overview, first_aired, status, network
  ├── genre (array), poster_url, rating
  └── cast (ManyToMany) → CastMember

Episode
  ├── show (ForeignKey)
  ├── title, season_number, episode_number
  ├── air_date, tvdb_id
  ├── on_disk (boolean) ← KEY: tracks if available
  └── cast (ManyToMany) → CastMember

Movie
  ├── name (title), release_date
  ├── genre (array), director
  ├── on_disk (boolean) ← KEY: tracks if available
  ├── overview, rating
  ├── poster_path
  └── cast (ManyToMany) → CastMember

CastMember
  ├── name, role
  └── image_url
```

---

## Environment Setup

### Prerequisites

- Python 3.9+ (with venv)
- PostgreSQL 12+ (local or remote)
- Plex server (running on your NAS)
- NZBGet (optional, for download automation)
- Windows network drives mapped:
  - `Y:\` = Plex library (SHOW_FOLDER_PATH reference)
  - `Z:\` = Plex2 library (where downloads go)

### Step 1: Clone & Install

```powershell
cd C:\Users\Nick\PycharmProjects\nstv

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure `.env`

Create `.env` file in project root:

```dotenv
# Django
DJANGO_DB_PASSWORD=admin

# Plex Server Connection
PLEX_EMAIL=your-email@example.com
PLEX_API_KEY=your-plex-api-key
PLEX_SERVER=http://192.168.1.101:32400

# File Paths (Windows network drives)
SHOW_FOLDER_PATH="Y:\Library\TV Shows"
PLEX_TV_SHOW_DIR="Z:\Library\TV Shows"
PLEX_MOVIES_DIR="Z:\Library\Movies"

# NZBGet Directories
NZBGET_COMPLETE_DIR=C:\ProgramData\NZBGet\complete
NZBGET_NZB_DIR=C:\ProgramData\NZBGet\nzb

# Optional
TEMP_FOLDER_PATH=
```

### Step 3: Database Setup

```powershell
# Run migrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser

# Start Django dev server
python manage.py runserver
```

Visit: http://localhost:8000/nstv

---

## Common Tasks

### 1. Process Downloads (Core Workflow)

Move completed NZB downloads from NZBGet to Plex:

```powershell
# Dry run (see what would be moved)
python manage.py process_downloads --dry-run

# Actually process
python manage.py process_downloads

# Process only TV shows
python manage.py process_downloads --media-type tv

# Process only movies
python manage.py process_downloads --media-type movies

# Skip Plex sync (move files only)
python manage.py process_downloads --no-sync

# Verbose output
python manage.py process_downloads --verbose
```

**What it does:**
1. Reads `C:\ProgramData\NZBGet\complete` directory
2. Detects if each item is TV (S##E## pattern) or Movie (year or quality indicators)
3. Moves items to:
   - TV: `Z:\Library\TV Shows\[ShowName]\[item]`
   - Movies: `Z:\Library\Movies\[MovieName]\[item]`
4. Triggers Plex sync to database

### 2. Sync Plex to Database

Import shows/episodes/movies from Plex into Django:

```powershell
# Sync TV shows
python -c "from nstv.plexController.add_shows_to_nstv import main; main()"

# Sync episodes for all shows
python -c "from nstv.plexController.add_episodes_to_show import main; main()"

# Sync movies
python -c "from nstv.plexController.add_movies_to_nstv import main; main()"

# All at once
python manage.py process_downloads --dry-run  # Includes syncs
```

### 3. Find & Delete Duplicates

```powershell
# Find duplicate episodes
python manage.py audit_episode_duplicates

# Find duplicate movies (via Plex API)
python -c "from nstv.plexController.find_duplicates import main; main()"

# Delete duplicate episodes (keeps best quality)
python -c "from nstv.plexController.duplicate_deletion import main; main()"
```

### 4. Enrich Metadata

Add TVDB metadata to shows:

```powershell
python manage.py enrich_from_tvdb
```

### 5. Fix Movie Titles

Normalize movie title formatting:

```powershell
python manage.py fix_movie_titles
```

### 6. Run Tests

```powershell
# All tests
pytest

# Specific test file
pytest tests/test_models.py -v

# With Django settings
pytest --ds=djangoProject.settings
```

---

## Database & Models

### Key Concepts

**on_disk Field**: Boolean flag indicating if media is physically available on the NAS. Set by:
- `process_downloads` → True (when moved to Plex directory)
- `add_episodes_to_show` → True (when scanned from Plex)
- `duplicate_deletion` → False or deleted (when removed)

**TVDB Enrichment**: Metadata like overview, ratings, cast comes from TVDB (The Movie Database):
- Show: `Show.overview`, `Show.status`, `Show.network`, `Show.genre`, `Show.rating`
- Episode: Matched by `tvdb_id` or season/episode numbers
- Movie: Matched by release date and name

**Episode Matching**: 3-tier matching strategy:
1. By TVDB ID (most reliable)
2. By season/episode numbers + title
3. By normalized title (handles filename variations)

**Duplicates**: Same episode/movie in multiple quality levels:
- Detected by: Same show + season + episode (episodes) or title + year (movies)
- Ranked by: Resolution, codec, bitrate
- Kept: Highest quality version
- Deleted: Lower quality duplicates

### Database Queries (Django Shell)

```powershell
python manage.py shell
```

Then in the Python shell:

```python
from nstv.models import Show, Episode, Movie, CastMember

# Find a show
show = Show.objects.get(title='Breaking Bad')

# Get all episodes for a show
episodes = show.episodes.all()

# Episodes not on disk
missing = show.episodes.filter(on_disk=False)

# TV shows with anime flag
anime_shows = Show.objects.filter(anime=True)

# Movies by director
movies = Movie.objects.filter(director='Christopher Nolan')

# Find duplicates
from collections import Counter
duplicate_episodes = [
    ep for ep in Episode.objects.all() 
    if Episode.objects.filter(
        show=ep.show,
        season_number=ep.season_number,
        episode_number=ep.episode_number
    ).count() > 1
]
```

---

## Plex Integration

### How Plex Connection Works

1. **API Key**: Get from Plex web UI → Settings → Account → Remote Access
2. **Server URL**: Format: `http://192.168.1.101:32400` (IP of Plex server)
3. **Connection**: PlexAPI library handles authentication and queries

### Plex Sync Flow

```
[Plex Server on NAS]
    ↓ (PlexAPI queries)
[add_shows_to_nstv.py]
    └─ plex.library.section('TV Shows').search()
    └─ Creates Show objects, stores title + metadata
    
[add_episodes_to_show.py]
    └─ plex_show.episodes()
    └─ Creates Episode objects, sets on_disk=True
    └─ Matches with existing Django Episodes
    
[add_movies_to_nstv.py]
    └─ plex.library.section('Movies').search()
    └─ Creates Movie objects, sets on_disk=True
```

### Handling Title Mismatches

Some shows have multiple names. Handle with `SHOW_ALIASES`:

```python
# In add_episodes_to_show.py
SHOW_ALIASES = {
    'Plex Title': 'Django Title',
    '6ixtynin9 the Series': '6ixtynin9',
}
```

### Season Number Mapping

Some shows (esp. non-English) have non-standard season numbering:

```python
# In add_episodes_to_show.py
SEASON_TITLE_REPLACEMENTS = {
    'Running Man': {
        'S2010': 'S01',
        'S2011': 'S02',
        # ...maps year-based seasons to numeric
    },
}
```

---

## Troubleshooting

### "TV directory not found: Z:\Library\TV Shows"

**Problem**: Network drive not mapped or path doesn't exist
**Solution**:
1. Open File Explorer → "This PC"
2. Map network drive:
   - Drive: `Z:`
   - Path: `\\192.168.1.101\Plex2` (or your NAS path)
   - Check "Reconnect at sign-in"
3. Verify `.env` has correct paths
4. Restart terminal/Python

### "Cannot connect to Plex server"

**Problem**: Plex API credentials wrong or server not running
**Solution**:
1. Verify `PLEX_SERVER` format: `http://192.168.1.101:32400`
2. Verify `PLEX_API_KEY` is valid (get from Plex → Settings → Account)
3. Ping Plex server: `ping 192.168.1.101` or visit in browser
4. Check firewall isn't blocking port 32400

### "Database connection refused"

**Problem**: PostgreSQL not running or connection details wrong
**Solution**:
1. Start PostgreSQL: `pg_ctl start` or use Services
2. Verify `DJANGO_DB_PASSWORD` matches your DB password
3. Check `HOST` is `127.0.0.1` or correct remote IP
4. Test connection: `psql -U postgres -h 127.0.0.1`

### Episodes not syncing

**Problem**: Episodes not appearing in Django after adding to Plex
**Solution**:
1. Run: `python manage.py process_downloads` (includes sync)
2. Or manually sync: `python -c "from nstv.plexController.add_episodes_to_show import main; main()"`
3. Check episode titles match Plex exactly
4. Check for `SHOW_ALIASES` mismatch (case-sensitive)
5. Check `SEASON_TITLE_REPLACEMENTS` for unusual season numbering

### Duplicates not detected

**Problem**: Same show/episode exists multiple times but not detected
**Solution**:
1. Check episode is actually marked as same season/episode in Plex
2. Check `.on_disk` flag is set (run sync first)
3. Run: `python manage.py audit_episode_duplicates --verbose`
4. Check filename patterns match detection regex

---

## Useful Commands Quick Reference

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Process downloads with dry-run
python manage.py process_downloads --dry-run

# Full sync (shows + episodes + movies)
python manage.py process_downloads

# Django shell (interactive)
python manage.py shell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest

# Check for issues
python manage.py check

# Start dev server
python manage.py runserver
```

---

## Contributing to NSTV

### Code Style

- Python: PEP 8 (black formatter)
- Django: Follow Django conventions
- Comments: Explain WHY, not WHAT
- Type hints: Use when possible

### Adding Features

1. Create feature branch: `git checkout -b feature/my-feature`
2. Add tests first (TDD)
3. Implement feature
4. Run: `pytest` to verify
5. Update relevant documentation
6. Commit and create PR

### Testing

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Run: `pytest --ds=djangoProject.settings -v`

---

## Next Steps

- Explore the web UI: http://localhost:8000/nstv
- Check `docs/` folder for specific guides
- Review models in `nstv/models.py`
- Look at `process_downloads.py` for the main workflow

Happy coding! 🎬📺

