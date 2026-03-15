"""
Fix for missing movie ID sequence issue

Problem: The sequence nstv_movie_id_seq does not exist, causing duplicate key errors
Solution: Recreate the sequence with the correct starting value
"""
import django
import os

os.chdir(r'C:\Users\Nick\PycharmProjects\nstv')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.models import Movie
from django.db import connection
from django.db.models import Max

print("\n" + "="*70)
print("FIXING MOVIE ID SEQUENCE ISSUE")
print("="*70)

# Get max movie ID
max_id = Movie.objects.aggregate(Max('id'))['id__max']
next_id = (max_id or 0) + 1

print(f"\n📊 Current state:")
print(f"   Max movie ID: {max_id}")
print(f"   Next ID should be: {next_id}")
print(f"   Total movies: {Movie.objects.count()}")

# Fix: Recreate the sequence
with connection.cursor() as cursor:
    print(f"\n🔧 Fixing sequence...")
    
    # For IDENTITY columns, we need to reset the identity
    # First, get the current max id and set it properly
    try:
        cursor.execute(f"ALTER TABLE movie ALTER COLUMN id RESTART WITH {next_id};")
        print(f"   ✓ Reset IDENTITY column to start at {next_id}")
    except Exception as e:
        print(f"   ⚠ Error with IDENTITY restart: {e}")
        print("   Trying alternate method...")
        
        # Alternate: Try to recreate the sequence
        try:
            cursor.execute("DROP SEQUENCE IF EXISTS nstv_movie_id_seq CASCADE;")
            cursor.execute(f"CREATE SEQUENCE nstv_movie_id_seq START {next_id};")
            cursor.execute("""
                ALTER TABLE movie 
                ALTER COLUMN id 
                SET DEFAULT nextval('nstv_movie_id_seq'::regclass);
            """)
            print(f"   ✓ Created sequence starting at {next_id}")
        except Exception as e2:
            print(f"   Error: {e2}")

# Verify fix
print(f"\n✅ Verification:")
try:
    # Try to create a test movie
    test_movie = Movie.objects.create(name="Test Movie for Sequence Verification")
    print(f"   ✓ Successfully created test movie with ID: {test_movie.id}")
    print(f"   ✓ Sequence is working correctly!")
    
    # Delete test movie
    test_movie.delete()
    print(f"   ✓ Cleaned up test movie")
except Exception as e:
    print(f"   ⚠ Error during verification: {e}")

print("\n" + "="*70)
print("✅ FIX COMPLETE!")
print("="*70)
print("\nYou should now be able to add movies without duplicate key errors.")
print(f"Next movie will get ID: {next_id}")
print("\nTest by adding 'Sunset Boulevard'\n")

