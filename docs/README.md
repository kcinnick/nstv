# Documentation Index

## Getting Started
- **[README.rst](../README.rst)** - Main project overview, features, and quick start
- **[instructions.md](../instructions.md)** - Claude AI coding guidelines and technical reference

## Features & Workflows

### Post-Download Automation
- **[POST_DOWNLOAD_AUTOMATION.md](POST_DOWNLOAD_AUTOMATION.md)** ⭐ **START HERE** - Quick reference for processing downloads
- **[AUTOMATION.md](AUTOMATION.md)** - Full automation guide with all setup options
- **[NZBGET_SETUP.md](NZBGET_SETUP.md)** - NZBGet integration setup (currently disabled)

### Duplicate Media Management
- **Duplicate Detection** - Built into web UI at `/duplicates/`
- **Quality Analysis** - Automatic ranking of duplicate versions
- **Plex API Deletion** - Remote file deletion without NAS filesystem access
- See [instructions.md](../instructions.md) section on "find_duplicates & duplicate_deletion"

### TVDB Metadata Enrichment
- Import show/episode metadata from TVDB
- Automatic deduplication during import
- See [instructions.md](../instructions.md) section on "TVDB Import"

## Reference

### Maintenance & Tasks
- **[MANUAL_TASKS.md](MANUAL_TASKS.md)** - Regular maintenance tasks and reminders
- **[BUGS.md](BUGS.md)** - Known issues, workarounds, and bug tracking

### Design & Development
- **[frontend-design-guidelines.md](../frontend-design-guidelines.md)** - HTML/CSS design system
- **[instructions.md](../instructions.md)** - Full technical reference for developers/AI

## Quick Command Reference

### Daily Operations
```powershell
# Process completed downloads
.venv\Scripts\python.exe manage.py process_downloads

# Run development server
python manage.py runserver

# Check for duplicate media (web UI)
# Visit: http://127.0.0.1:8000/duplicates/
```

### Database Operations
```powershell
# Run migrations
python manage.py migrate

# Audit duplicate episodes
python manage.py audit_episode_duplicates

# Fix movie titles with embedded years
python manage.py fix_movie_titles --dry-run
```

### Plex Sync
```powershell
# Sync shows and episodes
python nstv/plexController/add_shows_to_nstv.py
python nstv/plexController/add_episodes_to_show.py

# Sync movies
python nstv/plexController/add_movies_to_nstv.py
```

## Architecture Overview

### Key Components
```
nstv/
├── models.py                    # Django models (Show, Episode, Movie, etc.)
├── views.py                     # Web interface handlers
├── download.py                  # NZBGeek integration
├── management/commands/         # Django CLI commands
│   ├── process_downloads.py   # Post-download automation
│   ├── audit_episode_duplicates.py
│   └── fix_movie_titles.py
├── plexController/             # Plex server integration
│   ├── add_shows_to_nstv.py
│   ├── add_episodes_to_show.py
│   ├── add_movies_to_nstv.py
│   ├── find_duplicates.py     # Duplicate detection
│   ├── duplicate_deletion.py  # Plex API deletion
│   └── quality_analyzer.py    # Media quality scoring
└── get_info_from_tvdb/        # TVDB metadata import

templates/                      # Django HTML templates
scripts/                        # Automation scripts
docs/                          # Documentation (you are here)
```

### Data Flow
1. **Media downloaded** → NZBGet complete directory
2. **Auto-processing** (disabled) or manual `process_downloads` command
3. **Files moved** to Plex TV/Movie directories
4. **Plex scan** detects new media
5. **Django sync** updates database from Plex
6. **TVDB enrichment** adds detailed metadata
7. **Web UI** displays media library

### Database Models
- `Show` - TV series with metadata
- `Episode` - Individual episodes linked to shows
- `Movie` - Movies with metadata
- `CastMember` - Actors/crew (many-to-many with shows/episodes/movies)
- `NZBDownload` - Download tracking
- `DuplicateDeletionLog` - Audit trail for deleted duplicates

## Environment Configuration

Required environment variables (see `.env.example`):
- **Django**: `DJANGO_DB_PASSWORD`
- **Plex**: `PLEX_EMAIL`, `PLEX_API_KEY`, `PLEX_SERVER`
- **TVDB**: `TVDB_API_KEY`
- **NZBGeek**: `NZBGEEK_USERNAME`, `NZBGEEK_PASSWORD`
- **Paths**: `NZBGET_COMPLETE_DIR`, `PLEX_TV_SHOW_DIR`, `PLEX_MOVIES_DIR`

## Current Status

### Working Features ✅
- Media library browsing and search
- TVDB metadata import
- Duplicate media detection and cleanup
- Manual download processing
- Quality-based duplicate ranking
- Health status dashboard

### Known Issues ⚠️
- NZBGet post-processing automation disabled (Python path issue)
- See [BUGS.md](BUGS.md) for workarounds

### In Development 🚧
- Task Scheduler automation as NZBGet alternative
- Email notifications for duplicate scans

## Support & Troubleshooting

### Common Issues
1. **"Plex server is not accessible"** → Check NAS is online, verify environment variables
2. **"Permission denied"** → Run as administrator, check write permissions
3. **Slow file processing** → Normal for large files copying across network drives
4. **NZBGet hung** → Automation disabled, use manual processing

### Where to Look
- **Logs**: Check Django console output or `logs/` directory
- **Database**: Use Django admin interface at `/admin/`
- **Plex**: Check Plex web interface for scan status
- **NZBGet**: Check Messages tab in web interface

## Contributing

When making changes:
1. Use feature/bugfix branches (see [instructions.md](../instructions.md))
2. Update relevant documentation
3. Add tests for new functionality
4. Update [BUGS.md](BUGS.md) if fixing issues
5. Run `python manage.py check` before committing

---

**Last Updated**: 2026-03-10  
**Project**: nstv - TV Show & Movie Library Manager  
**Tech Stack**: Django 5.2, PostgreSQL 16, Plex API, TVDB API
