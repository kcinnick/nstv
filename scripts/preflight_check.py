"""
Pre-flight check script for NZBGet automation.
Validates all requirements before enabling automation.
"""
import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
import django
django.setup()

from django.core.management import call_command
from plexapi.myplex import MyPlexAccount

def check_section(title):
    """Print section header"""
    print(f'\n{"=" * 80}')
    print(f'{title}')
    print("=" * 80)

def check_env_var(name, required=True):
    """Check if environment variable exists"""
    value = os.getenv(name)
    if value:
        # Mask sensitive values
        if 'PASSWORD' in name or 'KEY' in name or 'API' in name:
            display = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
        else:
            display = value
        print(f'  ✓ {name} = {display}')
        return True
    else:
        status = '✗ REQUIRED' if required else '⚠ OPTIONAL'
        print(f'  {status}: {name} not set')
        return not required

def check_path(name, path_var):
    """Check if path exists"""
    path = os.getenv(path_var)
    if not path:
        print(f'  ✗ {name}: Environment variable {path_var} not set')
        return False
    
    if os.path.exists(path):
        print(f'  ✓ {name}: {path}')
        return True
    else:
        print(f'  ✗ {name}: Path does not exist: {path}')
        return False

def check_plex_connection():
    """Test Plex server connectivity"""
    email = os.getenv('PLEX_EMAIL')
    api_key = os.getenv('PLEX_API_KEY')
    server_name = os.getenv('PLEX_SERVER')
    
    if not all([email, api_key, server_name]):
        print('  ✗ Missing Plex credentials')
        return False
    
    try:
        account = MyPlexAccount(email, api_key)
        plex = account.resource(server_name).connect()
        sections = plex.library.sections()
        print(f'  ✓ Connected to Plex server: {server_name}')
        print(f'  ✓ Found {len(sections)} library sections')
        return True
    except Exception as e:
        print(f'  ✗ Plex connection failed: {e}')
        return False

def check_python_executable():
    """Verify Python executable paths"""
    venv_python = project_root / '.venv' / 'Scripts' / 'python.exe'
    if venv_python.exists():
        print(f'  ✓ Virtual environment Python: {venv_python}')
        return True
    else:
        print(f'  ✗ Virtual environment Python not found: {venv_python}')
        return False

def check_nzbget_script():
    """Check if NZBGet script is properly installed"""
    script_source = project_root / 'scripts' / 'nzbget_postprocess.py'
    script_dest = Path('C:/ProgramData/NZBGet/scripts/nzbget_postprocess.py')
    
    if not script_source.exists():
        print(f'  ✗ Source script not found: {script_source}')
        return False
    
    print(f'  ✓ Source script exists: {script_source}')
    
    if script_dest.exists():
        # Check if disabled
        if script_dest.name.endswith('.disabled'):
            print(f'  ⚠ Script is DISABLED: {script_dest}')
            return False
        else:
            print(f'  ✓ Script installed: {script_dest}')
            
            # Compare modification times
            source_mtime = script_source.stat().st_mtime
            dest_mtime = script_dest.stat().st_mtime
            
            if source_mtime > dest_mtime:
                print(f'  ⚠ Source script is newer than installed version')
                print(f'    Run: Copy-Item "{script_source}" "{script_dest}" -Force')
                return True  # Not critical, but warn
            return True
    else:
        # Check for disabled version
        disabled_path = Path(str(script_dest) + '.disabled')
        if disabled_path.exists():
            print(f'  ⚠ Script exists but is DISABLED: {disabled_path}')
            print(f'    To enable: Rename-Item "{disabled_path}" "{script_dest}"')
            return False
        else:
            print(f'  ✗ Script not installed at: {script_dest}')
            print(f'    Run: Copy-Item "{script_source}" "{script_dest}"')
            return False

def test_process_downloads_command():
    """Test the Django management command"""
    try:
        print('  Testing process_downloads command (dry-run)...')
        # Redirect output to capture
        from io import StringIO
        output = StringIO()
        call_command('process_downloads', '--dry-run', stdout=output, stderr=output)
        result = output.getvalue()
        
        if 'Plex server' in result and 'accessible' in result:
            print('  ✓ Command executes successfully')
            return True
        else:
            print('  ⚠ Command executed but output unexpected')
            print(f'    Output preview: {result[:200]}...')
            return True  # Not critical
    except Exception as e:
        print(f'  ✗ Command failed: {e}')
        return False

def main():
    """Run all pre-flight checks"""
    print('\n' + '=' * 80)
    print('NZBGet Automation Pre-Flight Check')
    print('=' * 80)
    
    all_passed = True
    
    # Check environment variables
    check_section('1. Environment Variables')
    all_passed &= check_env_var('NZBGET_COMPLETE_DIR')
    all_passed &= check_env_var('PLEX_TV_SHOW_DIR')
    all_passed &= check_env_var('PLEX_MOVIES_DIR', required=False)
    all_passed &= check_env_var('PLEX_EMAIL')
    all_passed &= check_env_var('PLEX_API_KEY')
    all_passed &= check_env_var('PLEX_SERVER')
    
    # Check paths
    check_section('2. Directory Paths')
    all_passed &= check_path('NZBGet Complete Directory', 'NZBGET_COMPLETE_DIR')
    all_passed &= check_path('Plex TV Show Directory', 'PLEX_TV_SHOW_DIR')
    check_path('Plex Movies Directory', 'PLEX_MOVIES_DIR')  # Optional
    
    # Check Plex connection
    check_section('3. Plex Server Connection')
    all_passed &= check_plex_connection()
    
    # Check Python
    check_section('4. Python Environment')
    all_passed &= check_python_executable()
    
    # Check NZBGet script
    check_section('5. NZBGet Script Installation')
    script_ok = check_nzbget_script()
    
    # Test command
    check_section('6. Django Management Command')
    all_passed &= test_process_downloads_command()
    
    # Summary
    check_section('Pre-Flight Check Summary')
    if all_passed and script_ok:
        print('  ✅ ALL CHECKS PASSED')
        print('\n  Ready to enable NZBGet automation!')
        print('\n  Next steps:')
        if not script_ok:
            print('  1. Install or enable the NZBGet script (see section 5 above)')
        print('  2. Configure script in NZBGet Settings > Extension Scripts')
        print('  3. Set PYTHON_PATH to (leave blank or set):')
        print('     C:\\Users\\Nick\\nstv\\.venv\\Scripts\\python.exe')
        print('  4. Reload NZBGet')
        print('  5. Test with a small download')
    else:
        print('  ❌ SOME CHECKS FAILED')
        print('\n  Please fix the issues marked with ✗ above before enabling automation.')
        if not all_passed:
            print('\n  Critical issues must be resolved.')
        if not script_ok:
            print('  NZBGet script installation/enablement required.')
    
    print('\n' + '=' * 80)
    
    return all_passed and script_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
