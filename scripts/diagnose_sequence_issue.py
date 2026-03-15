#!/usr/bin/env python
"""Diagnose movie ID sequence issue"""
import django
import os

os.chdir(r'C:\Users\Nick\PycharmProjects\nstv')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.models import Movie
from django.db import connection
from django.db.models import Max

print("\n" + "="*60)
print("MOVIE ID SEQUENCE DIAGNOSIS")
print("="*60)

# Check if movie with ID 113 exists
try:
    movie_113 = Movie.objects.get(id=113)
    print(f"\n✓ Movie ID 113 EXISTS: {movie_113.name}")
except Movie.DoesNotExist:
    print("\n✗ Movie ID 113 does NOT exist in database")

# Get max movie ID
max_id = Movie.objects.aggregate(Max('id'))['id__max']
print(f"✓ Max movie ID in database: {max_id}")

# Count movies
count = Movie.objects.count()
print(f"✓ Total movies: {count}")

# Show last 5 movies
print("\nLast 5 movies in database:")
for m in Movie.objects.all().order_by('-id')[:5]:
    print(f"  ID {m.id}: {m.name}")

print("\n" + "="*60)
if max_id is not None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval('nstv_movie_id_seq'::regclass);")
        next_val = cursor.fetchone()[0]
        print(f"Current sequence next value: {next_val}")
        
        if next_val <= max_id:
            print(f"\n⚠️  PROBLEM FOUND!")
            print(f"   Sequence next value ({next_val}) <= Max ID ({max_id})")
            print(f"   This causes duplicate key errors!")
            print(f"\n   Solution: Need to reset sequence to {max_id + 1}")
        else:
            print(f"\n✓ Sequence is OK (next value {next_val} > max ID {max_id})")
print("="*60)

