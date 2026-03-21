# Hard Drive Organization - Implementation Complete

## What Was Done

### Enhanced `process_downloads.py` Management Command

The command now intelligently separates movies and TV shows based on filename patterns:

#### 1. Media Type Detection
```python
# TV Show Pattern: S##E## (e.g., S01E01, S02E03)
TV_SHOW_PATTERN = re.compile(r'[Ss]\d{1,2}[Ee]\d{1,2}')

# Movie Pattern: (YYYY) or [YYYY] (e.g., (2010), [2024])
MOVIE_PATTERN = re.compile(r'(\([\d]{4}\))|(\[[\d]{4}\])|(\d{4}\s*(?:1080p|720p|2160p|...))')
```

#### 2. Automatic Organization
```
Downloads from NZBGet:
    ↓
Detect Type (TV or Movie)
    ↓
Extract Name (Remove quality indicators)
    ↓
Create Organization Folder
    ↓
Move to Plex Directory
```

#### 3. Directory Structure Created

**TV Shows:**
```
Y:\Library\TV Shows\
├─ Feud\
│  ├─ Feud.S01E01.1080p.mkv
│  └─ Feud.S02E01.1080p.mkv
├─ Breaking Bad\
│  ├─ Breaking.Bad.S01E01.mkv
│  └─ Breaking.Bad.S05E16.mkv
└─ [Other Shows]\
```

**Movies:**
```
Y:\Library\Movies\
├─ Inception (2010)\
│  └─ Inception.2010.1080p.mkv
├─ The Shawshank Redemption (1994)\
│  └─ The.Shawshank.Redemption.1994.1080p.mkv
└─ [Other Movies]\
```

### Key Features

✅ **Automatic Classification** - Detects TV vs Movie by filename pattern
✅ **Smart Organization** - Creates show/movie folders automatically
✅ **Error Handling** - Skips unknown formats (safe mode)
✅ **Dry-Run Mode** - Test with `--dry-run` flag
✅ **Verbose Output** - See exactly what's happening
✅ **Duplicate Prevention** - Won't overwrite existing files
✅ **Plex Integration** - Auto-syncs database after move

---

## How to Use

### Process All Downloads
```powershell
python manage.py process_downloads
```

### Process TV Shows Only
```powershell
python manage.py process_downloads --media-type=tv
```

### Process Movies Only
```powershell
python manage.py process_downloads --media-type=movies
```

### Test Run (No Files Moved)
```powershell
python manage.py process_downloads --dry-run
```

### Verbose Output
```powershell
python manage.py process_downloads --verbose
```

### Combine Options
```powershell
python manage.py process_downloads --media-type=tv --dry-run --verbose
```

---

## NZBGet Integration

The post-processing script (`scripts/nzbget_postprocess.py`) automatically calls this command after downloads complete:

1. NZBGet downloads file to `C:\ProgramData\NZBGet\complete\`
2. Download completes with SUCCESS status
3. Post-processing script triggers
4. `process_downloads` management command runs
5. File is classified and moved to Plex directory
6. Plex library refreshes automatically
7. Django database syncs

---

## Naming Convention Expected

### TV Shows Must Have S##E## Format
✅ Good: `Breaking.Bad.S05E16.1080p.mkv`
✅ Good: `feud.s02e01.webrip.mkv`
❌ Bad: `Breaking Bad Episode 16.mkv`

### Movies Must Have Year
✅ Good: `Inception (2010) 1080p.mkv`
✅ Good: `The Shawshank Redemption [1994].mkv`
✅ Good: `Avatar 2009 1080p.mkv`
❌ Bad: `Avatar.mkv` (no year)

---

## Storage Layout

### Current NAS Configuration

**Plex Volume 1:**
- `/volume1/Plex/Library/TV Shows/`
- `/volume1/Plex/Library/Movies/`

**Plex Volume 2:**
- `/volume2/Plex2/Library/TV Shows/`
- `/volume2/Plex2/Library/Movies/`

**Network Mapping:**
- `Y:\Library\TV Shows\` → One of the above
- `Y:\Library\Movies\` → One of the above

### Both Volumes Can Be Used
Configure Plex to scan multiple library locations:
- TV Shows: `/volume1/Plex/Library/TV Shows` + `/volume2/Plex2/Library/TV Shows`
- Movies: `/volume1/Plex/Library/Movies` + `/volume2/Plex2/Library/Movies`

This distributes load across both hard drives!

---

## Error Handling

| Scenario | Action |
|----------|--------|
| File already exists | Skips, logs warning |
| Permission denied | Logs error, continues |
| Unknown format | Skips, logs if verbose |
| Plex unreachable | Skips sync, files still moved |
| Directory doesn't exist | Creates it automatically |

---

## Example Workflow

```
1. Download "Feud.S02E01.Pilot.1080p.WEBDL.mkv" via NZBGet
   ↓
2. File lands in C:\ProgramData\NZBGet\complete\
   ↓
3. Post-processor triggers and runs: python manage.py process_downloads
   ↓
4. Command detects: "S02E01" → TV Show
   ↓
5. Extracts name: "Feud"
   ↓
6. Creates folder: Y:\Library\TV Shows\Feud\
   ↓
7. Moves file: Y:\Library\TV Shows\Feud\Feud.S02E01.Pilot.1080p.WEBDL.mkv
   ↓
8. Plex library updates
   ↓
9. Django database syncs
   ↓
✅ Done! File available in Plex
```

---

## Testing

To test the organization logic without moving files:

```powershell
# Test with dry-run and verbose
python manage.py process_downloads --dry-run --verbose

# Should output something like:
# [1/2] Processing: Feud.S02E01.1080p.mkv
#   Organization: Feud/
#   Type: tv
#   WOULD MOVE
# [2/2] Processing: Inception.2010.1080p.mkv
#   Organization: Inception (2010)/
#   Type: movie
#   WOULD MOVE
```

---

## Changes Made

**File:** `nstv/management/commands/process_downloads.py`

- ✅ Added `TV_SHOW_PATTERN` and `MOVIE_PATTERN` regex
- ✅ Updated Plex auth to use `PlexServer` (not `MyPlexAccount`)
- ✅ Added `_detect_media_type()` method
- ✅ Added `_extract_show_name()` method  
- ✅ Added `_extract_movie_name()` method
- ✅ Enhanced `_get_items_to_process()` to filter by media type
- ✅ Enhanced `_move_items()` to create organization folders
- ✅ Updated error handling for robustness

---

## Status

✅ **COMPLETE** - Hard drives properly organized!

Both NAS volumes can now be used for movies and TV shows, with intelligent automatic organization based on file patterns.

