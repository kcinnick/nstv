"""
Test script to verify duplicate detection finds Plex's native duplicate media files.
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.plexController.find_duplicates import DuplicateFinder

print("Testing Duplicate Detection")
print("=" * 80)

try:
    finder = DuplicateFinder()
    print("[OK] Connected to Plex server")
    print()
    
    # Test TV Shows
    print("Scanning TV Shows for duplicates...")
    print("-" * 80)
    duplicate_episodes = finder.find_duplicate_episodes()
    
    if duplicate_episodes:
        print(f"\n[OK] Found {len(duplicate_episodes)} duplicate episode groups:")
        for group in duplicate_episodes[:5]:  # Show first 5
            space_savings_gb = round(group.total_space_savings() / (1024**3), 2)
            print(f"\n  {group.show_title} - S{group.season_number:02d}E{group.episode_number:02d}: {group.title}")
            print(f"  {len(group.items)} versions, {space_savings_gb} GB savings")
            for item in group.items:
                status = "KEEP" if item.is_recommended_keep else "DELETE"
                print(f"    [{status}] Quality: {item.quality_score.total_score:.1f} - {item.file_path[:80]}...")
    else:
        print("\n[NONE] No duplicate episodes found")
    
    print()
    
    # Test Movies
    print("Scanning Movies for duplicates...")
    print("-" * 80)
    duplicate_movies = finder.find_duplicate_movies()
    
    if duplicate_movies:
        print(f"\n[OK] Found {len(duplicate_movies)} duplicate movie groups:")
        for group in duplicate_movies[:5]:  # Show first 5
            space_savings_gb = round(group.total_space_savings() / (1024**3), 2)
            print(f"\n  {group.title} ({group.year})")
            print(f"  {len(group.items)} versions, {space_savings_gb} GB savings")
            for item in group.items:
                status = "KEEP" if item.is_recommended_keep else "DELETE"
                print(f"    [{status}] Quality: {item.quality_score.total_score:.1f} - {item.file_path[:80]}...")
    else:
        print("\n[NONE] No duplicate movies found")
    
    print()
    print("=" * 80)
    print("Test complete!")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
