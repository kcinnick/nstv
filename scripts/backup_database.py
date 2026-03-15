#!/usr/bin/env python3
"""
PostgreSQL Backup Script
Creates a full backup of PostgreSQL database with timestamp
Safe to run multiple times
"""

import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

def find_pg_dump():
    """Find pg_dump executable"""
    paths = [
        'pg_dump',
        'C:\\Program Files\\PostgreSQL\\16\\bin\\pg_dump.exe',
        'C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe',
        'C:\\Program Files\\PostgreSQL\\14\\bin\\pg_dump.exe',
        'C:\\Program Files\\PostgreSQL\\12\\bin\\pg_dump.exe',
    ]

    for path in paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, timeout=2)
            if result.returncode == 0:
                return path
        except:
            pass
    return None

def create_backup():
    """Create backup of PostgreSQL database"""

    print("=" * 70)
    print("PostgreSQL Database Backup")
    print("=" * 70)

    # Find pg_dump
    pg_dump = find_pg_dump()
    if not pg_dump:
        print("\n✗ Error: Could not find pg_dump executable")
        print("\nPlease ensure PostgreSQL is installed.")
        return False

    print(f"\n✓ Found pg_dump: {pg_dump}")

    # Create backup directory
    backup_dir = Path.home() / 'PostgreSQL_Backups'
    backup_dir.mkdir(exist_ok=True, parents=True)

    # Create timestamped backup file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'postgres_backup_{timestamp}.sql'

    print(f"✓ Backup directory: {backup_dir}")
    print(f"✓ Backup file: {backup_file}")

    # Run backup
    print("\n[*] Creating backup... (this may take a minute)")

    # Set up environment with password
    env = os.environ.copy()
    env['PGPASSWORD'] = 'admin'

    cmd = f'"{pg_dump}" -h 127.0.0.1 -U postgres -d postgres > "{backup_file}"'

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=300, env=env)

        if backup_file.exists() and backup_file.stat().st_size > 0:
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            print(f"\n✓ Backup successful!")
            print(f"  File: {backup_file}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"\n✗ Backup failed - file not created or empty")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"\n✗ Backup timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"\n✗ Backup error: {e}")
        return False

def list_backups():
    """List existing backups"""
    backup_dir = Path.home() / 'PostgreSQL_Backups'

    if not backup_dir.exists():
        print("\nNo backups found yet.")
        return

    backups = sorted(backup_dir.glob('postgres_backup_*.sql'), reverse=True)

    if not backups:
        print("\nNo backups found.")
        return

    print("\n" + "=" * 70)
    print("Existing Backups")
    print("=" * 70)

    for i, backup in enumerate(backups[:10], 1):  # Show last 10
        size_mb = backup.stat().st_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{i}. {backup.name}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Date: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='PostgreSQL Backup Tool')
    parser.add_argument('--list', action='store_true', help='List existing backups')
    args = parser.parse_args()

    if args.list:
        list_backups()
        return 0

    success = create_backup()

    print("\n" + "=" * 70)
    print("Backup Tips")
    print("=" * 70)
    print("""
- Run backup before major upgrades
- Keep backups for 30 days
- Backups are stored: ~/PostgreSQL_Backups/
- To list backups: python scripts/backup_database.py --list
- To restore: psql -h 127.0.0.1 -U postgres < backup_file.sql

Schedule regular backups using Windows Task Scheduler:
1. Open Task Scheduler
2. Create new task
3. Trigger: Daily or Weekly
4. Action: python scripts/backup_database.py
5. Working directory: C:\\Users\\Nick\\PycharmProjects\\nstv
""")

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())

