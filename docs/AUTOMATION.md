# Automated Post-Download Processing

This feature automatically moves completed downloads from NZBGet to your Plex media directories and syncs your Django database.

## Overview

**Before**: Manual process requiring you to click a button in the web UI after each download

**After**: Fully automated - downloads are automatically processed and added to Plex

## Components

1. **Django Management Command** (`process_downloads`) - Core processing logic
2. **NZBGet Post-Processing Script** - Triggers processing when NZBGet completes a download
3. **Windows Task Scheduler Scripts** - Periodic processing for backup automation

## Quick Start

### Option 1: NZBGet Integration (Recommended)

This triggers processing immediately when downloads complete.

1. **Copy the NZBGet script**:
   ```powershell
   # The script is already in: C:\Users\Nick\nstv\scripts\nzbget_postprocess.py
   # Copy it to your NZBGet scripts directory (e.g., C:\ProgramData\NZBGet\scripts)
   ```

2. **Configure NZBGet**:
   - Open NZBGet web interface
   - Go to Settings > Extension Scripts
   - Find "Auto-process downloads to Plex"
   - Set `NSTV_PROJECT_PATH` to: `C:\Users\Nick\nstv`
   - Set `PYTHON_PATH` to your Python executable (e.g., `C:\Users\Nick\nstv\.venv\Scripts\python.exe`)
   - Save and reload NZBGet

3. **Test it**:
   ```bash
   # Download something via your web UI
   # Watch NZBGet logs - you should see the script run after completion
   ```

### Option 2: Windows Task Scheduler

This runs processing every 15-30 minutes as a backup.

1. **Open Task Scheduler** (Windows Key + R, type `taskschd.msc`)

2. **Create Basic Task**:
   - Name: `NSTV Download Processor`
   - Description: `Automatically process completed downloads`
   - Trigger: Daily at midnight
   - Repeat: Every 15 minutes, for 1 day
   - Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\Users\Nick\nstv\scripts\run_download_processor.ps1"`
   - Start in: `C:\Users\Nick\nstv`

3. **Additional Settings**:
   - Run whether user is logged on or not
   - Run with highest privileges
   - Stop task if runs longer than 30 minutes

### Option 3: Manual Execution

Run whenever you want to process downloads:

```bash
# From project directory
cd C:\Users\Nick\nstv

# Activate virtual environment
.\.venv\Scripts\activate

# Process all downloads
python manage.py process_downloads

# Or use the batch file
.\scripts\run_download_processor.bat

# Or PowerShell
.\scripts\run_download_processor.ps1
```

## Management Command Options

### Basic Usage

```bash
python manage.py process_downloads
```

### Advanced Options

```bash
# Process only TV shows
python manage.py process_downloads --media-type=tv

# Process only movies
python manage.py process_downloads --media-type=movies

# Dry run - see what would happen without moving files
python manage.py process_downloads --dry-run

# Skip Plex database sync (just move files)
python manage.py process_downloads --no-sync

# Verbose output
python manage.py process_downloads --verbose

# Combine options
python manage.py process_downloads --media-type=tv --verbose --dry-run
```

## How It Works

### Workflow

1. **Detection**: Script checks `NZBGET_COMPLETE_DIR` for downloaded files
2. **Classification**: Determines if files are TV shows or movies (based on category or path)
3. **Movement**: Moves files to appropriate Plex directory:
   - TV Shows → `PLEX_TV_SHOW_DIR`
   - Movies → `PLEX_MOVIES_DIR`
4. **Sync**: Updates Django database with new episodes/movies from Plex
5. **Logging**: Reports success/failure for each file

### File Handling

- **Existing files**: Skipped (not overwritten)
- **Permissions**: Errors logged but don't stop processing
- **Atomic**: Each file moved independently (one failure doesn't stop others)
- **Safe**: Original files only removed after successful move

## Environment Variables

Required variables (should already be set):

```powershell
NZBGET_COMPLETE_DIR=<path to NZBGet completed downloads>
PLEX_TV_SHOW_DIR=<path to Plex TV Shows directory>
PLEX_MOVIES_DIR=<path to Plex Movies directory>
PLEX_EMAIL=<your Plex account email>
PLEX_API_KEY=<your Plex API token>
PLEX_SERVER=<your Plex server name>
```

## Troubleshooting

### Check environment variables

```powershell
# In PowerShell
$env:NZBGET_COMPLETE_DIR
$env:PLEX_TV_SHOW_DIR
$env:PLEX_MOVIES_DIR
```

### Test the command

```bash
# Dry run to see what would happen
python manage.py process_downloads --dry-run --verbose
```

### View logs

**PowerShell script logs**:
```
C:\Users\Nick\nstv\logs\download_processor_YYYY-MM.log
```

**NZBGet logs**:
- Open NZBGet web interface
- Go to Messages
- Look for post-processing script output

### Common Issues

**"No files to process"**
- Check that downloads are completing to `NZBGET_COMPLETE_DIR`
- Verify the directory path is correct

**"Permission denied"**
- Run with administrator privileges
- Check file/directory permissions on Plex directories

**"Plex directory not found"**
- Verify external drives are mounted
- Check environment variable paths

**"Plex sync failed"**
- Verify Plex server is running
- Check Plex credentials in environment variables

## Integration with Existing Web UI

The existing web UI buttons still work! They call the same underlying logic. Now you have choices:

- **Automatic**: NZBGet triggers processing immediately
- **Scheduled**: Task Scheduler runs every 15 minutes
- **Manual**: Use web UI buttons when you want manual control

## Next Steps

1. Test with a small download first
2. Monitor logs to ensure it's working
3. Adjust Task Scheduler frequency if needed
4. Consider adding email notifications (see PowerShell script)

## Uninstall/Disable

**Disable NZBGet integration**:
- In NZBGet Settings > Extension Scripts, uncheck the script

**Disable Task Scheduler**:
- Open Task Scheduler
- Right-click "NSTV Download Processor"
- Disable or Delete

**The manual web UI buttons always remain available.**
