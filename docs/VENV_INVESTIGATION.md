# Virtual Environment Investigation
**Date**: March 10, 2026  
**Status**: Investigation Complete

## Findings

Found **THREE** virtual environments in the project root:

### 1. `.venv/` (ACTIVE - KEEP)
- **Status**: ✅ Active, referenced in scripts
- **Python**: 3.11+ (based on package compatibility)
- **Django Version**: 6.0.2 (newest)
- **Packages**: All required packages installed (Django, PlexAPI, django-tables2, pytest-django)
- **Referenced in**: `scripts/nzbget_postprocess.py` line 60
- **Last Updated**: February 28, 2026
- **Size**: ~68 MB

### 2. `venv/` (OLD - REMOVE)
- **Status**: ⚠️ Unused, older Django version
- **Python**: 3.11+
- **Django Version**: 5.2.11 (older than .venv)
- **Packages**: Similar to .venv but outdated
- **Referenced in**: Nothing
- **Last Updated**: February 22, 2026
- **Size**: Unknown (not measured)

### 3. `activate/` (BROKEN - REMOVE)
- **Status**: ❌ Broken, pip list failed
- **Python**: Executable exists but packages may be corrupted
- **Django Version**: N/A (pip list failed with exit code 1)
- **Packages**: Failed to list
- **Referenced in**: Nothing (only in .gitignore)
- **Last Updated**: February 22, 2026
- **Size**: Unknown

## Recommendations

### Keep
- ✅ **`.venv/`** - This is the active virtual environment with current packages

### Remove
- ❌ **`venv/`** - Outdated Django version (5.2.11 vs 6.0.2), not referenced anywhere
- ❌ **`activate/`** - Broken pip, not referenced, likely from failed setup

## Action Plan

1. **Verify .venv is working**:
   ```bash
   .\.venv\Scripts\python.exe manage.py --version
   ```

2. **Remove old virtual environments**:
   ```bash
   Remove-Item -Recurse -Force venv/
   Remove-Item -Recurse -Force activate/
   ```

3. **Update .gitignore** (already done):
   - `.venv/` is ignored
   - `venv/` is ignored  
   - `activate/` is ignored

4. **Document in README**:
   Add note that `.venv` is the only virtual environment and how to set it up

## Verification

Before removal, confirmed:
- [x] `.venv` has Django 6.0.2 (newest version)
- [x] `.venv` has all required packages (PlexAPI, django-tables2, pytest)
- [x] Scripts reference `.venv` specifically
- [x] `venv/` has older Django (5.2.11)
- [x] `venv/` not referenced anywhere
- [x] `activate/` is broken (pip failed)
- [x] `activate/` not referenced anywhere (except .gitignore)

## Disk Space Savings

Estimated savings from removing venv/ and activate/:
- Each venv is ~60-100 MB
- Total savings: ~120-200 MB

## Safety

All three are already gitignored, so removing them:
- ✅ Won't affect git history
- ✅ Won't affect repository
- ✅ Won't affect deployments (venvs are always recreated)
- ✅ Can be recreated from requirements.txt if needed

## Conclusion

**Safe to remove**: `venv/` and `activate/`  
**Keep**: `.venv/` (active, referenced, up-to-date)
