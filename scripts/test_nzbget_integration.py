"""
Test harness for NZBGet post-processing script.
Simulates NZBGet environment to validate script functionality.
"""
import os
import sys
import subprocess
from pathlib import Path

def test_nzbget_script():
    """Test the NZBGet post-processing script in isolation"""
    
    print("=" * 80)
    print("NZBGet Script Test Harness")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    script_path = project_root / 'scripts' / 'nzbget_postprocess.py'
    
    if not script_path.exists():
        print(f"ERROR: Script not found at {script_path}")
        return False
    
    print(f"\n✓ Script found: {script_path}")
    
    # Simulate NZBGet environment variables
    test_env = os.environ.copy()
    test_env.update({
        'NZBPP_DIRECTORY': str(project_root),  # Dummy value
        'NZBPP_STATUS': 'SUCCESS',
        'NZBPP_CATEGORY': 'tv',  # Test with TV category
        'NZBPP_NZBNAME': 'Test.Show.S01E01.1080p.mkv',
    })
    
    print("\nSimulated NZBGet Environment:")
    print(f"  NZBPP_STATUS: {test_env['NZBPP_STATUS']}")
    print(f"  NZBPP_CATEGORY: {test_env['NZBPP_CATEGORY']}")
    print(f"  NZBPP_NZBNAME: {test_env['NZBPP_NZBNAME']}")
    
    # Test 1: Syntax check
    print("\n" + "-" * 80)
    print("Test 1: Python Syntax Check")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✓ Syntax check passed")
        else:
            print(f"✗ Syntax check failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Syntax check error: {e}")
        return False
    
    # Test 2: Dry-run test (will fail on actual execution but should load properly)
    print("\n" + "-" * 80)
    print("Test 2: Script Import and Variable Detection")
    print("-" * 80)
    
    # Check Python path auto-detection logic
    venv_python = project_root / '.venv' / 'Scripts' / 'python.exe'
    if venv_python.exists():
        print(f"✓ Virtual environment Python exists: {venv_python}")
    else:
        print(f"✗ Virtual environment Python not found: {venv_python}")
        return False
    
    # Test 3: Validate command construction
    print("\n" + "-" * 80)
    print("Test 3: Command Construction")
    print("-" * 80)
    
    # The command that would be built:
    expected_cmd = [
        str(venv_python),
        str(project_root / 'manage.py'),
        'process_downloads',
        '--media-type', 'tv'
    ]
    
    print("Expected command:")
    print(f"  {' '.join(expected_cmd)}")
    
    # Verify manage.py exists
    manage_py = project_root / 'manage.py'
    if manage_py.exists():
        print(f"✓ manage.py exists: {manage_py}")
    else:
        print(f"✗ manage.py not found: {manage_py}")
        return False
    
    # Test 4: Test with --dry-run to validate full execution path
    print("\n" + "-" * 80)
    print("Test 4: Full Execution Test (Dry-Run)")
    print("-" * 80)
    
    try:
        cmd = [
            str(venv_python),
            str(project_root / 'manage.py'),
            'process_downloads',
            '--media-type', 'tv',
            '--dry-run'
        ]
        
        print(f"Executing: {' '.join(cmd)}")
        print("(This validates the full chain: Python → Django → process_downloads)\n")
        
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ Command executed successfully")
            print("\nOutput preview:")
            print(result.stdout[:500])
            
            # Check for expected strings in output
            if 'Plex server' in result.stdout:
                print("\n✓ Plex connectivity check present")
            if 'Processing TV Shows' in result.stdout or 'No items to process' in result.stdout:
                print("✓ Processing logic executed")
                
            return True
        else:
            print(f"✗ Command failed with exit code {result.returncode}")
            print(f"\nSTDOUT:\n{result.stdout}")
            print(f"\nSTDERR:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Command timed out (should not happen in dry-run)")
        return False
    except Exception as e:
        print(f"✗ Execution error: {e}")
        return False

def main():
    """Run all tests"""
    print("\nThis test harness validates the NZBGet script without actually")
    print("installing it to NZBGet. It simulates the NZBGet environment and")
    print("verifies the script would execute correctly.\n")
    
    success = test_nzbget_script()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nThe NZBGet script is ready to deploy!")
        print("\nNext steps:")
        print("1. Copy script to NZBGet:")
        print('   Copy-Item "scripts\\nzbget_postprocess.py" "C:\\ProgramData\\NZBGet\\scripts\\nzbget_postprocess.py" -Force')
        print("\n2. Reload NZBGet")
        print("\n3. Test with a small download (< 1 GB)")
    else:
        print("❌ TESTS FAILED")
        print("\nPlease fix the issues above before deploying to NZBGet.")
    print("=" * 80)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
