# NSTV Project Architecture & Module Reference

Complete reference guide to NSTV's codebase structure, dependencies, and module interactions.

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web UI Layer                             │
│  (templates/, views.py, Django admin)                       │
│  - Show browser with episode tracking                       │
│  - Movie browser with genre/director filtering              │
│  - Cast member detail pages                                 │
└────────┬───────────────────────────────────────┬─────────────┘
         │                                       │
         ▼                                       ▼
    ┌─────────────────────────────────────────────────┐
    │          Django ORM & Models Layer              │
    │  (models.py)                                    │
    │  - Show, Episode, Movie, CastMember             │
    │  - Relationships & QuerySet helpers             │
    └────┬────────────────────────────────┬──────────┘
         │                                │
         ▼                                ▼
    ┌────────────────┐        ┌──────────────────────┐
    │   PostgreSQL   │        │ Management Commands  │
    │   Database     │        │ (management/cmds/)   │
    │  - Show        │        │ - process_downloads  │
    │  - Episode     │        │ - audit_duplicates   │
    │  - Movie       │        │ - enrich_from_tvdb   │
    │  - CastMember  │        │ - fix_movie_titles   │
    └────────────────┘        └──────┬───────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
         ┌────────────────┐  ┌────────────────┐  ┌─────────────┐
         │ Plex API Layer │  │  File System   │  │  TVDB API   │
         │ (plexController)  │  Interaction   │  │  (get_info) │
         │ - add_shows    │  │  (process_d)   │  │             │
         │ - add_episodes │  │ - Move files   │  │ - Metadata  │
         │ - add_movies   │  │ - Path handling│  │ - Enrichment│
         │ - find_dups    │  │ - Directory mgmt  │ - Cast info │
         └────────────────┘  └────────────────┘  └─────────────┘
```

---

## 🗂️ Complete Module Reference

### 1. `djangoProject/` - Django Project Configuration

#### `settings.py`
**Purpose**: Central configuration for Django

**Key Variables**:
- `DEBUG` = True (development)
- `DATABASES` = PostgreSQL on 127.0.0.1:5432
- `INSTALLED_APPS` = django, django_tables2, nstv
- `STATIC_DIR` = `templates\static`

**Environment Variables Loaded**:
- `DJANGO_DB_PASSWORD` → PostgreSQL password
- `PLEX_*` → Plex connection details
- `NZBGET_*` → NZBGet directories
- `*_DIR` → File paths

#### `urls.py`
**Purpose**: URL routing

**Typical Routes**:
- `/nstv/` → Main index
- `/nstv/shows/` → Show list
- `/nstv/shows/<id>/` → Show detail
- `/nstv/movies/` → Movie list
- `/nstv/admin/` → Django admin

#### `wsgi.py` / `asgi.py`
**Purpose**: Application entry points for production servers

---

### 2. `nstv/` - Main Django Application

#### `models.py`
**Purpose**: Database schema and ORM definitions

**Models**:

```python
class Show(models.Model):
    gid                 # Plex unique ID
    title              # Show name
    anime              # Boolean flag
    tvdb_id            # TVDB database ID
    cast               # M2M relationship to CastMember
    # TVDB metadata
    overview, first_aired, status, network
    genre              # ArrayField (PostgreSQL)
    poster_url, rating
    
    # Key methods:
    # show.episodes.all()  # Get related episodes
    # show.episodes.filter(on_disk=True)  # Available episodes

class Episode(models.Model):
    show               # FK to Show (CASCADE delete)
    title              # Episode name
    season_number      # S01, S02, etc
    episode_number     # E01, E02, etc
    air_date           # Release date
    on_disk            # ⭐ KEY: Is it physically on the NAS?
    tvdb_id            # TVDB ID
    cast               # M2M relationship
    
    # Key methods:
    # episode.on_disk = True; episode.save()

class Movie(models.Model):
    gid                # Plex unique ID
    name               # Movie title (note: not 'title')
    release_date       # Release date
    genre              # ArrayField
    director           # Director name(s)
    on_disk            # ⭐ KEY: Is it physically on the NAS?
    poster_path        # Poster URL
    cast               # M2M relationship
    # TMDB metadata
    overview, rating

class CastMember(models.Model):
    name               # Actor/cast member name
    role               # Character or role
    image_url          # Headshot URL
    # Reverse relations: shows, episodes, movies
```

#### `views.py`
**Purpose**: HTTP request handlers (web interface)

**Key Views**:
- `show_list()` - Display all TV shows with episode progress
- `show_detail()` - Show specific show + episode grid
- `movie_list()` - Display all movies
- `movie_detail()` - Movie details + cast
- `search()` - Search shows/movies
- `health_dashboard()` - Status overview

**View Patterns**:
- Renders Django templates
- Queries models via ORM
- Passes context to templates
- Uses django-tables2 for table rendering

#### `admin.py`
**Purpose**: Django admin interface configuration

**Registers**:
- `ShowAdmin` - Show CRUD + list filters
- `EpisodeAdmin` - Episode management
- `MovieAdmin` - Movie management
- `CastMemberAdmin` - Actor management

#### `forms.py`
**Purpose**: Django form definitions (search, filters)

#### `tables.py`
**Purpose**: django-tables2 table definitions for HTML rendering

#### `download.py`
**Purpose**: Download tracking utilities (NZBDownload model, etc.)

---

### 3. `nstv/management/commands/` - Django Management Commands

#### `process_downloads.py`
**Purpose**: ⭐ CORE WORKFLOW - Move NZBGet downloads to Plex

**Command**:
```bash
python manage.py process_downloads [--dry-run] [--media-type {tv|movies|all}] [--no-sync] [--verbose]
```

**Flow**:
1. Read `NZBGET_COMPLETE_DIR`
2. Detect media type:
   - TV: Pattern `[Ss]\d{1,2}[Ee]\d{1,2}`
   - Movies: Pattern year or quality indicators
3. Extract show/movie name from filename
4. Create destination folder: `{PLEX_*_DIR}/{ShowName}/`
5. Move file to destination
6. Trigger Plex sync (calls add_shows, add_episodes, add_movies)

**Key Methods**:
- `_detect_media_type()` - Regex pattern matching
- `_extract_show_name()` - Parse show name from filename
- `_extract_movie_name()` - Parse movie name from filename
- `_process_media_type()` - Main processing loop
- `_move_items()` - File operations
- `_sync_plex_database()` - Call sync scripts

**Important Variables**:
- `TV_SHOW_PATTERN = re.compile(r'[Ss]\d{1,2}[Ee]\d{1,2}')`
- `MOVIE_PATTERN = re.compile(r'(\([\d]{4}\))...')`
- `self.dry_run` - Boolean flag to test without moving
- `self.nzbget_dir` - Source directory from env
- `self.tv_dir`, `self.movies_dir` - Destination from env

**Output**:
- Colored status messages (SUCCESS, WARNING, ERROR)
- Progress indicators [1/N]
- Summary with move count

#### `audit_episode_duplicates.py`
**Purpose**: Find and list duplicate episodes

**Command**:
```bash
python manage.py audit_episode_duplicates [--verbose] [--delete]
```

**Algorithm**:
1. Query all episodes
2. Group by (show, season_number, episode_number)
3. Identify groups with count > 1
4. Report or delete (with --delete)

#### `enrich_from_tvdb.py`
**Purpose**: Populate metadata from TVDB API

**Command**:
```bash
python manage.py enrich_from_tvdb [--show-id <id>]
```

**Operations**:
- Query TVDB API for show metadata
- Update Show: overview, status, network, rating, etc.
- Update Episode: air_date, cast
- Create CastMember relationships

#### `fix_movie_titles.py`
**Purpose**: Normalize movie title formatting

**Command**:
```bash
python manage.py fix_movie_titles
```

**Operations**:
- Clean up movie names (remove extra spaces, punctuation)
- Standardize formatting
- Merge duplicate movie records

---

### 4. `nstv/plexController/` - Plex Integration

#### `add_shows_to_nstv.py`
**Purpose**: Sync TV shows from Plex → Django database

**Entry Point**:
```python
def main():
    plex = get_plex_connection()
    plex_tv_shows = plex.library.section('TV Shows')
    for plex_show in plex_tv_shows.search():
        # Create/update Show in Django
```

**Algorithm**:
1. Connect to Plex API
2. Query 'TV Shows' library section
3. For each show:
   - Get show title (check SHOW_ALIASES)
   - Create or update Show object
   - Store: title, tvdb_id, genre, poster, etc.

**Key Variables**:
- `SHOW_ALIASES` dict - Maps Plex title → Django title
- `plex.friendlyName` - Plex server name

#### `add_episodes_to_show.py`
**Purpose**: Sync episodes from Plex → Django database

**Entry Point**:
```python
def main():
    plex = get_plex_connection()
    plex_tv_shows = plex.library.section('TV Shows')
    for plex_show in tqdm(plex_tv_shows.search()):
        add_existing_episodes_for_plex_show(plex_show)
```

**Algorithm**:
1. For each show in Plex:
   - Find or create matching Show in Django
   - For each episode in Plex show:
     - Match to Django Episode (by title + season + episode)
     - Set `on_disk=True`
     - Update or create

**Key Handling**:
- `SEASON_TITLE_REPLACEMENTS` - Handle non-standard season numbering
  - Example: "S2010" → "S01" for Running Man
- Episode matching: TVDB ID → season/episode → normalized title
- Deduplication: Check existing before creating

#### `add_movies_to_nstv.py`
**Purpose**: Sync movies from Plex → Django database

**Similar to add_shows_to_nstv but for Movies**

#### `find_duplicates.py`
**Purpose**: Detect duplicate episodes/movies

**Key Class**: `DuplicateFinder`

**Methods**:
- `find_duplicate_episodes()` - Same show/season/episode
- `find_duplicate_movies()` - Same title + year
- `rank_quality()` - Score by resolution, codec, bitrate

**Returns**: List of `DuplicateGroup` objects with duplicates ranked

#### `duplicate_deletion.py`
**Purpose**: Delete duplicates via Plex API

**Algorithm**:
1. Find duplicates (calls find_duplicates.py)
2. Rank by quality
3. Delete lower-quality versions via Plex API
4. Update Django: set `on_disk=False`

**Important**: Uses Plex API deletion, not local file deletion

#### `quality_analyzer.py`
**Purpose**: Analyze and rank media quality

**Ranking Criteria**:
1. Resolution: 4K > 1080p > 720p > 480p
2. Codec: x265/HEVC > x264/H264
3. Bitrate: Higher is better

**Output**: Quality score for ranking

#### `plexDance.py`
**Purpose**: Utility functions for Plex interaction

**Functions**:
- `get_plex_connection()` - Create PlexServer connection
- `movie_or_show()` - Detect media type
- `find_library_by_name()` - Get library section by name

---

### 5. `nstv/get_info_from_tvdb/` - TVDB Integration

**Purpose**: Query TVDB API for metadata enrichment

**Key Functions**:
- `search_show()` - Find show by name
- `get_show_info()` - Get show details
- `get_episode_info()` - Get episode details
- `get_cast()` - Get cast information

**API Details**:
- Uses `tvdb-v4-official` package
- Returns structured data for DB storage

---

### 6. `nstv/tests/` - Test Suite

#### `unit/` - Unit tests
**Example**:
- Test model creation: `test_show_creation()`
- Test model relationships: `test_episode_to_show()`
- Test filename parsing: `test_detect_media_type()`

#### `integration/` - Integration tests
**Example**:
- Test full download processing: `test_process_downloads()`
- Test Plex sync: `test_sync_shows_to_db()`
- Test duplicate detection: `test_find_duplicates()`

**Run Tests**:
```bash
pytest
pytest -v
pytest tests/test_models.py::test_episode_creation
```

---

### 7. `templates/` - HTML Templates

#### `base.html`
**Purpose**: Main layout with navigation and styling

#### `show_list.html`
**Purpose**: Display all TV shows with thumbnails

**Variables**: `shows` (QuerySet of Show objects)

#### `show_detail.html`
**Purpose**: Show detail page with episode grid

**Features**:
- Season selector
- Episode grid (green=on_disk, red=missing)
- Completion percentage
- Cast information

#### `movie_list.html`
**Purpose**: Display all movies

**Features**:
- Genre filtering
- Director filtering
- Search

#### `movie_detail.html`
**Purpose**: Movie detail page

**Features**:
- Poster and metadata
- Director and cast
- Related movies

#### `static/` - CSS, JavaScript, images
- `style.css` - Main styling
- `script.js` - Client-side interactions
- `images/` - Posters, icons, etc.

---

## 🔄 Data Flow Diagrams

### Flow 1: Download Processing
```
NZBGet Complete Dir
    ↓ [process_downloads command]
    ├─ Detect: regex S##E## or year
    ├─ Extract: show/movie name
    ├─ Create: destination folder
    └─ Move: file to destination
    ↓ [Plex auto-discovery] (30-60s)
    ↓ [add_shows_to_nstv]
    └─ Create/update: Show objects
    ↓ [add_episodes_to_show]
    └─ Create/update: Episode objects + on_disk=True
    ↓ [Web UI refresh]
    └─ New episode appears in green
```

### Flow 2: Duplicate Detection
```
Plex API Query
    ↓ [find_duplicates.py]
    ├─ Group: same title + season/episode
    ├─ Rank: quality (resolution, codec, bitrate)
    └─ Output: DuplicateGroup list
    ↓ [User review or auto-delete]
    ↓ [duplicate_deletion.py]
    ├─ Delete: via Plex API
    └─ Update: Django on_disk=False
```

### Flow 3: TVDB Enrichment
```
Django Show objects
    ↓ [enrich_from_tvdb command]
    ├─ Search: TVDB API by title
    ├─ Fetch: show metadata (overview, rating, cast)
    └─ Update: Show fields
    ↓ [TVDB Episode data]
    ├─ Fetch: episode details + air_date
    └─ Update: Episode fields
```

---

## 🔌 Dependencies & External Services

### Python Packages
```
Django==5.2.11              # Web framework
PlexAPI==4.18.0             # Plex API client
tvdb-v4-official==1.1.0     # TVDB API client
psycopg2-binary==2.9.11     # PostgreSQL adapter
django-tables2==2.8.0       # Table rendering
python-dotenv==1.2.1        # .env file loading
pytest==9.0.2               # Testing framework
pytest-django==4.12.0       # Django testing plugin
requests==2.32.5            # HTTP client
```

### External Services
```
Plex Server
  ├─ Address: 192.168.1.101:32400 (configurable)
  ├─ API: PlexAPI (Python wrapper)
  └─ Auth: API key from Plex account
  
TVDB (The Video Database)
  ├─ API: https://v4.thetvdb.com
  ├─ Purpose: Metadata enrichment
  └─ Auth: API key (via tvdb-v4-official)
  
PostgreSQL Database
  ├─ Host: 127.0.0.1:5432 (local)
  ├─ Auth: username=postgres, password from DJANGO_DB_PASSWORD
  └─ Tables: show, episode, movie, cast_member, etc.
  
NZBGet (Optional)
  ├─ Path: C:\ProgramData\NZBGet\complete
  ├─ Function: Download directory source
  └─ Integration: process_downloads reads from here
```

---

## 🚀 Execution Paths

### User Initiates Download Processing
```
1. User runs: python manage.py process_downloads --dry-run
2. Django loads settings from .env
3. Command.handle() checks environment variables
4. _validate_config() verifies all paths exist
5. _check_plex_connection() tests Plex API
6. _process_media_type('tv', Z:\Library\TV Shows) loops items
7. For each item:
   a. _detect_media_type() checks filename patterns
   b. _extract_show_name() parses name
   c. _move_items() moves file (or dry-run shows)
8. _sync_plex_database() calls add_shows, add_episodes (unless --no-sync)
9. Output summary with counts
```

### Plex Discovers New File
```
1. File appears in Z:\Library\TV Shows\ShowName\
2. Plex scans directory (30-60s, configurable)
3. Plex identifies media and indexes
4. Plex creates episode object in 'TV Shows' library
```

### User Syncs Database
```
1. User runs: python -c "from nstv.plexController.add_episodes_to_show import main; main()"
2. Script connects to Plex API
3. For each show in Plex library:
   a. Find Django Show by title
   b. For each episode in Plex show:
      i. Match to Django Episode (by season/episode)
      ii. Set on_disk=True
      iii. Save to database
4. Script outputs: Created X, Updated Y
```

---

## 📝 Common Code Patterns

### Connecting to Plex
```python
from plexapi.server import PlexServer
import os

plex_server = os.getenv('PLEX_SERVER')  # http://192.168.1.101:32400
plex_api_key = os.getenv('PLEX_API_KEY')

plex = PlexServer(plex_server, plex_api_key)
tv_library = plex.library.section('TV Shows')
```

### Querying Django ORM
```python
from nstv.models import Show, Episode

# Get all shows
shows = Show.objects.all()

# Get specific show
show = Show.objects.get(title='Breaking Bad')

# Get related episodes
episodes = show.episodes.all()
missing_episodes = episodes.filter(on_disk=False)

# Create new episode
episode = Episode.objects.create(
    show=show,
    season_number=5,
    episode_number=16,
    title="Felina",
    on_disk=True
)

# Update multiple
Episode.objects.filter(show=show).update(on_disk=True)

# Filter with Q objects
from django.db.models import Q
anime_shows = Show.objects.filter(Q(anime=True) | Q(genre__contains='Anime'))
```

### File Path Handling
```python
import os
from pathlib import Path

# Using os.path
source = os.path.join(base_dir, item_name)
dest = os.path.join(plex_dir, show_name, item_name)
shutil.move(source, dest)

# Using pathlib (modern)
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
```

### Regex Patterns
```python
import re

TV_PATTERN = re.compile(r'[Ss]\d{1,2}[Ee]\d{1,2}', re.IGNORECASE)
MOVIE_PATTERN = re.compile(r'(\([\d]{4}\))|(\[[\d]{4}\])|(\d{4}\s*(?:1080p|720p))', re.IGNORECASE)

if TV_PATTERN.search(filename):
    # It's a TV show
    
show_name = re.sub(r'[Ss]\d{1,2}[Ee]\d{1,2}.*', '', filename).strip()
```

### Management Command Output
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('[OK] Success message'))
        self.stdout.write(self.style.WARNING('[WARN] Warning message'))
        self.stdout.write(self.style.ERROR('[FAIL] Error message'))
        self.stdout.write('Normal message')
```

---

## 🔍 Debugging Tips

### Check Environment
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('PLEX_SERVER'))"
```

### Test Plex Connection
```python
python manage.py shell
>>> from nstv.plexController.plexDance import get_plex_connection
>>> plex = get_plex_connection()
>>> print(plex.friendlyName)
```

### Check Database
```python
python manage.py shell
>>> from nstv.models import Show, Episode
>>> Show.objects.count()
>>> Episode.objects.filter(on_disk=False).count()
```

### View Django Logs
```python
# Add to settings.py for logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'nstv': {'level': 'DEBUG', 'handlers': ['console']},
    },
}
```

---

**Last Updated**: March 21, 2026
**For**: Solo developer (Nick)
**Reference**: See DEVELOPER_GUIDE.md for practical examples

