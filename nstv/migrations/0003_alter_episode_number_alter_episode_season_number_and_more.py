# Generated by Django 4.2.5 on 2023-09-07 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0002_alter_episode_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='number',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='season_number',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='slug',
            field=models.TextField(null=True),
        ),
    ]
