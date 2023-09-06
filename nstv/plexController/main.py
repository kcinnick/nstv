from plexapi.myplex import MyPlexAccount
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from django.shortcuts import render, redirect
from nstv.models import Show, Episode
from nstv.forms import DownloadForm, AddShowForm

account = MyPlexAccount('nicktucker4@gmail.com', os.getenv('PLEX_API_KEY'))
plex = account.resource(os.getenv('PLEX_SERVER')).connect()  # returns a PlexServer instance

plexTvShows = plex.library.section('TV Shows')
for show in plexTvShows.search():
    print(show.title)
    showObject = Show.objects.all().filter(title=show.title)
    if showObject:
        print('show already exists')
    else:
        print('show does not exist')
        showObject = Show(title=show.title)
        showObject.save()
        print('show added to database')