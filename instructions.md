# Development Instructions

## Overview
Django app tracking TV shows/episodes/movies, syncing with Plex server.

## ⚠️ Windows/PowerShell ONLY
This project runs on Windows with PowerShell. Unix/Bash commands **WILL NOT WORK**.

**Command equivalents** (full reference: `docs/POWERSHELL_COMMAND_REFERENCE.md`):
| Unix | PowerShell |
|------|-----------|
| `grep "text" file` | `Select-String "text" file` |
| `ls -la` | `Get-ChildItem -Force` |
| `find . -name "*.py"` | `Get-ChildItem -Recurse -Include "*.py"` |
| `test -f file` | `Test-Path file` |
| `cat file` | `Get-Content file` |

## Core Rules
- Keep changes minimal, scoped to request
- Prefer updating existing files over new abstractions
- No hardcoded secrets/credentials/paths
- Use environment variables for config
- Add/adjust tests for behavior changes

## Git Workflow
**Branching**: Use `feature/<name>` or `bugfix/<name>` for non-trivial changes
**Commits**: Present tense, descriptive ("Add feature" not "Added feature")
**Messages**: Include what/why, reference issues

## Setup
1. Activate venv
2. `.env` has required keys (see `.env.example`)
3. Run migrations: `python manage.py migrate`
4. Verify: `python manage.py check`

## Plex Sync
**Components**:
- `nstv/plexController/add_shows_to_nstv.py`
- `nstv/plexController/add_episodes_to_show.py`
- `nstv/plexController/add_movies_to_nstv.py`
- `nstv/plexController/plexDance.py`

**Rules**:
- Read Plex config from environment variables
- Don't connect at module import time
- Keep functions testable via dependency injection
- Handle missing optional data (genres/directors/posters)

## Download & File Management
**Status**: NZBGet integration disabled - use manual processing

**Manual processing**:
```powershell
.venv\Scripts\python.exe manage.py process_downloads
# Options: --dry-run, --media-type=tv|movies|all, --no-sync, --verbose
```

**Safety features**:
- Plex connectivity check before processing
- Cross-drive file movement (C: → Y:) with progress tracking
- Source files removed only after successful copy

**Background Threading Pattern**:
```python
thread = threading.Thread(target=operation_function, args=(arg1, request), daemon=True)
thread.start()
messages.info(request, "Operation started.")
return redirect(request.META.get('HTTP_REFERER'))
```

**Flow**:
1. User clicks download → NZBGeek search → Download NZB to ~/Downloads
2. Move NZB to NZBGet watch directory → Monitor history for completion
3. Move files to Plex → Sync episodes automatically → Return status via messages

**Quality Filtering**: Movies (all qualities), TV (HD with fallback), Anime (exclude English-only audio)

## Environment Variables
- `DJANGO_DB_PASSWORD`, `PLEX_EMAIL`, `PLEX_API_KEY`, `PLEX_SERVER`
- `TVDB_API_KEY`, `NZBGEEK_USERNAME`, `NZBGEEK_PASSWORD`
- `NZBGET_NZB_DIR`, `NZBGET_COMPLETE_DIR`, `PLEX_TV_SHOW_DIR`, `PLEX_MOVIES_DIR`
- `SHOW_FOLDER_PATH`, `TEMP_FOLDER_PATH`

## Testing & Verification
```powershell
python manage.py check           # Django health
python manage.py migrate         # Run migrations
python -m pytest nstv/tests -q   # Run tests
python manage.py runserver       # Start dev server
```

## Architecture
```
nstv/
├── models.py                  # Django models
├── views.py                   # Web handlers
├── download.py                # NZBGeek integration
├── management/commands/       # CLI commands
├── plexController/            # Plex server integration
├── get_info_from_tvdb/       # TVDB metadata
└── utils/
templates/                     # Django HTML
scripts/                       # Automation scripts
docs/                         # Documentation
```

**Data Models**:
- `Show`, `Episode`, `Movie`, `CastMember` (many-to-many)
- `NZBDownload`, `DuplicateDeletionLog`

## Documentation
- **New users**: Start with `QUICK_START.md`
- **Setup**: `docs/DEPLOYMENT.md`
- **Tasks**: `docs/MANUAL_TASKS.md`
- **PowerShell**: `docs/POWERSHELL_COMMAND_REFERENCE.md`
- **Archive**: `docs/archive/` (local reference only)
**Usage**:
```bash
# Process all downloads
python manage.py process_downloads

# Dry run to preview
python manage.py process_downloads --dry-run --verbose

# Process only TV shows
python manage.py process_downloads --media-type=tv

# Move files without syncing database
python manage.py process_downloads --no-sync
```

**What it does**:
1. Checks Plex server is accessible
2. Scans `NZBGET_COMPLETE_DIR` for completed downloads
3. Moves files to `PLEX_TV_SHOW_DIR` or `PLEX_MOVIES_DIR`
4. Syncs Django database with new media from Plex
5. Removes source files after successful move

**Error Handling**:
- Aborts gracefully if Plex offline (files remain for retry)
- Skips files that already exist at destination
- Logs detailed progress for large file transfers

**See**: `docs/POST_DOWNLOAD_AUTOMATION.md` for full documentation

### audit_episode_duplicates
Detect and optionally fix duplicate episodes in the database.

Usage:
```bash
# Dry run - show duplicates
python manage.py audit_episode_duplicates

# Fix duplicates by merging
python manage.py audit_episode_duplicates --fix

# Audit specific show
python manage.py audit_episode_duplicates --show-id 123
```

Merge logic preserves:
- Episodes with `on_disk=True`
- Episodes with TVDB ID
- Most descriptive titles
- Air dates and episode numbers

### find_duplicates & duplicate_deletion (NEW)
**Web UI**: `/duplicates/` - Scan for and delete duplicate media files

Detects duplicate versions of the same episode/movie in Plex library:
- **Single episode with multiple media files** (Plex's native duplicate structure)
- **Cross-episode duplicates** (same show/season/episode from different scans)
- **Quality-based ranking** via resolution, codec, bitrate analysis

**Quality Scoring**:
- Resolution: 4K=100, 1080p=80, 720p=60, SD=40
- Codec: HEVC=20, H.264=15, others=10
- Bitrate: Higher is better (normalized score)
- Audio codec: Various formats scored

**Deletion**:
- Uses Plex API `media.delete()` for remote NAS file management
- Windows client can delete files on Linux NAS without direct filesystem access
- Logs all deletions to `DuplicateDeletionLog` model for audit trail
- Refreshes Plex library after deletion

**Important Fixes**:
- Groups by `show.ratingKey` not `show.title` to avoid matching different shows with same name (e.g., "The Twilight Zone (1959)" vs "(2019)")
- Uses `media.delete()` not `removeMedia()` (which doesn't exist in PlexAPI)

**Related Files**:
- `nstv/plexController/find_duplicates.py` - Detection logic
- `nstv/plexController/duplicate_deletion.py` - Deletion via Plex API
- `nstv/plexController/quality_analyzer.py` - Quality scoring
- `nstv/views.py` - Web interface handlers
- `nstv/models.py` - `DuplicateDeletionLog` model

**See**: Scan takes 2-3 minutes for ~100 shows. Quality scores help identify which version to keep.

## TVDB Import

### Deduplication Strategy
`nstv/get_info_from_tvdb/main.py` uses three-tier matching to prevent duplicates:

1. **TVDB ID match**: If episode has tvdb_id, update existing record
2. **Season/Episode number match**: Canonical identifier (S01E01)
3. **Normalized title match**: Fuzzy matching for edge cases

After import, `merge_duplicate_episodes_for_show()` cleans up any remaining duplicates.

## Movie Data Quality

### Title & Release Date Handling
Movies imported from Plex may have years embedded in titles (e.g., "Red River 1948").

**Automatic Cleaning**: `plexController/add_movies_to_nstv.py` automatically:
1. Detects year patterns at end of title: `\s*[\(]?(\d{4})[\)]?\s*$`
2. Extracts year if in valid range (1900 to current year + 5)
3. Stores cleaned title without year
4. Populates `release_date` if Plex doesn't provide `originallyAvailableAt`

**Pattern**:
```python
# Input: "Red River 1948"
# Output: name="Red River", release_date=date(1948, 1, 1)

# Input: "The Matrix (1999)"  
# Output: name="The Matrix", release_date=date(1999, 1, 1)
```

### fix_movie_titles Management Command
Clean existing movies with years in titles:

```bash
# Dry run - show what would change
python manage.py fix_movie_titles --dry-run

# Apply fixes
python manage.py fix_movie_titles
```

The command:
- Scans all movies for year patterns in title
- Extracts year to `release_date` if field is empty
- Updates title to remove year
- Preserves existing release dates

## Views & Data Presentation

### Health Status Dashboard (shows_index)
The TV shows index displays a health status dashboard instead of a traditional table:

**Data Structure**: View builds nested dictionaries with:
- Shows → Seasons → Episodes
- Availability tracking (on_disk boolean)
- Progress calculations (available/total, percentages)
- Sorted by season/episode number (None values sorted last)

**Pattern**:
```python
shows_data.append({
    'id': show.id,
    'title': show.title,
    'seasons': sorted_seasons,  # Each season has episodes list
    'total_episodes': total_episodes,
    'available_episodes': available_episodes,
    'overall_percentage': overall_percentage
})
```

**Sorting with None values**:
```python
# Put None values at end, sort others numerically
season['episodes'].sort(key=lambda x: (x['number'] is None, x['number'] or 0))
```

### Genre/Director Filtering (movies)
Movies can be filtered by genre or director using dedicated views:

**Views**: 
- `movies_by_genre(request, genre)` - Uses `Movie.objects.filter(genre__contains=[genre])`
- `movies_by_director(request, director)` - Uses `Movie.objects.filter(director__iexact=director)`

**URL Patterns**:
- `/movies/genre/<str:genre>`
- `/movies/director/<str:director>`

**Template Context**: Pass `filter_type` and `filter_value` to show active filter with clear option

## Common Workflow
1. Implement smallest functional change.
2. Run targeted tests.
3. Run Django checks.
4. Summarize what changed and any follow-up steps.
