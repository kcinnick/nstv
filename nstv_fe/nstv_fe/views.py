from django.shortcuts import render
from .forms import DownloadForm
from .models import Show, Episode
from .tables import ShowTable


def index(request):
    from nstv.download import NZBGeek
    nzb_geek = NZBGeek()
    nzb_geek.login()
    if request.method == 'POST':
        form = DownloadForm(request.POST)
        if form.is_valid():
            season_number = form.cleaned_data.get('season_number')
            episode_number = form.cleaned_data.get('episode_number')
            #  TODO:  clean up 22-25. seems very convoluted for what
            #  TODO:  is simply taking the title of the show from the
            #  TODO:  form and passing it to the ORM query..
            show_title_int = int(form.cleaned_data.get('show_title'))
            show_title = dict(form.fields['show_title'].choices)
            show_title = show_title[show_title_int]
            show = Show.objects.get(title=show_title)

            print(f"Downloading {show.title} S{season_number} E{episode_number}..")
            try:
                nzb_geek.get_nzb(
                    show, season_number=season_number, episode_number=episode_number)
            except AttributeError:
                #  no download link found
                print('No download link found.  Returning to index.')

    index_context = {
        "title": "Dashboard",
        "download_form": DownloadForm()
    }

    return render(request, '/home/nick/PycharmProjects/nstv/nstv_fe/templates/index.html', index_context)


def shows_index(request):
    show_table = ShowTable(
        Show.objects.all().order_by('id')
    )
    show_table.paginate(page=request.GET.get("page", 1), per_page=10)

    index_context = {
        "title": "Show Index",
        "shows": show_table
    }

    return render(request, '/home/nick/PycharmProjects/nstv/nstv_fe/templates/shows_index.html', index_context)


def show(request, sid):
    show_ = Show.objects.filter(id=sid).first()
    episodes = Episode.objects.filter(show=show_)
    index_context = {
        "title": "Show",
        "show": show_,
        "episodes": episodes
    }

    return render(request, '/home/nick/PycharmProjects/nstv/nstv_fe/templates/show.html', index_context)


def download_episode(request, sid, eid):
    print(eid, sid)

    from nstv.download import NZBGeek
    nzb_geek = NZBGeek()
    nzb_geek.login()
    episode = Episode.objects.get(id=eid)
    show_ = Show.objects.get(id=sid)
    print('episode title: {} ~'.format(episode.title))
    if episode.title:
        nzb_geek.get_nzb(
            show=show_, episode_title=episode.title
        )
    else:
        print(
            'Searching shows by season or episode number '
            'isn\'t currently supported.\n')
        raise NotImplementedError

    index_context = {
        "title": "Show",
        "show": show,
        "episodes": []
    }

    return render(request, '/home/nick/PycharmProjects/nstv/nstv_fe/templates/show.html', index_context)
