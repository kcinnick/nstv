"""
Test the improved TVDB matching logic
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

import tvdb_v4_official
from nstv.get_info_from_tvdb.main import find_tvdb_record_for_series
from nstv.models import Show

# Create a test show if it doesn't exist
test_title = "Shoujiki Fudousan"
show, created = Show.objects.get_or_create(title=test_title)
print(f"{'Created' if created else 'Found'} show: {show.title}")

# Test the matching function
tvdb = tvdb_v4_official.TVDB(os.getenv('TVDB_API_KEY'))

try:
    result = find_tvdb_record_for_series(tvdb, test_title)
    print(f"\n✓ SUCCESS! Found TVDB record:")
    print(f"  ID: {result.get('id')}")
    print(f"  Name: {result.get('name')}")
    print(f"  English: {result.get('translations', {}).get('eng')}")
    
    # Verify the show was updated
    show.refresh_from_db()
    print(f"\n✓ Show.tvdb_id updated to: {show.tvdb_id}")
    
except Exception as e:
    print(f"\n✗ FAILED: {str(e)}")
