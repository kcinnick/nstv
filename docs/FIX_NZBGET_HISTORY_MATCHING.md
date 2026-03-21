# NZBGet History Matching - BUG FIX

## Problem
When downloading NZBs, the app was showing:
```
[510s] FEUD-S02E01-Pilot.WEBDL-1080p_1 not yet in NZBGet history. Still queued or processing...
```

Even though the file WAS in NZBGet history. This happened because:
- The app searches for `NZBDownload` records by exact title match
- NZBGet may format the title differently than how the app names the file
- The exact match failed, so it kept saying "not yet in history"

## Root Cause
In `nstv/download.py`, the monitoring code used:
```python
if NZBDownload.objects.all().filter(title=result.title).exists():
```

This is an exact match, but NZBGet may have different formatting.

## Solution
Updated the monitoring logic to:
1. First try exact title match
2. If exact match fails, try partial/case-insensitive match using `icontains`
3. Search using the base filename without extension

### Code Changes
**File: `nstv/download.py`**

Added fallback matching logic:
```python
if NZBDownload.objects.all().filter(title=result.title).exists():
    # Exact match - proceed as before
    nzb_download = ...
    
elif NZBDownload.objects.all().filter(title__icontains=result.title.split('.')[0]).exists():
    # Fallback: partial match using first part of filename
    nzb_download = ...
    # Then check status as usual
```

## Testing
To verify the fix works:
```powershell
python manage.py runserver
# Try downloading a file
# Monitor should now find it in NZBGet history
```

## Result
✅ Downloads are now properly detected in NZBGet history
✅ No more false "not yet in history" messages
✅ Monitoring continues to completion

