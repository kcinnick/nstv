#!/usr/bin/env python3
"""
PostgreSQL Upgrade Verification Script
Run this after upgrading PostgreSQL to verify everything works
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Run command and return success status"""
    if description:
        print(f"\n[*] {description}...", end=" ")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False, "", "Command timed out"
    except Exception as e:
        print("ERROR")
        return False, "", str(e)

def verify_postgres_version():
    """Check PostgreSQL version"""
    print("\n" + "=" * 70)
    print("PostgreSQL Upgrade Verification")
    print("=" * 70)

    success, stdout, stderr = run_command(
        'psql -h 127.0.0.1 -U postgres -d postgres -c "SELECT version();"',
        "Checking PostgreSQL version"
    )

    if success:
        print("✓")
        # Extract version info
        lines = stdout.strip().split('\n')
        if lines:
            version_line = lines[-1].strip()
            print(f"  {version_line}")

            # Check if version is 14 or higher
            if 'PostgreSQL 1' in version_line and any(str(v) in version_line for v in [14, 15, 16, 17, 18]):
                print("  ✓ Version 14+ detected - Django compatible!")
                return True
            elif 'PostgreSQL 12' in version_line:
                print("  ✗ Still PostgreSQL 12 - upgrade may not have completed")
                return False
            else:
                return True
    else:
        print("✗")
        print(f"  Error: {stderr}")
        return False

def verify_django_connection():
    """Test Django database connection"""
    success, stdout, stderr = run_command(
        'python manage.py check',
        "Checking Django compatibility"
    )

    if success:
        print("✓")
        print("  Django can connect to database")
        return True
    else:
        print("✗")
        if "PostgreSQL 14 or later is required" in stderr:
            print("  ERROR: Django still detected old PostgreSQL version")
            print("  Try restarting PostgreSQL service or your Django server")
        else:
            print(f"  Error: {stderr[:100]}")
        return False

def count_database_objects():
    """Count tables and records to verify data integrity"""
    success, stdout, stderr = run_command(
        'psql -h 127.0.0.1 -U postgres -d postgres -c "SELECT COUNT(*) as tables FROM information_schema.tables WHERE table_schema=\'public\';"',
        "Verifying data integrity (counting tables)"
    )

    if success:
        print("✓")
        lines = [l.strip() for l in stdout.strip().split('\n') if l.strip() and not l.strip().startswith('-')]
        if lines:
            count = lines[-1].strip()
            if count.isdigit():
                print(f"  Tables found: {count}")
                if int(count) > 0:
                    print("  ✓ Database has data")
                    return True
        return False
    else:
        print("✗")
        print(f"  Error: {stderr[:100]}")
        return False

def verify_django_models():
    """Verify Django can load models"""
    success, stdout, stderr = run_command(
        'python -c "import django; django.setup(); from nstv.models import Show, Movie; print(f\'Shows: {Show.objects.count()}, Movies: {Movie.objects.count()}\')"',
        "Verifying Django models and data"
    )

    if success:
        print("✓")
        print(f"  {stdout.strip()}")
        return True
    else:
        print("✗")
        if "ModuleNotFoundError" in stderr:
            print("  Note: Run from project root directory")
        else:
            print(f"  Error: {stderr[:100]}")
        return False

def verify_migrations():
    """Check if migrations are applied"""
    success, stdout, stderr = run_command(
        'python manage.py migrate --check',
        "Checking Django migrations"
    )

    if success:
        print("✓")
        print("  All migrations applied")
        return True
    else:
        print("✗")
        if "No changes detected" in stderr or "No migrations to apply" in stderr:
            print("  Note: Migrations already applied")
            return True
        else:
            print(f"  Pending migrations found")
            return False

def generate_report():
    """Generate final verification report"""
    print("\n" + "=" * 70)
    print("Upgrade Verification Report")
    print("=" * 70)

    # Change to project directory
    project_dir = Path(__file__).resolve().parent.parent
    import os
    os.chdir(project_dir)

    results = {}

    # Run all checks
    print("\nRunning verification checks...")
    results['postgres_version'] = verify_postgres_version()
    results['django_connection'] = verify_django_connection()
    results['data_integrity'] = count_database_objects()
    results['django_models'] = verify_django_models()
    results['migrations'] = verify_migrations()

    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    checks = {
        'PostgreSQL Version Check': results['postgres_version'],
        'Django Connection Test': results['django_connection'],
        'Database Data Integrity': results['data_integrity'],
        'Django Models Loading': results['django_models'],
        'Migrations Status': results['migrations'],
    }

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    for check, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:10} - {check}")

    print(f"\nResult: {passed}/{total} checks passed")

    if passed == total:
        print("\n✅ Upgrade successful! Your Django application is ready.")
        print("\nNext steps:")
        print("  1. python manage.py runserver")
        print("  2. Visit http://localhost:8000")
        print("  3. Test that shows/movies appear correctly")
        return 0
    elif passed >= 3:
        print("\n⚠️  Most checks passed, but some issues found.")
        print("Try:")
        print("  1. Restart PostgreSQL service: net stop postgresql-x64-14 (or 15/16)")
        print("  2. Then: net start postgresql-x64-14")
        print("  3. Rerun this script: python scripts/verify_upgrade.py")
        return 1
    else:
        print("\n❌ Upgrade verification failed. Please check:")
        print("  1. PostgreSQL service is running")
        print("  2. Password is correct (admin)")
        print("  3. Run from project directory")
        print("  4. Check PostgreSQL logs: C:\\Program Files\\PostgreSQL\\14\\data\\pg_log\\")
        return 1

if __name__ == '__main__':
    sys.exit(generate_report())

