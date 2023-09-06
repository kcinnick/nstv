import os

from django.shortcuts import render, redirect
from .forms import DownloadForm, AddShowForm
from .models import Show, Episode
from .tables import ShowTable


def index(request):
    print('index')
    from nstv.download import NZBGeek

    nzb_geek = NZBGeek()
    nzb_geek.login()
    if request.method == "POST":
        form = DownloadForm(request.POST)
        if form.is_valid():
            season_number = form.cleaned_data.get("season_number")
            episode_number = form.cleaned_data.get("episode_number")
            #  TODO:  clean up 22-25
            show_title_int = int(form.cleaned_data.get("show_title"))
            show_title = dict(form.fields["show_title"].choices)
            show_title = show_title[show_title_int]
            try:
                show = Show.objects.get(title=show_title)
            except Show.DoesNotExist:
                print(f"Show {show_title} not found.  Adding to database.")
                return redirect("/add_show")
            print(f"Downloading {show.title} S{season_number} E{episode_number}..")
            try:
                nzb_geek.get_nzb(
                    show, season_number=season_number, episode_number=episode_number
                )
            except AttributeError:
                #  no download link found
                print("No download link found.  Returning to index.")

    index_context = {"title": "Dashboard", "download_form": DownloadForm()}

    return render(
        request,
        f"index.html",
        index_context,
    )


def shows_index(request):
    print('shows_index')
    print(Show.objects.all())
    show_table = ShowTable(Show.objects.all().order_by("id"))
    show_table.paginate(page=request.GET.get("page", 1), per_page=10)

    index_context = {"title": "Show Index", "shows": show_table}

    return render(
        request,
        f"shows_index.html",
        index_context,
    )


def show_index(request, show_id):
    print('show_index')
    show = Show.objects.filter(id=show_id).first()
    episodes = Episode.objects.filter(show=show)
    index_context = {"title": "Show", "show": show, "episodes": episodes}

    return render(
        request,
        f"show.html",
        index_context,
    )


def download_episode(request, sid, eid):
    print('download_episode')
    print(eid, sid)

    from nstv.download import NZBGeek
    nzb_geek = NZBGeek()
    nzb_geek.login()
    episode = Episode.objects.get(id=eid)
    parent_show = Show.objects.get(id=sid)
    print('episode title: {} ~'.format(episode.title))
    if episode.title:
        nzb_geek.get_nzb(
            show=parent_show, episode_title=episode.title
        )
    else:
        print(
            'Searching shows by season or episode number '
            'isn\'t currently supported.\n')
        raise NotImplementedError

    return redirect(parent_show)


def add_show_page(request):
    form = AddShowForm(request.POST or None)
    index_context = {"title": "Add Show", "add_show_form": form}

    if request.method == "POST":
        if form.is_valid():
            show = Show(**form.cleaned_data)
            show.save()
            return redirect('shows_index')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        return render(
            request,
            'add_show.html',
            index_context,
        )