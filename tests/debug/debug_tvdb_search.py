"""
Debug script to see what TVDB returns for problematic searches
"""
import os
from pprint import pprint
import tvdb_v4_official
from dotenv import load_dotenv

load_dotenv()

tvdb = tvdb_v4_official.TVDB(os.getenv('TVDB_API_KEY'))

# Test the problematic searches
test_searches = [
    "Shoujiki Fudousan",
    "The Honest Realtor",
]

for search_term in test_searches:
    print(f"\n{'='*80}")
    print(f"Searching for: {search_term}")
    print(f"{'='*80}")
    
    results = tvdb.search(query=search_term, type='series', language='eng')
    print(f"\nFound {len(results)} results:\n")
    
    for idx, result in enumerate(results[:3]):  # Show first 3 results
        print(f"\nResult #{idx + 1}:")
        print(f"  ID: {result.get('id')}")
        print(f"  Name: {result.get('name')}")
        print(f"  Translations: {result.get('translations')}")
        print(f"  Aliases: {result.get('aliases')}")
        print(f"  Primary Language: {result.get('primary_language')}")
