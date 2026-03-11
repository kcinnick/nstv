# Claude Sonnet 4.5 Instructions

## Purpose
This repository is a Django app (`nstv`) used to track TV shows, episodes, and movies and sync that data from a local Plex server.

## Documentation
- **Backend/Python**: This file (instructions.md)
- **Frontend/UI**: See `frontend-design-guidelines.md` for HTML/CSS design system

## Core Rules
- Keep changes minimal and scoped to the user request.
- Prefer updating existing files over adding new abstractions.
- Do not hardcode secrets, credentials, or local machine paths.
- Use environment variables for runtime configuration.
- Add/adjust tests for behavior changes.

## Git Workflow

### Branching Strategy
**Always use feature/bugfix branches when working on non-trivial changes.**

- **Features**: `feature/<descriptive-name>` (e.g., `feature/health-dashboard`)
- **Bug Fixes**: `bugfix/<descriptive-name>` (e.g., `bugfix/movie-title-year-extraction`)
- **Hotfixes**: `hotfix/<descriptive-name>` (for urgent production fixes)

### Branch Creation Rules
1. **New Features**: Always create a feature branch from `master`
2. **Bug Fixes**: If not already on a feature branch, create a `bugfix/` branch from `master`
3. **Small Typos/Docs**: Can be committed directly to current branch if already on a feature branch

### Workflow
```bash
# Check current branch
git branch --show-current

# Create new branch if on master
git checkout -b feature/my-feature  # or bugfix/my-fix

# Make changes, commit frequently
git add -A
git commit -m "Descriptive commit message"

# When complete, merge or create PR
```

### Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Be descriptive: Include what changed and why
- Reference issues if applicable

## Local Setup
1. Activate virtual environment.
2. Ensure `.env` has required keys (see `.env.example`).
3. Run migrations before starting server.

## Verification Commands
- `venv\Scripts\python.exe manage.py check`
- `venv\Scripts\python.exe manage.py migrate`
- `venv\Scripts\python.exe -m pytest nstv/tests -q`

## Plex Sync Components
- `nstv/plexController/add_shows_to_nstv.py`
- `nstv/plexController/add_episodes_to_show.py`
- `nstv/plexController/add_movies_to_nstv.py`
- `nstv/plexController/plexDance.py`

## Plex Sync Expectations
- Read Plex config from environment variables.
- Avoid connecting to Plex at module import time.
- Keep functions testable via dependency injection (optional `plex` argument).
- Handle missing optional data from Plex (genres/directors/posters).

## Environment Variables
- `DJANGO_DB_PASSWORD`
- `PLEX_EMAIL`
- `PLEX_API_KEY`
- `PLEX_SERVER`
- `TVDB_API_KEY`
- `NZBGEEK_USERNAME`
- `NZBGEEK_PASSWORD`
- `NZBGET_NZB_DIR`
- `NZBGET_COMPLETE_DIR`
- `PLEX_TV_SHOW_DIR`
- `PLEX_MOVIES_DIR`
- `SHOW_FOLDER_PATH`
- `TEMP_FOLDER_PATH`

## Download & File Management

### Post-Download Automation (NEW)
**Status**: ⚠️ NZBGet integration currently disabled - use manual processing  
**Documentation**: See `docs/POST_DOWNLOAD_AUTOMATION.md`

Automated processing moves completed downloads to Plex and syncs the database.

**Manual Processing Command**:
```bash
.venv\Scripts\python.exe manage.py process_downloads
```

**Options**:
- `--dry-run` - Preview what would be processed
- `--media-type=tv|movies|all` - Process specific media type
- `--no-sync` - Move files without database sync
- `--verbose` - Detailed output

**Safety Features**:
- Plex connectivity check before processing
- Files remain in download directory if Plex offline
- Cross-drive file movement (C: to Y:) with progress tracking
- Source files removed only after successful copy

**Known Issues**:
- NZBGet post-processing script disabled due to Python path resolution issue
- See `docs/BUGS.md` for current workarounds

**Related Files**:
- `nstv/management/commands/process_downloads.py` - Core logic
- `scripts/nzbget_postprocess.py` - NZBGet integration (disabled)
- `docs/POST_DOWNLOAD_AUTOMATION.md` - Full documentation
- `docs/NZBGET_SETUP.md` - Setup guide (when automation fixed)

### Background Threading
All long-running operations run in background threads to prevent blocking the UI:
- **Downloads**: `download_episode()`, `download_movie()` - Start NZB downloads
- **File moves**: `move_downloaded_tv_show_files_to_plex()`, `move_downloaded_movie_files_to_plex()`

Pattern:
```python
def view_function(request):
    # Start operation in background thread
    thread = threading.Thread(
        target=operation_function,
        args=(arg1, request),
        daemon=True
    )
    thread.start()
    messages.info(request, "Operation started. Check console for progress.")
    return redirect(request.META.get('HTTP_REFERER'))
```

### Download Flow
1. User clicks download button
2. NZBGeek login and search
3. Download NZB file to ~/Downloads
4. Move NZB to NZBGet watch directory
5. Monitor NZBGet history for completion status
6. Django messages provide user feedback

### File Movement Flow
1. User clicks "Move to Plex" button
2. Validate source (NZBGET_COMPLETE_DIR) and destination exist
3. Move files with detailed error handling
4. For TV shows: Automatically sync episodes with Plex after move
5. Return status via Django messages (success/warning/error)

### Quality Filtering
- Movie downloads: No quality filter by default (search all qualities)
- TV downloads: HD filtering with fallback if no HD results found
- Anime shows: Filter out English-only audio tracks

## Django Management Commands

### process_downloads (NEW)
Automatically process completed downloads from NZBGet directory.

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
