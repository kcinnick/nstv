# Automation Scripts

This directory contains scripts for automating post-download processing.

## Scripts Overview

### 1. `run_download_processor.bat`
**Purpose**: Windows batch file for manual or scheduled execution  
**Use case**: Simple Windows Task Scheduler integration  
**How to use**:
```
# Manual execution
run_download_processor.bat

# Or double-click the file in Explorer
```

### 2. `run_download_processor.ps1`
**Purpose**: PowerShell script with logging and advanced features  
**Use case**: Production Task Scheduler setup with logging  
**Features**:
- Logs to `logs/download_processor_YYYY-MM.log`
- Environment validation
- Better error handling
- Execution time tracking

**How to use**:
```powershell
# Manual execution
.\run_download_processor.ps1

# Task Scheduler setup
# Program: powershell.exe
# Arguments: -ExecutionPolicy Bypass -File "C:\Users\Nick\nstv\scripts\run_download_processor.ps1"
```

### 3. `nzbget_postprocess.py`
**Purpose**: NZBGet post-processing script  
**Use case**: Automatic triggering when NZBGet completes downloads  
**Installation**:
1. Copy to NZBGet's scripts directory
2. Configure in NZBGet Settings > Extension Scripts
3. Set `NSTV_PROJECT_PATH` parameter

## Which Script Should I Use?

**For automatic processing when downloads finish**:
→ Use `nzbget_postprocess.py` (best option)

**For scheduled periodic processing**:
→ Use `run_download_processor.ps1` (recommended) or `.bat` (simpler)

**For manual testing**:
→ Use `.bat` file (easiest) or run Django command directly

## Configuration Required

All scripts require these environment variables:
- `NZBGET_COMPLETE_DIR` - Where NZBGet puts completed downloads
- `PLEX_TV_SHOW_DIR` - Target directory for TV shows
- `PLEX_MOVIES_DIR` - Target directory for movies

## See Also

- [AUTOMATION.md](../docs/AUTOMATION.md) - Full setup guide
- Django management command: `python manage.py process_downloads --help`
