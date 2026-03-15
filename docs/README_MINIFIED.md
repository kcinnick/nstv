# Documentation

## ⚠️ Windows/PowerShell Only
**Do NOT use Unix/Linux commands** - they won't work. See `POWERSHELL_COMMAND_REFERENCE.md` for equivalents.

**Quick Reference**: `grep` → `Select-String` | `ls -la` → `Get-ChildItem -Force` | `find .` → `Get-ChildItem -Recurse` | `test -f` → `Test-Path`

## Start Here
1. **New users**: `../QUICK_START.md`
2. **Setup/Deploy**: `DEPLOYMENT.md`
3. **Development**: `../instructions.md`
4. **Code style**: `FRONTEND_GUIDELINES.md`

## Documentation Map
| Document | Purpose |
|----------|---------|
| `DEPLOYMENT.md` | How to deploy/run |
| `MANUAL_TASKS.md` | Recurring maintenance |
| `NZBGET_SETUP.md` | NZBGet configuration |
| `POWERSHELL_COMMAND_REFERENCE.md` | Windows PowerShell commands |
| `FRONTEND_GUIDELINES.md` | HTML/CSS design system |

## Features
- Media Library: Browse/search shows, episodes, movies
- Plex Sync: Auto-sync from local Plex server
- TVDB Integration: Enrich metadata automatically
- Download Automation: NZBGeek → File movement → Plex sync (manual)
- Duplicate Detection: Find/delete duplicate media
- Background Processing: Long operations don't block UI

## Architecture
```
nstv/
├── models.py, views.py, forms.py         # Django
├── download.py                           # NZBGeek
├── plexController/                       # Plex, duplicates
├── get_info_from_tvdb/                   # TVDB
├── management/commands/process_downloads.py
└── utils/
```

**Models**: `Show`, `Episode`, `Movie`, `CastMember`, `NZBDownload`, `DuplicateDeletionLog`

## Common Commands
```powershell
python manage.py runserver                    # Dev server
python manage.py process_downloads            # Process downloads
python manage.py migrate                      # Database
python manage.py check                        # Verify setup
```

## Configuration
Environment variables (see `.env.example`):
- Database: `DJANGO_DB_PASSWORD`
- Plex: `PLEX_EMAIL`, `PLEX_API_KEY`, `PLEX_SERVER`
- TVDB: `TVDB_API_KEY`
- Downloads: `NZBGEEK_USERNAME`, `NZBGEEK_PASSWORD`
- Paths: `NZBGET_*_DIR`, `PLEX_*_DIR`, `SHOW_FOLDER_PATH`, `TEMP_FOLDER_PATH`

## Archived Docs
Located in `archive/` - not in version control:
- PostgreSQL upgrades
- Investigations & research
- Bug fixes & history
- Automation research

See `INDEX.md` for detailed navigation.

## Status
✅ Media library, Plex sync, TVDB integration  
⚠️ NZBGet automation disabled (use manual `process_downloads`)

