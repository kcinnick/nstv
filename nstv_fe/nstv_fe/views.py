from django.shortcuts import render
from .models import Show
import os


def index(request):
    index_context = {
        "title": "Dashboard",
    }
    from nstv.download import NZBGeek
    nzb_geek = NZBGeek()
    nzb_geek.login()
    show = Show(title='Chopped', gid='85019')
    season_number = request.GET.get('season_number')
    episode_number = request.GET.get('episode_number')
    nzb_geek.get_nzb(show, season_number=season_number, episode_number=episode_number)
    return render(request, '/home/nick/PycharmProjects/nstv/nstv_fe/templates/index.html', index_context)
