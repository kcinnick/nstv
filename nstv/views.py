import os

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import DownloadForm, AddShowForm
from .models import Show, Episode
from .tables import ShowTable, EpisodeTable

SHOW_ALIASES = {
    # plex title: django title
    '6ixtynin9 the Series': '6ixtynin9'
}

def index(request):
    from nstv.download import NZBGeek

    nzb_geek = NZBGeek()
    nzb_geek.login()
    form = DownloadForm(request.POST or None)
    index_context = {"title": "Dashboard", "download_form": form}

    if request.method == "POST":
        if form.is_valid():
            season_number = form.cleaned_data["season_number"]
            episode_number = form.cleaned_data["episode_number"]
            show_title_int = int(form.cleaned_data.get("show_title"))
            show_title = dict(form.fields["show_title"].choices)
            show_title = show_title[show_title_int]
            try:
                show = Show.objects.get(title=show_title)
            except Show.DoesNotExist:
                return redirect("add_show_page")
            print(f"Downloading {show.title} S{season_number} E{episode_number}..")
            try:
                nzb_geek.get_nzb(show, season_number=season_number, episode_number=episode_number)
            except AttributeError:
                print("No download link found. Returning to index.")
        else:
            index_context["form_errors"] = form.errors
            return render(request, "index.html", index_context)

    return render(request, "index.html", index_context)


def shows_index(request):
    print('shows_index')
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
    episodes_table = EpisodeTable(show.episodes, order_by="id")
    episodes_table.paginate(page=request.GET.get("page", 1), per_page=10)

    index_context = {"title": "Show", "show": show, "episodes": episodes_table}

    return render(
        request,
        f"show.html",
        index_context,
    )


def download_episode(request, show_id, episode_id):
    print('download_episode')
    # print(eid, sid)

    from nstv.download import NZBGeek
    nzb_geek = NZBGeek()
    nzb_geek.login()
    episode = Episode.objects.get(id=episode_id)
    parent_show = Show.objects.get(id=show_id)
    print('episode title: {} ~'.format(episode.title))
    if episode.title:
        nzb_geek.get_nzb(
            show=parent_show, episode_title=episode.title,
            season_number=episode.season_number, episode_number=episode.episode_number
        )
    else:
        print(
            'Searching shows by season or episode number '
            'isn\'t currently supported.\n')
        raise NotImplementedError

    return redirect(request.META.get('HTTP_REFERER'))


def add_show_page(request):
    form = AddShowForm(request.POST or None)
    index_context = {"title": "Add Show", "add_show_form": form}

    if request.method == "POST" and form.is_valid():
        show = Show(**form.cleaned_data)
        if Show.objects.filter(title=show.title).exists():
            print(f"Show {show.title} already exists.")  # TODO: find a way to flash these as messages on the page
            return HttpResponseRedirect(reverse('shows_index'))  # TODO: in the future, should redirect to show's page
        else:
            print(
                f"Show {show.title} did not previously exist. Show was created."
            )  # TODO: find a way to flash these as messages on the page
            show.save()

    index_context["form_errors"] = form.errors

    if form.errors:
        raise Exception(form.errors)
        return HttpResponseRedirect(reverse('shows_index'))

    return render(request, "add_show.html", index_context)


def delete_show(request, show_id):
    print('delete_show')
    if request.method == "POST":
        print(show_id)
        show = Show.objects.get(id=show_id)
        show.delete()
        print(f"Show {show.title} was deleted.")
    else:
        print('delete_show: request.method != "POST"')
        raise Exception('delete_show: request.method != "POST"')

    return HttpResponseRedirect(reverse('shows_index'))