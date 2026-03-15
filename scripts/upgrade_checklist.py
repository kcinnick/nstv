#!/usr/bin/env python3
"""
Quick Reference: PostgreSQL Upgrade Checklist
Print this file and follow the steps
"""

CHECKLIST = """
╔════════════════════════════════════════════════════════════════════════════╗
║           PostgreSQL 12 → 14+ Upgrade - Quick Reference                   ║
║                    (Data-Safe, No Data Loss)                              ║
╚════════════════════════════════════════════════════════════════════════════╝

CURRENT STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ PostgreSQL: 12.17
✓ Password: admin
✓ Backup: Created (1.01 MB)
✓ Location: C:\\Users\\Nick\\PostgreSQL_Backups\\postgres_backup_20260315_155657.sql
✓ Django: 5.2.11 (requires PostgreSQL 14+)


PRE-UPGRADE CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Read: docs/POSTGRESQL_UPGRADE_GUIDE.md
☐ Backup verified: python scripts/backup_database.py --list
☐ Downloaded PostgreSQL 16 installer
☐ Closed Django application
☐ Closed pgAdmin (if using)
☐ Administrative access ready (for running installer)


UPGRADE PROCEDURE (Option A - Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: DOWNLOAD
   → https://www.postgresql.org/download/windows/
   → Click "PostgreSQL 16" (or 15/14)
   → Download the full INSTALLER (not ZIP)
   
   Estimated time: 2 minutes

Step 2: RUN INSTALLER
   → Right-click installer → "Run as Administrator"
   → Follow the installation wizard
   → Choose "Install/Upgrade" (should auto-detect PostgreSQL 12)
   → When prompted for password, enter: admin
   → Let it continue - it will upgrade automatically
   
   Estimated time: 10-15 minutes
   (Screen will show upgrade progress)

Step 3: WAIT FOR COMPLETION
   → Don't close any windows
   → Don't restart computer
   → Wait for installer to finish
   → Should show "Installation successful"

Step 4: VERIFY UPGRADE
   Run this command:
   
   python scripts/verify_upgrade.py
   
   Expected output:
   ✓ PostgreSQL Version Check (should show 14+)
   ✓ Django Connection Test (should pass)
   ✓ Database Data Integrity (should pass)
   ✓ Django Models Loading (should pass)
   ✓ Migrations Status (should pass)
   
   Result: 5/5 checks passed ✓

Step 5: RUN MIGRATIONS (usually not needed)
   python manage.py migrate
   
   Expected: No migrations to apply

Step 6: START APPLICATION
   python manage.py runserver
   
   Then visit: http://localhost:8000
   Verify: Shows and movies appear correctly


POST-UPGRADE VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Check PostgreSQL version:
  python scripts/test_postgres_connection.py
  Expected: PostgreSQL 14+ (not 12)

✓ Check Django compatibility:
  python manage.py check
  Expected: System check identified no issues

✓ Check data integrity:
  python manage.py shell
  >>> from nstv.models import Show, Movie
  >>> Show.objects.count()  # Should show your shows
  >>> Movie.objects.count()  # Should show your movies

✓ Access admin:
  python manage.py runserver
  Visit: http://localhost:8000/admin
  Login and verify shows/movies appear


TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: "PostgreSQL still shows version 12"
Solution:
  1. Restart PostgreSQL service: net stop postgresql-x64-12
  2. Then start new version: net start postgresql-x64-14 (or 15/16)
  3. Rerun: python scripts/verify_upgrade.py

Problem: "Django says incompatible version"
Solution:
  1. Restart Python: python -c "import sys; print(sys.version)"
  2. Restart Django: python manage.py runserver
  3. Clear cache: del /s __pycache__

Problem: "Password authentication failed"
Solution:
  1. Verify you entered "admin" when installer asked for password
  2. Restore from backup and retry
  3. Run: python scripts/test_postgres_connection.py

Problem: "Installer can't find PostgreSQL 12"
Solution:
  1. Check installation location: C:\\Program Files\\PostgreSQL\\12
  2. Try manual upgrade with pg_upgrade (see guide)
  3. Or restore from backup and do dump/restore


ROLLBACK (If Something Goes Wrong)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Stop PostgreSQL service:
   net stop postgresql-x64-14

2. Uninstall PostgreSQL 14:
   Control Panel → Uninstall a program → PostgreSQL → Uninstall

3. Reinstall PostgreSQL 12:
   Download from: https://www.postgresql.org/download/windows/
   Choose version 12
   Install with password: admin

4. Restore from backup:
   psql -h 127.0.0.1 -U postgres < "C:\\Users\\Nick\\PostgreSQL_Backups\\postgres_backup_*.sql"

5. Verify:
   python scripts/test_postgres_connection.py
   Should show: PostgreSQL 12.17 and password works

Your data is NEVER lost - you can always restore!


IMPORTANT NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  PASSWORD DURING INSTALL
   When the installer asks "Enter password for postgres user"
   Type: admin
   (Same as your current password)

⚠️  DON'T RESTART COMPUTER
   If prompted during install, don't restart
   Let installer finish first, then you can restart

⚠️  KEEP BACKUP
   Keep the backup file for 30 days
   Location: C:\\Users\\Nick\\PostgreSQL_Backups\\
   After 30 days, you can delete if everything works

⚠️  ADMIN RIGHTS
   Right-click installer → "Run as Administrator"
   This is required to upgrade system services


ESTIMATED TIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Download installer:        2-5 minutes
Run installer:            10-15 minutes
Verify upgrade:            2-3 minutes
Test application:          5 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                    20-30 minutes


NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Download PostgreSQL 16 from: https://www.postgresql.org/download/windows/
2. Run the installer with admin rights
3. When asked for password: type admin
4. Wait for completion
5. Run: python scripts/verify_upgrade.py
6. Run: python manage.py runserver
7. Test at: http://localhost:8000

Questions? See: docs/POSTGRESQL_UPGRADE_GUIDE.md


╔════════════════════════════════════════════════════════════════════════════╗
║  STATUS: 🟢 READY TO UPGRADE  (Data backed up, password confirmed)        ║
║  RISK:   🟢 LOW               (Multiple safety layers)                    ║
║  ACTION: Download PostgreSQL 16 and run installer                          ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

if __name__ == '__main__':
    print(CHECKLIST)

    # Optionally save to file
    from pathlib import Path
    output_file = Path(__file__).resolve().parent.parent / 'UPGRADE_CHECKLIST.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(CHECKLIST)

    print(f"\n✓ Checklist saved to: {output_file}")

