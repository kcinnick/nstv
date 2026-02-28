# Claude Sonnet 4.5 Instructions

## Purpose
This repository is a Django app (`nstv`) used to track TV shows, episodes, and movies and sync that data from a local Plex server.

## Core Rules
- Keep changes minimal and scoped to the user request.
- Prefer updating existing files over adding new abstractions.
- Do not hardcode secrets, credentials, or local machine paths.
- Use environment variables for runtime configuration.
- Add/adjust tests for behavior changes.

## Local Setup
1. Activate virtual environment.
2. Ensure `.env` has required keys (see `.env.example`).
3. Run migrations before starting server.

## Verification Commands
- `venv\Scripts\python.exe manage.py check`
- `venv\Scripts\python.exe manage.py migrate`
- `venv\Scripts\python.exe -m pytest nstv/tests -q`

## Plex Sync Components
- `nstv/plexController/add_shows_to_nstv.py`
- `nstv/plexController/add_episodes_to_show.py`
- `nstv/plexController/add_movies_to_nstv.py`
- `nstv/plexController/plexDance.py`

## Plex Sync Expectations
- Read Plex config from environment variables.
- Avoid connecting to Plex at module import time.
- Keep functions testable via dependency injection (optional `plex` argument).
- Handle missing optional data from Plex (genres/directors/posters).

## Environment Variables
- `DJANGO_DB_PASSWORD`
- `PLEX_EMAIL`
- `PLEX_API_KEY`
- `PLEX_SERVER`
- `SHOW_FOLDER_PATH`
- `TEMP_FOLDER_PATH`

## Common Workflow
1. Implement smallest functional change.
2. Run targeted tests.
3. Run Django checks.
4. Summarize what changed and any follow-up steps.
