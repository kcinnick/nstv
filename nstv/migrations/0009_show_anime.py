# Generated by Django 4.2.5 on 2023-09-20 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0008_rename_number_episode_episode_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='anime',
            field=models.BooleanField(default=False),
        ),
    ]
