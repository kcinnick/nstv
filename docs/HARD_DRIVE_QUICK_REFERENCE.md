# Hard Drive Organization - Quick Reference

## Your Setup

- **NAS:** Two volumes (Plex and Plex2) with Movies and TV Shows folders each
- **Network Drive:** Y:\ maps to one NAS volume
- **Downloads:** C:\ProgramData\NZBGet\complete\
- **Auto-Organization:** ✅ ENABLED

---

## How It Works Now

### TV Shows
```
NZBGet Download (e.g., "Feud.S02E01.1080p.mkv")
           ↓
Auto-detect: S##E## pattern
           ↓
Move to: Y:\Library\TV Shows\Feud\
           ↓
Plex reads and displays
```

### Movies
```
NZBGet Download (e.g., "Inception (2010) 1080p.mkv")
           ↓
Auto-detect: (YYYY) pattern
           ↓
Move to: Y:\Library\Movies\Inception (2010)\
           ↓
Plex reads and displays
```

---

## Manual Processing

If you need to manually process downloads:

```powershell
# Process everything
python manage.py process_downloads

# Only TV shows
python manage.py process_downloads --media-type=tv

# Only movies
python manage.py process_downloads --media-type=movies

# Test without moving
python manage.py process_downloads --dry-run

# Verbose output
python manage.py process_downloads --verbose
```

---

## File Organization

### TV Shows
```
Y:\Library\TV Shows\
├─ Feud\
│  ├─ S01E01.mkv
│  ├─ S01E02.mkv
│  └─ S02E01.mkv
├─ Breaking Bad\
│  ├─ S01E01.mkv
│  └─ S05E16.mkv
```

### Movies
```
Y:\Library\Movies\
├─ Inception (2010)\
│  └─ Inception.2010.1080p.mkv
├─ Avatar (2009)\
│  └─ Avatar.2009.1080p.mkv
```

---

## Filename Requirements

### For TV to Be Recognized
Must contain: `S##E##` (e.g., S01E01, S02E03, S2023E15)

✅ Examples:
- `Feud.S02E01.1080p.WEBDL.mkv`
- `breaking.bad.s05e16.mkv`
- `The.Office.S09E23.webrip.mkv`

### For Movies to Be Recognized
Must contain: `(YYYY)` or `[YYYY]` or `YYYY` with quality

✅ Examples:
- `Inception (2010) 1080p.mkv`
- `Avatar [2009] 1080p.mkv`
- `The.Shawshank.Redemption.1994.1080p.mkv`

---

## Both NAS Volumes Can Be Used

Ask your Plex admin to configure multiple library locations:

**Plex TV Shows Library:**
- `/volume1/Plex/Library/TV Shows/`
- `/volume2/Plex2/Library/TV Shows/`

**Plex Movies Library:**
- `/volume1/Plex/Library/Movies/`
- `/volume2/Plex2/Library/Movies/`

This spreads your content across both drives!

---

## Status: ✅ READY

Downloads are now automatically organized into:
- TV Show folders (by show name)
- Movie folders (by movie name)

Both NAS volumes can be utilized!

