#!/usr/bin/env python3
"""
PostgreSQL Connection Tester
Attempts to connect to PostgreSQL with various approaches
"""

import subprocess
import os
from pathlib import Path

def find_psql():
    """Try to find psql executable"""
    possible_paths = [
        'psql',  # In PATH
        'C:\\Program Files\\PostgreSQL\\16\\bin\\psql.exe',
        'C:\\Program Files\\PostgreSQL\\15\\bin\\psql.exe',
        'C:\\Program Files\\PostgreSQL\\14\\bin\\psql.exe',
        'C:\\Program Files (x86)\\PostgreSQL\\16\\bin\\psql.exe',
        'C:\\Program Files (x86)\\PostgreSQL\\15\\bin\\psql.exe',
    ]

    for path in possible_paths:
        if isinstance(path, str) and path.startswith('C:\\'):
            if os.path.exists(path):
                return path
        else:
            # Try to run it
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    return path
            except:
                pass

    return None

def test_with_psql(psql_path, password):
    """Test connection using psql command"""
    try:
        # Set password in environment for psql
        env = os.environ.copy()
        env['PGPASSWORD'] = password

        cmd = [
            psql_path,
            '-h', '127.0.0.1',
            '-U', 'postgres',
            '-d', 'postgres',
            '-c', 'SELECT version();'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, env=env)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def main():
    print("=" * 70)
    print("PostgreSQL Connection Tester")
    print("=" * 70)

    # Find psql
    psql = find_psql()
    if not psql:
        print("\n✗ Could not find psql executable")
        print("\nPlease ensure PostgreSQL is installed:")
        print("  1. Download from: https://www.postgresql.org/download/windows/")
        print("  2. Run the installer")
        print("  3. Note the password you set for 'postgres' user during installation")
        print("\nOr specify the path manually:")
        return 1

    print(f"\n✓ Found psql at: {psql}")

    # Try common passwords
    passwords_to_try = [
        'penguin',
        'password',
        'postgres',
        'admin',
        'admin123',
        'P@ssw0rd',
        '',
    ]

    print("\n" + "=" * 70)
    print("Testing passwords...")
    print("=" * 70)

    for pwd in passwords_to_try:
        pwd_display = f"'{pwd}'" if pwd else "(empty)"
        success, stdout, stderr = test_with_psql(psql, pwd)

        if success:
            print(f"\n✓ SUCCESS with password: {pwd_display}")
            print(f"\nPostgreSQL version:\n{stdout}")
            print("\nUpdate your .env file:")
            print(f"DJANGO_DB_PASSWORD={pwd}")
            return 0
        else:
            if 'FATAL' in stderr or 'password authentication' in stderr.lower():
                print(f"✗ Wrong password: {pwd_display}")
            else:
                print(f"? Error with {pwd_display}: {stderr[:50]}")

    print("\n" + "=" * 70)
    print("✗ Could not connect with any common password")
    print("=" * 70)
    print("\nYou need to reset the PostgreSQL password:")
    print("\n1. Open Command Prompt/PowerShell")
    print("2. Navigate to PostgreSQL bin directory (e.g., C:\\Program Files\\PostgreSQL\\16\\bin)")
    print("3. Run: psql -U postgres")
    print("4. At the password prompt, try 'postgres' or leave blank")
    print("5. Once connected, run: ALTER USER postgres WITH PASSWORD 'newpassword';")
    print("6. Update .env file with the new password")
    print("7. Run: python manage.py migrate")

    return 1

if __name__ == '__main__':
    exit(main())

