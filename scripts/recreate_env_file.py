#!/usr/bin/env python3
"""
Script to recreate .env file with recovered variables.
This script automatically fills in the DJANGO_DB_PASSWORD and provides
a template for other environment variables.
"""

import re
from pathlib import Path


def extract_db_password():
    """Extract DATABASE PASSWORD from settings.py"""
    settings_path = Path(__file__).resolve().parent.parent / 'djangoProject' / 'settings.py'

    if not settings_path.exists():
        return None

    with open(settings_path, 'r') as f:
        content = f.read()

    # Look for PASSWORD field in DATABASES configuration
    match = re.search(r"'PASSWORD'\s*:\s*['\"]([^'\"]+)['\"]", content)

    if match:
        return match.group(1)

    return None


def recreate_env_file():
    """Recreate the .env file with recovered and template values"""
    project_root = Path(__file__).resolve().parent.parent
    env_file_path = project_root / '.env'

    db_password = extract_db_password()

    if not db_password:
        print("✗ Error: Could not find DJANGO_DB_PASSWORD in settings.py")
        return False

    # Create the .env file content
    env_content = f"""DJANGO_DB_PASSWORD={db_password}
PLEX_EMAIL=
PLEX_API_KEY=
PLEX_SERVER=
SHOW_FOLDER_PATH=
TEMP_FOLDER_PATH=
NZBGET_COMPLETE_DIR=
PLEX_TV_SHOW_DIR=
PLEX_MOVIES_DIR=
NZBGET_NZB_DIR=
"""

    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)

        print("✓ Successfully created .env file at:", env_file_path)
        print()
        print("File contents:")
        print("-" * 60)
        print(env_content)
        print("-" * 60)
        print()
        print("Next steps:")
        print("1. Fill in the remaining environment variables:")
        print("   - PLEX_EMAIL: Your Plex account email")
        print("   - PLEX_API_KEY: Your Plex API key")
        print("   - PLEX_SERVER: Your Plex server name")
        print("   - SHOW_FOLDER_PATH: Path to your shows folder")
        print("   - TEMP_FOLDER_PATH: Path to temporary folder")
        print("   - NZBGET_COMPLETE_DIR: NZBGet completed downloads folder")
        print("   - PLEX_TV_SHOW_DIR: Plex TV shows library folder")
        print("   - PLEX_MOVIES_DIR: Plex movies library folder")
        print("   - NZBGET_NZB_DIR: NZBGet NZB folder")
        print()

        return True
    except Exception as e:
        print(f"✗ Error creating .env file: {e}")
        return False


if __name__ == '__main__':
    success = recreate_env_file()
    exit(0 if success else 1)

