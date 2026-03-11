# Known Issues and Bugs

## Active Issues

### NZBGet Post-Processing Automation - Python Path Resolution Issue
**Status**: Open  
**Priority**: Medium  
**Date Reported**: 2026-03-10  

**Problem**:
NZBGet post-processing script triggers PyCharm/IntelliJ instead of Python, causing Java errors and hung processing.

**Symptoms**:
- NZBGet Messages tab shows Java/PyCharm errors instead of Python output
- Processing hangs indefinitely
- Errors like: `Cannot invoke "java.lang.Long.longValue()" because the return value of "java.lang.Long.getLong(String)" is null`

**Root Cause**:
Windows resolving `python` command to PyCharm launcher instead of actual Python interpreter.

**Current Workaround**:
Script disabled (renamed to `nzbget_postprocess.py.disabled`). Use manual processing:
```powershell
cd C:\Users\Nick\nstv
.\.venv\Scripts\python.exe manage.py process_downloads
```

**Attempted Fixes**:
1. ✅ Updated script to default to venv Python if PYTHON_PATH not set
2. ✅ Added validation of Python executable path
3. ❌ Still needs testing with correct NZBGet configuration

**Next Steps**:
1. In NZBGet Settings → Extension Scripts → nzbget_postprocess
2. Set PYTHON_PATH explicitly to: `C:\Users\Nick\nstv\.venv\Scripts\python.exe`
3. Re-enable script (remove `.disabled` extension)
4. Test with small download
5. Monitor NZBGet Messages tab for clean output

**Files Affected**:
- `scripts/nzbget_postprocess.py`
- `C:\ProgramData\NZBGet\scripts\nzbget_postprocess.py.disabled`

---

## Resolved Issues

### Duplicate Detection - Different Shows with Same Title
**Status**: Fixed  
**Priority**: High  
**Date Resolved**: 2026-03-07  

**Problem**:
Duplicate detection grouped different shows like "The Twilight Zone (1959)" and "The Twilight Zone (2019)" as duplicates.

**Fix**:
Changed grouping key from `show.title` to `show.ratingKey` to ensure unique identification.

**Commit**: `33f132b`

---

### Plex API Deletion - Wrong Method Used
**Status**: Fixed  
**Priority**: High  
**Date Resolved**: 2026-03-07  

**Problem**:
Deletion attempts used non-existent `removeMedia()` method, causing failures.

**Fix**:
Changed to correct Plex API method: `media.delete()`

**Commit**: `e7defdc`

---

### Cross-Platform File Deletion
**Status**: Fixed  
**Priority**: High  
**Date Resolved**: 2026-03-07  

**Problem**:
Windows Django app couldn't use `os.remove()` on NAS file paths that don't exist locally.

**Fix**:
Use Plex API for deletion instead of filesystem operations.

**Commit**: `2071989`
