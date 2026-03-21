"""
Migration to fix episode.season_number data type from TEXT to BIGINT

The old backup had season_number as TEXT, but the model defines it as IntegerField.
This causes type mismatch errors when querying.
"""
from django.db import migrations

def convert_season_number_to_int(apps, schema_editor):
    """Convert season_number from text to integer"""
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(
            "ALTER TABLE episode ALTER COLUMN season_number TYPE bigint USING season_number::bigint"
        )
        print("✓ Converted episode.season_number from TEXT to BIGINT")

def revert(apps, schema_editor):
    """Revert is not practical - data is already converted"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0008_fix_movie_id_sequence'),
    ]

    operations = [
        migrations.RunPython(convert_season_number_to_int, revert),
    ]

