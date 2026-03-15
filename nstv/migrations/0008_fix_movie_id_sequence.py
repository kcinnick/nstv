"""
Data migration to fix the movie ID sequence issue

This migration resets the movie table's IDENTITY column to start
after the maximum existing ID, preventing duplicate key errors.
"""
from django.db import migrations
from django.db.models import Max


def fix_movie_sequence(apps, schema_editor):
    """Reset the movie table's IDENTITY sequence"""
    Movie = apps.get_model('nstv', 'Movie')
    
    # Get max movie ID
    max_id = Movie.objects.aggregate(Max('id'))['id__max']
    next_id = (max_id or 0) + 1
    
    # Reset the IDENTITY column
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE movie ALTER COLUMN id RESTART WITH {next_id};")
        print(f"\n✓ Reset movie table IDENTITY column to start at {next_id}\n")


def reverse_fix(apps, schema_editor):
    """Reverse operation (no-op for this case)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0007_merge_20260315_1621'),
    ]

    operations = [
        migrations.RunPython(fix_movie_sequence, reverse_fix),
    ]

