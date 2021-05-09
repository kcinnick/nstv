from django.shortcuts import render
from .forms import DownloadForm
from .models import Show


def index(request):
    index_context = {
        "title": "Dashboard",
        "download_form": DownloadForm()
    }
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
                nzb_geek.get_nzb(show, season_number=season_number, episode_number=episode_number)
            except AttributeError:
                #  no download link found
                print('No download link found.  Returning to index.')

    return render(request, '/home/nick/PycharmProjects/nstv/nstv_fe/templates/index.html', index_context)
