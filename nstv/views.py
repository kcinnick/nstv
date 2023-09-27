import os
import shutil

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import DownloadForm, AddShowForm, AddMovieForm
from .models import Show, Episode, Movie
from .tables import ShowTable, EpisodeTable, MovieTable

SHOW_ALIASES = {
    # plex title: django title
    '6ixtynin9 the Series': '6ixtynin9',
    'Jeopardy!': 'Jeopardy',
}

NZBGET_COMPLETE_DIR = os.getenv("NZBGET_COMPLETE_DIR")
PLEX_TV_SHOW_DIR = os.getenv("PLEX_TV_SHOW_DIR")


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
            show_title = show_title.get(show_title_int)
            show = Show.objects.get(title=show_title)
            print(f"Downloading {show.title} S{season_number} E{episode_number}..")
            search_results = nzb_geek.get_nzb_search_results(show, season_number=season_number,
                                                             episode_number=episode_number)
            nzb_geek.download_from_results(search_results)
        else:
            print(form.errors)
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
    episodes_table = EpisodeTable(show.episodes)
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
        nzb_search_results = nzb_geek.get_nzb_search_results(
            show=parent_show, episode_title=episode.title,
            season_number=episode.season_number, episode_number=episode.episode_number,
            anime=parent_show.anime
        )
        nzb_geek.download_from_results(nzb_search_results)
    else:
        print(
            'Searching shows by season or episode number '
            'isn\'t currently supported.\n')
        raise NotImplementedError

    return redirect(request.META.get('HTTP_REFERER', '/'))


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
            return HttpResponseRedirect(reverse('shows_index'))

    index_context["form_errors"] = form.errors

    if form.errors:
        raise Exception(form.errors)

    return render(request, "add_show.html", index_context)


def add_movie_page(request):
    form = AddMovieForm(request.POST or None)
    index_context = {"title": "Add Movie", "add_movie_form": form}

    if request.method == "POST" and form.is_valid():
        movie = Movie(**form.cleaned_data)
        if Movie.objects.filter(title=movie.title).exists():
            print(f"Movie {movie.title} already exists.")  # TODO: find a way to flash these as messages on the page
            return HttpResponseRedirect(reverse('movie_index'))  # TODO: in the future, should redirect to show's page
        else:
            print(
                f"Movie {movie.title} did not previously exist. Movie created."
            )  # TODO: find a way to flash these as messages on the page
            movie.save()
            return HttpResponseRedirect(reverse('movie_index'))

    index_context["form_errors"] = form.errors

    if form.errors:
        raise Exception(form.errors)

    return render(request, "add_movie.html", index_context)


def delete_show(request, show_id):
    print('delete_show')
    if request.method == "POST":
        show = Show.objects.get(id=show_id)
        show.delete()
        print(f"Show {show.title} was deleted.")
    else:
        print('delete_show: request.method != "POST"')
        raise Exception('delete_show: request.method != "POST"')

    return HttpResponseRedirect(reverse('shows_index'))


def delete_episode_of_show(request, show_id, episode_id):
    print('delete_episode_of_show')
    if request.method == "POST":
        show = Show.objects.get(id=show_id)
        for episode in show.episodes.all():
            if episode.id == episode_id:
                episode.delete()
                print(f"Episode {episode.title} was deleted.")
                break
    else:
        print('delete_episode_of_show: request.method != "POST"')
        raise Exception('delete_show: request.method != "POST"')

    return HttpResponseRedirect(reverse('show_index', args=(show_id,)))


def add_episodes_to_database(request, show_id):
    print('add_episodes_to_database')
    from nstv.get_info_from_tvdb.main import main
    main(show_id=show_id)
    return redirect(request.META.get('HTTP_REFERER'))


def move_downloaded_files_to_plex(request):
    print('move_downloaded_files_to_plex')
    # get all files in NZBGET_COMPLETE_DIR
    # and move them to the appropriate plex library
    for file_name in os.listdir(NZBGET_COMPLETE_DIR):
        file_path = os.path.join(NZBGET_COMPLETE_DIR, file_name)
        # move the file to the appropriate plex library
        print(f"Moving {file_path} to {PLEX_TV_SHOW_DIR}")
        # move the file from file_path to PLEX_TV_SHOW_DIR
        shutil.move(file_path, os.path.join(PLEX_TV_SHOW_DIR, file_name))

    from .plexController.add_episodes_to_show import main as add_episodes_to_show
    add_episodes_to_show()

    return redirect(request.META.get('HTTP_REFERER'))


def movie_index(request):
    print('movie_index')
    movies = Movie.objects.all()
    movies_table = MovieTable(movies)
    index_context = {"title": "Movie Index", "movies": movies_table}
    return render(request, "movie_index.html", index_context)


def delete_movie(request, movie_id):
    print('delete_movie')
    if request.method == "POST":
        movie = Movie.objects.get(id=movie_id)
        movie.delete()
        print(f"Movie {movie.title} was deleted.")
    else:
        print('delete_movie: request.method != "POST"')
        raise Exception('delete_movie: request.method != "POST"')

    return HttpResponseRedirect(reverse('movie_index'))


def download_movie(request, movie_id):
    print('download_movie')
    from nstv.download import NZBGeek
    nzb_geek = NZBGeek()
    nzb_geek.login()
    movie = Movie.objects.get(id=movie_id)
    print('movie title: {} ~'.format(movie.title))

    return HttpResponseRedirect(reverse('movie_index'))

