# Generated by Django 4.2.5 on 2023-09-07 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0004_remove_episode_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='air_date',
            field=models.DateField(null=True),
        ),
    ]