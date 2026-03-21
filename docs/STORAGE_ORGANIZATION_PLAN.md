# Storage Organization Plan

## Current Setup

### NAS Configuration
- **Volume 1 (Plex):** `/volume1/Plex/Library/`
  - TV Shows: `/volume1/Plex/Library/TV Shows`
  - Movies: `/volume1/Plex/Library/Movies`

- **Volume 2 (Plex2):** `/volume2/Plex2/Library/`
  - TV Shows: `/volume2/Plex2/Library/TV Shows`
  - Movies: `/volume2/Plex2/Library/Movies`

### Network Mapping
- **Y:\** → Maps to one of the NAS volumes (appears to be Plex2 based on .env)

### Local Download Directory
- **Downloads:** `C:\ProgramData\NZBGet\complete`

---

## Organization Strategy

### File Flow for Downloads

**TV Shows:**
```
NZBGet Download
    ↓
C:\ProgramData\NZBGet\complete\[Show Name].[SxxExxx].etc
    ↓
Auto-detect as TV show (by naming pattern: S##E##)
    ↓
Move to: Y:\Library\TV Shows\[Show Name]\
    ↓
Plex library auto-refresh
    ↓
Django database sync
```

**Movies:**
```
NZBGet Download
    ↓
C:\ProgramData\NZBGet\complete\[Movie Name].(2025).etc
    ↓
Auto-detect as Movie (by naming pattern: (YYYY) year)
    ↓
Move to: Y:\Library\Movies\[Movie Name] (Year)\
    ↓
Plex library auto-refresh
    ↓
Django database sync
```

---

## Detection Logic

### TV Show Patterns (Match ANY)
- `SxxEyy` - Standard season/episode notation
- `S01E01`, `S2023E15`, etc.

### Movie Patterns (Match ANY)
- `(YYYY)` - Year in parentheses
- `[YYYY]` - Year in brackets  
- `YYYY` followed by quality (1080p, 720p, etc.)

---

## Implementation

The `process_downloads.py` management command will:

1. **Scan** NZBGet complete directory
2. **Classify** each item as TV Show or Movie using filename patterns
3. **Move** to appropriate Plex directory (Y:\Library\TV Shows or Y:\Library\Movies)
4. **Organize** into show/movie folders
5. **Sync** Plex library
6. **Update** Django database

---

## Example Organization

### TV Shows
```
Y:\Library\TV Shows\
├─ Feud\
│  ├─ Season 1\
│  │  ├─ Feud.S01E01.mkv
│  │  ├─ Feud.S01E02.mkv
│  └─ Season 2\
│     ├─ Feud.S02E01.mkv
├─ Breaking Bad\
│  ├─ Season 1\
│  └─ Season 5\
└─ The Office\
```

### Movies
```
Y:\Library\Movies\
├─ The Shawshank Redemption (1994)\
│  └─ The Shawshank Redemption.1994.1080p.mkv
├─ Inception (2010)\
│  └─ Inception.2010.1080p.mkv
└─ Avatar (2009)\
   └─ Avatar.2009.2160p.mkv
```

---

## File Structure in Plex

Both volumes should mirror this structure:
- **Plex volume:** `/volume1/Plex/Library/TV Shows` & `/volume1/Plex/Library/Movies`
- **Plex2 volume:** `/volume2/Plex2/Library/TV Shows` & `/volume2/Plex2/Library/Movies`
- **Network path (Y:\):** Maps to one of above

Plex can be configured to scan multiple locations, so both volumes are utilized.

---

## Status

✅ Configuration identified
✅ File flow designed
✅ Detection patterns defined
⏳ Implementation needed: Enhance `process_downloads.py` with better classification

