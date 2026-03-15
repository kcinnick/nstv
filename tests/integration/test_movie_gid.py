"""
Test the fixed get_gid_for_movie function
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.download import NZBGeek
from nstv.models import Movie

# Create or get test movie
movie_name = "2001 A Space Odyssey"
movie, created = Movie.objects.get_or_create(name=movie_name)
print(f"{'Created' if created else 'Found'} movie: {movie.name}")
print(f"Current GID: {movie.gid}\n")

# Test get_gid_for_movie
nzb = NZBGeek()
nzb.login()

print("=" * 80)
gid = nzb.get_gid_for_movie(movie)
print("=" * 80)

if gid:
    # Refresh from DB
    movie.refresh_from_db()
    print(f"\nSUCCESS! GID found and saved: {movie.gid}")
else:
    print(f"\nFAILED: No GID found for {movie_name}")
