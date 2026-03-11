# Post-Download Automation System

## Quick Start

**Status**: ⚠️ NZBGet integration currently disabled (see [BUGS.md](BUGS.md))  
**Current Method**: Manual processing via command line

### Process Downloads Now
```powershell
cd C:\Users\Nick\nstv
.\.venv\Scripts\python.exe manage.py process_downloads
```

## What This Does

1. ✅ Checks Plex server is online
2. ✅ Finds completed downloads in NZBGet directory
3. ✅ Moves files to appropriate Plex directory (TV Shows or Movies)
4. ✅ Syncs Django database with new media
5. ✅ Removes files from download directory after successful move

## Command Options

```powershell
# Dry run - see what would happen without moving files
python manage.py process_downloads --dry-run

# Process only TV shows
python manage.py process_downloads --media-type=tv

# Process only movies
python manage.py process_downloads --media-type=movies

# Move files but skip database sync
python manage.py process_downloads --no-sync

# Verbose output
python manage.py process_downloads --verbose
```

## Files & Components

```
nstv/
├── management/
│   └── commands/
│       └── process_downloads.py    # Django management command
├── scripts/
│   ├── nzbget_postprocess.py       # NZBGet integration (disabled)
│   ├── run_download_processor.bat  # Windows batch script
│   └── run_download_processor.ps1  # PowerShell script with logging
└── docs/
    ├── AUTOMATION.md               # Full automation guide
    ├── NZBGET_SETUP.md            # NZBGet integration setup
    ├── BUGS.md                     # Known issues
    └── MANUAL_TASKS.md            # Task reminders
```

## How It Works

### File Movement
- **Source**: `%NZBGET_COMPLETE_DIR%` (e.g., `C:\ProgramData\NZBGet\complete`)
- **Destination**: `%PLEX_TV_SHOW_DIR%` or `%PLEX_MOVIES_DIR%` (e.g., `Y:\Library\TV Shows`)
- **Method**: `shutil.move()` - copies across drives then removes source

### Cross-Drive Copying
Large files (2+ GB) take time to copy from C: to network drive Y:
- Progress shown per file
- File size displayed before moving
- Source removed only after successful copy

### Plex Safety Check
Before any processing, script verifies:
- Plex server credentials configured
- Plex server is accessible
- Library sections exist

If Plex is offline: **Aborts gracefully, files remain for next run**

## Environment Variables Required

```powershell
NZBGET_COMPLETE_DIR=C:\ProgramData\NZBGet\complete
PLEX_TV_SHOW_DIR=Y:\Library\TV Shows
PLEX_MOVIES_DIR=Y:\Library\Movies
PLEX_EMAIL=your@email.com
PLEX_API_KEY=your-plex-token
PLEX_SERVER=your-server-name
```

## Automation Options (Future)

### Option A: NZBGet Post-Processing
**Status**: 🔴 Currently Disabled  
**When Fixed**: Processes immediately when downloads complete  
**Setup**: See [NZBGET_SETUP.md](NZBGET_SETUP.md)

### Option B: Windows Task Scheduler
**Status**: 🟡 Available but not configured  
**Frequency**: Every 15-30 minutes  
**Script**: `scripts\run_download_processor.ps1`

### Option C: Manual Execution
**Status**: 🟢 Working  
**When**: Run whenever you want to process downloads  
**Method**: Command line or batch file

## Troubleshooting

### "Plex server is not accessible"
- Verify Plex is running on your NAS
- Check network connectivity
- Files remain in download directory - safe to retry

### "Permission denied"
- Run PowerShell as Administrator
- Check write permissions on Plex directories

### "Already exists at destination"
- File skipped (not an error)
- Remove from download directory manually if needed

### Processing seems hung
- Large files take time to copy over network
- Check network drive access
- Monitor PowerShell output for progress

## Testing

### Dry Run Test
```powershell
python manage.py process_downloads --dry-run --verbose
```

Expected output:
```
Checking Plex server connection...
✓ Plex server "AS6602T-8263" is accessible
Found 3 items to process
[1/3] Processing: Show.Name.mkv
  Size: 2.20 GB
  WOULD MOVE
```

### Actual Processing Test
```powershell
python manage.py process_downloads --no-sync --verbose
```

Monitor output for:
- ✓ Moved successfully
- Files removed from download directory

## Related Documentation

- **[AUTOMATION.md](AUTOMATION.md)** - Full automation guide with all options
- **[NZBGET_SETUP.md](NZBGET_SETUP.md)** - NZBGet integration (when fixed)
- **[BUGS.md](BUGS.md)** - Known issues and workarounds
- **[MANUAL_TASKS.md](MANUAL_TASKS.md)** - Regular maintenance tasks

## Next Steps

1. ✅ Manual processing works - use when needed
2. ⏳ Fix NZBGet Python path configuration
3. ⏳ Set up Task Scheduler as backup automation
4. ⏳ Test and monitor for stability
