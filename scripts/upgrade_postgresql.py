#!/usr/bin/env python3
"""
PostgreSQL Upgrade Guide - Version 12 to 14+
Complete backup and upgrade procedure without data loss
"""

import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd, description=""):
    """Run a shell command and return output"""
    if description:
        print(f"\n[*] {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"    ✓ Success")
            return result.stdout
        else:
            print(f"    ✗ Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return None

def backup_database():
    """Create a backup of the current PostgreSQL database"""
    backup_dir = Path.home() / 'PostgreSQL_Backups'
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'postgres_backup_{timestamp}.sql'

    print("\n" + "=" * 70)
    print("STEP 1: Backup Current Database")
    print("=" * 70)

    # Find pg_dump
    pg_dump_paths = [
        'pg_dump',
        'C:\\Program Files\\PostgreSQL\\12\\bin\\pg_dump.exe',
        'C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe',
    ]

    pg_dump = None
    for path in pg_dump_paths:
        try:
            if subprocess.run([path, '--version'], capture_output=True).returncode == 0:
                pg_dump = path
                break
        except:
            pass

    if not pg_dump:
        print("✗ Could not find pg_dump")
        return None

    print(f"\n✓ Found pg_dump: {pg_dump}")
    print(f"✓ Backup location: {backup_file}")

    # Set up environment with password
    env = os.environ.copy()
    env['PGPASSWORD'] = 'admin'

    cmd = f'"{pg_dump}" -h 127.0.0.1 -U postgres -d postgres > "{backup_file}"'

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=300, env=env)
        if result.returncode != 0:
            print(f"    ✗ Error: {result.stderr}")
    except Exception as e:
        print(f"    ✗ Exception: {e}")

    if backup_file.exists() and backup_file.stat().st_size > 0:
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"✓ Backup created: {backup_file} ({size_mb:.2f} MB)")
        return backup_file
    else:
        print("✗ Backup failed - file not created or empty")
        return None

def show_upgrade_steps():
    """Show the upgrade procedure"""
    print("\n" + "=" * 70)
    print("STEP 2: PostgreSQL Upgrade Procedure")
    print("=" * 70)

    steps = """
OPTION A: Using PostgreSQL Installer (Recommended for Windows)
============================================================

1. STOP PostgreSQL Service
   - Open Services (services.msc)
   - Find "PostgreSQL - Version 12" service
   - Right-click → Stop

2. DOWNLOAD PostgreSQL 14+
   - Visit: https://www.postgresql.org/download/windows/
   - Download PostgreSQL 16 (latest stable)
   - Or PostgreSQL 14 (long-term support)

3. RUN UPGRADE WIZARD
   - Run the PostgreSQL installer
   - Choose "Update" installation (not "New")
   - The installer will:
     * Detect your PostgreSQL 12 installation
     * Perform an in-place upgrade
     * Migrate all data automatically
     * Preserve all databases and users

4. VERIFY UPGRADE
   - Check Windows Services - PostgreSQL service should be running
   - Test connection with: python scripts/test_postgres_connection.py

5. UPDATE DJANGO
   - Your .env file password (admin) remains the same
   - Django will automatically detect the new version
   - Run migrations: python manage.py migrate

---

OPTION B: Using pg_upgrade (Advanced)
=====================================

1. Backup (already done above)

2. Download and install PostgreSQL 14+ in separate location
   - Don't run the installer's upgrade wizard
   - Just extract/install to a different directory

3. Stop PostgreSQL 12 service
   - net stop postgresql-x64-12

4. Run pg_upgrade
   - cd "C:\\Program Files\\PostgreSQL\\14\\bin"
   - pg_upgrade.exe ^
       --old-datadir "C:\\Program Files\\PostgreSQL\\12\\data" ^
       --new-datadir "C:\\Program Files\\PostgreSQL\\14\\data" ^
       --old-bindir "C:\\Program Files\\PostgreSQL\\12\\bin" ^
       --new-bindir "C:\\Program Files\\PostgreSQL\\14\\bin"

5. Replace PostgreSQL 12 with 14
   - Copy new data directory to PostgreSQL location
   - Update Windows Services to point to new version

6. Start PostgreSQL service and verify

---

OPTION C: Restore from Backup (if Something Goes Wrong)
======================================================

If the upgrade fails, you can restore from backup:

1. Find pg_restore or psql
   - pg_restore for custom format backups
   - psql for .sql format backups

2. Stop PostgreSQL service

3. Reinstall PostgreSQL 12 or downgrade

4. Restore database:
   psql -h 127.0.0.1 -U postgres -d postgres < backup_file.sql

---

RECOMMENDED: Use Option A (PostgreSQL Installer)
===============================================

It's the simplest and most reliable for Windows users.
The installer handles everything automatically.
"""

    print(steps)
    return True

def show_django_compatibility():
    """Show Django version compatibility info"""
    print("\n" + "=" * 70)
    print("STEP 3: Django Compatibility Check")
    print("=" * 70)

    compat = """
Current Setup:
  Django: 5.2.11
  PostgreSQL: 12.17 (current)

After Upgrade:
  ✓ Django 5.2.11 fully supports PostgreSQL 14+
  ✓ No Django changes needed
  ✓ Your .env password remains: admin
  ✓ Your .env DATABASE_NAME remains: postgres
  ✓ All data will be migrated automatically

Post-Upgrade Steps:
  1. python manage.py check
  2. python manage.py migrate
  3. python manage.py runserver
  4. Verify all shows/movies still appear in admin
"""

    print(compat)

def show_data_loss_prevention():
    """Show how data is protected"""
    print("\n" + "=" * 70)
    print("Data Loss Prevention Checklist")
    print("=" * 70)

    checklist = """
Your data is protected by:

✓ Backup File Created
  Location: C:\\Users\\{username}\\PostgreSQL_Backups\\
  Format: SQL dump (portable, human-readable)
  Can be restored to any PostgreSQL version
  Keep for 30 days after successful upgrade

✓ PostgreSQL Automatic Migration
  The upgrade process preserves:
  - All databases
  - All tables and data
  - All users and permissions
  - All views, sequences, indexes
  - Transaction history

✓ Django Migration Compatibility
  Django's migration system:
  - Records all schema changes
  - Can roll back if needed
  - Stored in: nstv/migrations/

✓ Double Verification
  After upgrade:
  1. Django can connect to database
  2. All tables are present
  3. All data is readable
  4. Run full test suite: pytest

RECOMMENDED BACKUP RETENTION:
- Keep backup file for 30 days
- After 30 days: upgrade verified, backup can be deleted
- Long-term: use backup script weekly
  python scripts/backup_database.py  (to be created)
"""

    print(checklist)

def show_rollback_plan():
    """Show how to rollback if needed"""
    print("\n" + "=" * 70)
    print("Emergency Rollback Plan (If Something Goes Wrong)")
    print("=" * 70)

    rollback = """
If upgrade fails or causes issues:

1. RESTORE FROM BACKUP
   a. Download PostgreSQL 12 again
   b. Reinstall PostgreSQL 12
   c. Run backup restoration:
      
      set PGPASSWORD=admin
      psql -h 127.0.0.1 -U postgres -d postgres < backup_file.sql
   
   d. Verify with: python scripts/test_postgres_connection.py
   e. Django still works (version compatibility unchanged)

2. INVESTIGATE ISSUE
   - Check PostgreSQL error logs
   - Verify disk space
   - Check Windows Event Viewer for errors

3. RETRY UPGRADE
   - Fix any issues found
   - Create fresh backup
   - Run upgrade again

IMPORTANT: You have a backup, so worst case is you restore it!
"""

    print(rollback)

def main():
    print("=" * 70)
    print("PostgreSQL 12 → 14+ Upgrade Guide")
    print("Data-Safe Upgrade Procedure")
    print("=" * 70)

    # Create backup
    backup_file = backup_database()

    if not backup_file:
        print("\n✗ Backup failed. Please fix backup before upgrading.")
        return 1

    # Show upgrade steps
    show_upgrade_steps()

    # Show Django compatibility
    show_django_compatibility()

    # Show data loss prevention
    show_data_loss_prevention()

    # Show rollback plan
    show_rollback_plan()

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. ✓ Backup created: See location above
2. Choose upgrade method (recommended: Option A - PostgreSQL Installer)
3. Follow the selected option's steps
4. Run: python scripts/test_postgres_connection.py
5. Run: python manage.py check
6. Run: python manage.py migrate
7. Test your Django application

Questions or issues? Check:
- PostgreSQL logs: C:\\Program Files\\PostgreSQL\\14\\data\\pg_log
- Django logs: Add logging to settings.py
- Windows Event Viewer: For system errors
""")

    return 0

if __name__ == '__main__':
    sys.exit(main())

