# Plex Rebuild Runbook

## Goal
Rebuild `Show`, `Episode`, and `Movie` data from Plex after data loss.

## Pre-checks
- PostgreSQL is running.
- Migrations are applied.
- `.env` contains valid Plex credentials.

## Rebuild Steps
1. Sync shows:
   - `venv\Scripts\python.exe nstv\plexController\add_shows_to_nstv.py`
2. Sync episodes:
   - `venv\Scripts\python.exe nstv\plexController\add_episodes_to_show.py`
3. Sync movies:
   - `venv\Scripts\python.exe nstv\plexController\add_movies_to_nstv.py`

## Optional Plex Dance
Use only when Plex library refresh requires file move-out/move-back behavior:
- `venv\Scripts\python.exe nstv\plexController\plexDance.py`

## Validation
- `venv\Scripts\python.exe manage.py check`
- Open app home page and verify shows/movies render.
- Spot-check records in Django admin.
