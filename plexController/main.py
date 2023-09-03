from plexapi.myplex import MyPlexAccount
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nstv_fe.nstv_fe.settings')
django.setup()
from django.shortcuts import render, redirect
from nstv_fe.nstv_fe.forms import DownloadForm, AddShowForm
from nstv_fe.nstv_fe.models import Show, Episode
from nstv_fe.nstv_fe.tables import ShowTable

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