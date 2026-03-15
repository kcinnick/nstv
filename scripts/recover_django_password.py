#!/usr/bin/env python3
"""
Script to recover environment variables from Django settings and codebase
Useful when .env file is accidentally deleted.
"""

import re
from pathlib import Path
from dotenv import dotenv_values


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


def extract_nzbget_env_vars():
    """Extract NZBGet related environment variables from Python files"""
    project_root = Path(__file__).resolve().parent.parent
    env_vars = {}

    # Search for os.getenv references in the codebase
    patterns = {
        'NZBGET_COMPLETE_DIR': r'os\.getenv\(["\']NZBGET_COMPLETE_DIR["\']\)',
        'PLEX_TV_SHOW_DIR': r'os\.getenv\(["\']PLEX_TV_SHOW_DIR["\']\)',
        'PLEX_MOVIES_DIR': r'os\.getenv\(["\']PLEX_MOVIES_DIR["\']\)',
        'PLEX_EMAIL': r'os\.getenv\(["\']PLEX_EMAIL["\']\)',
        'PLEX_API_KEY': r'os\.getenv\(["\']PLEX_API_KEY["\']\)',
        'PLEX_SERVER': r'os\.getenv\(["\']PLEX_SERVER["\']\)',
        'SHOW_FOLDER_PATH': r'os\.getenv\(["\']SHOW_FOLDER_PATH["\']\)',
        'TEMP_FOLDER_PATH': r'os\.getenv\(["\']TEMP_FOLDER_PATH["\']\)',
        'NZBGET_NZB_DIR': r'os\.getenv\(["\']NZBGET_NZB_DIR["\']\)',
    }

    # These are found in the codebase
    found_vars = set()
    for py_file in project_root.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for var_name, pattern in patterns.items():
                    if re.search(pattern, content):
                        found_vars.add(var_name)
        except:
            pass

    return found_vars


def main():
    print("=" * 60)
    print("Django Environment Variable Recovery Tool")
    print("=" * 60)
    print()

    # Database password
    db_password = extract_db_password()
    if db_password:
        print(f"✓ DJANGO_DB_PASSWORD={db_password}")
    else:
        print("✗ Could not find DJANGO_DB_PASSWORD in settings.py")

    print()
    print("Environment variables used in the codebase:")
    print("-" * 60)
    found_vars = extract_nzbget_env_vars()

    for var in sorted(found_vars):
        print(f"  • {var}")

    print()
    print("=" * 60)
    print("To recreate .env file:")
    print("=" * 60)
    print()
    print("DJANGO_DB_PASSWORD=" + (db_password or "YOUR_PASSWORD_HERE"))
    print("PLEX_EMAIL=")
    print("PLEX_API_KEY=")
    print("PLEX_SERVER=")
    print("SHOW_FOLDER_PATH=")
    print("TEMP_FOLDER_PATH=")
    print("NZBGET_COMPLETE_DIR=")
    print("PLEX_TV_SHOW_DIR=")
    print("PLEX_MOVIES_DIR=")
    print("NZBGET_NZB_DIR=")
    print()


if __name__ == '__main__':
    main()

