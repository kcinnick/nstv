# Environment Variable Recovery Guide

## Summary

Your `.env` file has been successfully recreated with all the necessary environment variables. The **DJANGO_DB_PASSWORD** has been automatically recovered from your Django settings.

## Your DJANGO_DB_PASSWORD

```
DJANGO_DB_PASSWORD=penguin
```

## Files Created

Two helper scripts have been created in `scripts/`:

### 1. `recover_django_password.py`
Analyzes your codebase to identify all environment variables that need to be set.

**Usage:**
```bash
python scripts/recover_django_password.py
```

**Output:**
- Shows the recovered `DJANGO_DB_PASSWORD`
- Lists all environment variables used in the codebase
- Provides a template for recreating `.env`

### 2. `recreate_env_file.py`
Automatically recreates the `.env` file with the recovered database password.

**Usage:**
```bash
python scripts/recreate_env_file.py
```

**Output:**
- Creates a new `.env` file in the project root
- Fills in `DJANGO_DB_PASSWORD` automatically
- Provides empty fields for other variables you need to fill manually

## Next Steps

Edit your `.env` file and fill in the remaining environment variables:

```
DJANGO_DB_PASSWORD=penguin            ✓ Already filled
PLEX_EMAIL=                            ← Your Plex account email
PLEX_API_KEY=                          ← Get from plex.tv/api
PLEX_SERVER=                           ← Your Plex server name
SHOW_FOLDER_PATH=                      ← Path to your shows folder
TEMP_FOLDER_PATH=                      ← Path for temporary files
NZBGET_COMPLETE_DIR=                   ← NZBGet completed downloads
PLEX_TV_SHOW_DIR=                      ← Plex TV library path
PLEX_MOVIES_DIR=                        ← Plex movies library path
NZBGET_NZB_DIR=                        ← NZBGet NZB folder
```

## How It Works

The recovery scripts work by:

1. **Database Password**: Extracted from hardcoded values in `djangoProject/settings.py`
   - Line: `'PASSWORD': 'penguin'`

2. **Other Variables**: Identified by searching for `os.getenv()` calls throughout the codebase
   - Found in `nstv/views.py`, `nstv/management/commands/`, `nstv/plexController/`, etc.

## Security Note

- The `DJANGO_DB_PASSWORD` is recovered from your Django settings file
- This is a local recovery process - no external services are contacted
- Make sure your `.env` file is properly secured and never committed to version control
- Add `.env` to your `.gitignore` file if not already present

