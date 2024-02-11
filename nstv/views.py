import os
import shutil

import plexapi.exceptions
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from tqdm import tqdm

from .download import NZBGeek
from .forms import DownloadForm, AddShowForm, AddMovieForm
from .models import Show, Episode, Movie, CastMember
from .tables import ShowTable, EpisodeTable, MovieTable

SHOW_ALIASES = {
    # plex title: django title
    '6ixtynin9 the Series': '6ixtynin9',
    'Jeopardy!': 'Jeopardy',
}

NZBGET_COMPLETE_DIR = os.getenv("NZBGET_COMPLETE_DIR")
PLEX_TV_SHOW_DIR = os.getenv("PLEX_TV_SHOW_DIR")
PLEX_MOVIES_DIR = os.getenv("PLEX_MOVIES_DIR")


def index(request):
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
            search_results = nzb_geek.get_nzb_search_results(
                show,
                season_number=season_number,
                episode_number=episode_number
            )
            nzb_geek.download_from_results(search_results, request)
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
        nzb_geek.download_from_results(nzb_search_results, request)
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
        if Movie.objects.filter(name=movie.name).exists():
            print(f"Movie {movie.name} already exists.")  # TODO: find a way to flash these as messages on the page
            if movie.gid is not None:
                pass
            else:
                nzb_geek = NZBGeek()
                nzb_geek.login()
                nzb_geek.get_gid_for_movie(movie)
            return HttpResponseRedirect(reverse('movies_index'))  # TODO: in the future, should redirect to movie's page
        else:
            print(
                f"Movie {movie.name} did not previously exist. Movie created."
            )  # TODO: find a way to flash these as messages on the page
            movie.save()
            nzb_geek = NZBGeek()
            nzb_geek.login()
            nzb_geek.get_gid_for_movie(movie)
            return HttpResponseRedirect(reverse('movies_index'))

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


def move_downloaded_files_to_plex(request, plex_dir):
    print(f'move_downloaded_files_to_{plex_dir.split("_")[-1]}')
    try:
        print(f'NZBGET_COMPLETE_DIR: {NZBGET_COMPLETE_DIR}')
        for file_name in tqdm(os.listdir(NZBGET_COMPLETE_DIR)):
            print('Moving file: ', file_name)
            file_path = os.path.join(NZBGET_COMPLETE_DIR, file_name)
            shutil.move(file_path, os.path.join(plex_dir, file_name))
        return JsonResponse({'status': 'success'}, status=200)
    except FileNotFoundError as e:
        print(e)
        return JsonResponse({'status': 'Network path was not found. Is your external HD turned on?'}, status=500)
    except Exception as e:
        print('failure: {}'.format(type(e)))
        return JsonResponse({'status': str(e)}, status=500)


def move_downloaded_tv_show_files_to_plex(request):
    json_response = move_downloaded_files_to_plex(request, PLEX_TV_SHOW_DIR)
    print(json_response)
    try:
        from .plexController.add_episodes_to_show import main as add_episodes_to_show
        add_episodes_to_show()
    except plexapi.exceptions.NotFound:
        return JsonResponse({'status': 'Network path was not found. Is your external HD turned on?'}, status=500)
    return redirect(request.META.get('HTTP_REFERER'))


def move_downloaded_movie_files_to_plex(request):
    json_response = move_downloaded_files_to_plex(request, PLEX_MOVIES_DIR)
    return json_response


def movies_index(request):
    print('movies_index')
    movies = Movie.objects.all()
    movies_table = MovieTable(movies)
    movies_table.exclude = ("poster_path",)
    index_context = {"title": "Movie Index", "movies": movies_table}
    return render(request, "movies_index.html", index_context)


def delete_movie(request, movie_id):
    print('delete_movie')
    if request.method == "POST":
        movie = Movie.objects.get(id=movie_id)
        movie.delete()
        print(f"Movie {movie.name} was deleted.")
    else:
        print('delete_movie: request.method != "POST"')
        raise Exception('delete_movie: request.method != "POST"')

    return HttpResponseRedirect(reverse('movies_index'))


def download_movie(request, movie_id):
    print('download_movie')
    nzb_geek = NZBGeek()
    nzb_geek.login()
    movie = Movie.objects.get(id=movie_id)
    print('movie name: {} ~'.format(movie.name))
    search_results = nzb_geek.get_nzb_search_results_for_movie(movie)
    nzb_geek.download_from_results(search_results, request)

    return HttpResponseRedirect(reverse('movies_index'))


def movie_index(request, movie_id):
    print('movie_index')
    movie = Movie.objects.filter(id=movie_id).first()
    index_context = {"title": "Movie", "movie": movie}

    return render(request, "movie.html", index_context)


def cast_member(request, cast_member_id):
    cast_member_object = CastMember.objects.get(id=cast_member_id)
    shows_for_cast_member = Show.objects.filter(cast__id=cast_member_id)
    movies_for_cast_member = Movie.objects.filter(cast__id=cast_member_id)
    index_context = {
        "title": "Cast Member",
        "shows": shows_for_cast_member,
        "movies": movies_for_cast_member,
        "cast_member": cast_member_object,
    }
    return render(request, "cast_member.html", index_context)


def search_results(request):
    query = request.GET.get('query', '')
    search_movies = request.GET.get('movies') == 'on'
    search_shows = request.GET.get('shows') == 'on'
    search_cast = request.GET.get('cast_members') == 'on'
    search_episodes = request.GET.get('episodes') == 'on'

    results = {}

    print('query is ' + query)
    if query:
        print('query is not empty')
        if search_movies:
            print('searching movies')
            results['movies'] = Movie.objects.filter(name__icontains=query)
        if search_shows:
            print('searching shows')
            results['shows'] = Show.objects.filter(title__icontains=query)
        if search_cast:
            print('searching cast')
            results['cast_members'] = CastMember.objects.filter(name__icontains=query)
        if search_episodes:
            print('searching episodes')
            results['episodes'] = Episode.objects.filter(title__icontains=query)
    else:
        print('query is empty')

    return render(request, 'search.html', {'results': results})
