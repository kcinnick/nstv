# Generated by Django 4.2.5 on 2023-09-27 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0012_remove_movie_release_date_movie_release_year_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='gid',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
