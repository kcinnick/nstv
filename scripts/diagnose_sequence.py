#!/usr/bin/env python
"""Diagnose and fix the duplicate movie ID sequence issue."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.models import Movie
from django.db import connection

print("=" * 60)
print("MOVIE ID SEQUENCE DIAGNOSIS")
print("=" * 60)

# Check if movie with ID 113 exists
try:
    movie_113 = Movie.objects.get(id=113)
    print(f"\n✓ Movie ID 113 EXISTS: {movie_113.title}")
except Movie.DoesNotExist:
    print("\n✗ Movie ID 113 does NOT exist in database")

# Get max movie ID
max_id = Movie.objects.all().aggregate(max_id=__import__('django.db.models', fromlist=['Max']).Max('id'))['max_id']
print(f"✓ Max movie ID in database: {max_id}")

# Check the sequence value
with connection.cursor() as cursor:
    cursor.execute("SELECT nextval('nstv_movie_id_seq'::regclass);")
    next_val = cursor.fetchone()[0]
    print(f"✓ Current sequence next value: {next_val}")

# Count movies
count = Movie.objects.count()
print(f"✓ Total movies in database: {count}")

# Show last 5 movies
print("\nLast 5 movies in database:")
for m in Movie.objects.all().order_by('-id')[:5]:
    print(f"  ID {m.id}: {m.title}")

# Check if sequence is out of sync
print("\n" + "=" * 60)
if max_id is not None and next_val <= max_id:
    print(f"⚠️  PROBLEM FOUND:")
    print(f"   Sequence next value ({next_val}) <= Max ID ({max_id})")
    print(f"   This will cause duplicate key errors!")
    print(f"\n   Fix: Reset sequence to {max_id + 1}")
else:
    print("✓ Sequence is OK (next value > max ID)")

print("=" * 60)

