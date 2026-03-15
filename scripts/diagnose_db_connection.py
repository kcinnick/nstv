#!/usr/bin/env python3
"""
PostgreSQL Database Troubleshooting Tool

This script helps diagnose and fix database connection issues.
It provides options to:
1. Test connection with different password attempts
2. Reset PostgreSQL password (if local)
3. Show current settings
"""

import os
import subprocess
import sys
from pathlib import Path


def test_postgres_connection(password):
    """Test PostgreSQL connection with given password"""
    try:
        import psycopg2
        conn_string = f"dbname=postgres user=postgres password={password} host=127.0.0.1 port=5432"
        try:
            conn = psycopg2.connect(conn_string)
            conn.close()
            return True
        except psycopg2.OperationalError as e:
            return False
    except ImportError:
        print("psycopg2 not installed. Install with: pip install psycopg2-binary")
        return None


def show_current_settings():
    """Show current database settings from settings.py"""
    settings_path = Path(__file__).resolve().parent.parent / 'djangoProject' / 'settings.py'
    print("\n" + "=" * 60)
    print("Current Database Configuration (from settings.py)")
    print("=" * 60)

    if settings_path.exists():
        with open(settings_path, 'r') as f:
            lines = f.readlines()
            in_db_config = False
            for line in lines:
                if 'DATABASES' in line:
                    in_db_config = True
                if in_db_config:
                    print(line.rstrip())
                    if '}' in line and 'DATABASES' not in line:
                        # Stop after closing brace
                        if line.count('}') >= 2:
                            break


def try_common_passwords():
    """Try commonly used PostgreSQL passwords"""
    common_passwords = [
        'penguin',
        'password',
        'postgres',
        'admin',
        'admin123',
        'P@ssw0rd',
        'p@ssw0rd',
        'test',
        'test123',
        '',  # empty password
    ]

    print("\n" + "=" * 60)
    print("Testing Common PostgreSQL Passwords")
    print("=" * 60)

    for pwd in common_passwords:
        result = test_postgres_connection(pwd)
        status = "✓ SUCCESS" if result else ("✗ FAILED" if result is False else "? UNKNOWN")
        pwd_display = f"'{pwd}'" if pwd else "(empty)"
        print(f"{status:12} - Password: {pwd_display}")

        if result:
            print(f"\n⚠️  Found working password: {pwd_display}")
            return pwd

    return None


def check_postgres_service():
    """Check if PostgreSQL service is running"""
    print("\n" + "=" * 60)
    print("PostgreSQL Service Status")
    print("=" * 60)

    # Check if service exists
    result = subprocess.run(['sc', 'query', 'postgresql-x64-16'],
                          capture_output=True, text=True)

    if result.returncode == 0:
        if 'RUNNING' in result.stdout:
            print("✓ PostgreSQL service is RUNNING")
            return True
        elif 'STOPPED' in result.stdout:
            print("✗ PostgreSQL service is STOPPED")
            print("\nTo start PostgreSQL service, run:")
            print("  net start postgresql-x64-16")
            return False
    else:
        print("? PostgreSQL service not found or inaccessible")
        print("\nService names to try:")
        print("  - postgresql-x64-16")
        print("  - postgresql-x64-15")
        print("  - postgresql-x64-14")
        return None


def main():
    print("=" * 60)
    print("PostgreSQL Database Troubleshooting Tool")
    print("=" * 60)

    # Check if PostgreSQL is running
    service_status = check_postgres_service()

    if service_status is False:
        print("\n⚠️  PostgreSQL service is not running!")
        print("Start it and try again.")
        return 1

    # Show current settings
    show_current_settings()

    # Try to find working password
    print("\nSearching for valid PostgreSQL password...")
    working_password = try_common_passwords()

    if working_password is not None:
        print("\n" + "=" * 60)
        print("✓ Successfully found working password!")
        print("=" * 60)
        print(f"\nPassword: {working_password}")
        print("\nUpdate your .env file with:")
        print(f"DJANGO_DB_PASSWORD={working_password}")
        print("\nThen run:")
        print("python manage.py migrate")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ Could not find working password")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Verify PostgreSQL is installed and running")
        print("2. Reset PostgreSQL password:")
        print("   - Windows: Use pg_admin or psql from PostgreSQL bin directory")
        print("   - Run: psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'newpassword';\"")
        print("3. Update .env file with correct password")
        print("4. Run: python manage.py migrate")
        return 1


if __name__ == '__main__':
    sys.exit(main())

