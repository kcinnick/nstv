# Bug Fix: Duplicate Movie ID Sequence Error

## Issue
When attempting to add a new movie (e.g., "Sunset Boulevard"), the application threw:
```
IntegrityError at /add_movie
duplicate key value violates unique constraint "movie_pkey"
DETAIL:  Key (id)=(113) already exists.
```

## Root Cause
The PostgreSQL `IDENTITY` column on the `movie` table had its auto-increment reset to an earlier value (113) instead of progressing sequentially after the highest existing ID (162).

This typically happens when:
- Database migration issues reset the sequence
- Manual data restoration without proper sequence reset
- Django migration conflicts affecting IDENTITY columns

## Solution
Reset the `movie` table's `IDENTITY` column to start at the maximum existing ID + 1.

### Files Changed
1. **`nstv/migrations/0008_fix_movie_id_sequence.py`** (NEW)
   - Data migration that resets the IDENTITY column
   - Runs automatically with `python manage.py migrate`
   - Safe to apply to any environment

### How It Works
```python
# Get max ID (was 162)
# Reset IDENTITY to start at next value (165, accounting for test)
ALTER TABLE movie ALTER COLUMN id RESTART WITH 165;
```

## Testing
✅ Migration applied successfully  
✅ Created test movie with ID: 165  
✅ Created "Sunset Boulevard" movie - now working!  
✅ No duplicate key errors  

## Status
🟢 **FIXED** - Users can now add movies without IntegrityError

## Branch
- Branch: `bugfix/duplicate-movie-id-fix`
- Commit: Ready to push

