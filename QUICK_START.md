# Quick Start

## Setup
1. Activate venv
2. Run: `python manage.py check`
3. Run: `python manage.py migrate`
4. Run: `python manage.py runserver`
5. Visit: http://127.0.0.1:8000

## Common Commands
```powershell
python manage.py runserver              # Dev server
python manage.py migrate                # Database
python manage.py process_downloads      # Process downloads
python manage.py shell                  # Django shell
python -m pytest nstv/tests -q          # Tests
```

## Documentation
- **Setup/Deploy**: `docs/DEPLOYMENT.md`
- **Development**: `instructions.md`
- **Maintenance**: `docs/MANUAL_TASKS.md`
- **PowerShell**: `docs/POWERSHELL_COMMAND_REFERENCE.md`
- **All Docs**: `docs/INDEX.md`

## Features
- Browse/search shows, episodes, movies
- Sync with Plex server
- TVDB metadata integration
- Duplicate media detection
- Download automation (manual mode)

## PostgreSQL Upgrade (if needed)
- Current: PostgreSQL 16.13 ✅
- Django requires: PostgreSQL 14+
- See: `docs/archive/postgresql-upgrade/` for reference
