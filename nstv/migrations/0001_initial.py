# Generated by Django 5.0.2 on 2024-03-12 22:54

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CastMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('role', models.TextField()),
                ('image_url', models.TextField(null=True)),
            ],
            options={
                'db_table': 'cast_member',
            },
        ),
        migrations.CreateModel(
            name='NZBDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nzb_id', models.TextField(default=None, null=True)),
                ('site', models.TextField(default=None, null=True)),
                ('title', models.TextField(default=None, null=True)),
                ('url', models.TextField(default=None, null=True)),
                ('status', models.TextField(default=None, null=True)),
            ],
            options={
                'db_table': 'nzb_download',
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gid', models.IntegerField(default=None, null=True)),
                ('name', models.TextField()),
                ('release_date', models.DateField(default=None, null=True)),
                ('genre', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=200), default=list, size=None)),
                ('director', models.TextField()),
                ('on_disk', models.BooleanField(default=False)),
                ('poster_path', models.TextField(default=None, null=True)),
                ('cast', models.ManyToManyField(related_name='movies', to='nstv.castmember')),
            ],
            options={
                'db_table': 'movie',
            },
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gid', models.IntegerField(default=None, null=True)),
                ('title', models.TextField()),
                ('anime', models.BooleanField(default=False)),
                ('tvdb_id', models.TextField(default=None, null=True)),
                ('cast', models.ManyToManyField(related_name='shows', to='nstv.castmember')),
            ],
            options={
                'db_table': 'show',
            },
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('air_date', models.DateField(null=True)),
                ('title', models.TextField()),
                ('season_number', models.IntegerField(null=True)),
                ('episode_number', models.IntegerField(null=True)),
                ('on_disk', models.BooleanField(default=False)),
                ('tvdb_id', models.IntegerField(default=None, null=True)),
                ('cast', models.ManyToManyField(related_name='episodes', to='nstv.castmember')),
                ('show', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='nstv.show')),
            ],
            options={
                'db_table': 'episode',
            },
        ),
    ]
