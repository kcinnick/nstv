# Generated by Django 4.2.5 on 2023-09-07 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nstv', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]