# Generated by Django 4.2.5 on 2023-09-24 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0012_remove_movie_release_date_movie_release_year_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='release_date',
            field=models.DateField(default=None, null=True),
        ),
    ]