import os
import shutil
import threading

import plexapi.exceptions
from django.contrib import messages
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
                episode_number=episode_number,
                hd=False
            )
            # Start download in background thread
            download_thread = threading.Thread(
                target=nzb_geek.download_from_results,
                args=(search_results, request),
                daemon=True
            )
            download_thread.start()
            messages.info(request, f"Download started for {show.title} S{season_number}E{episode_number}. Check console for progress.")
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
            anime=parent_show.anime, hd=False
        )
        # Start download in background thread
        download_thread = threading.Thread(
            target=nzb_geek.download_from_results,
            args=(nzb_search_results, request),
            daemon=True
        )
        download_thread.start()
        messages.info(request, f"Download started for {parent_show.title} S{episode.season_number}E{episode.episode_number} - {episode.title}. Check console for progress.")
    else:
        print(
            'Searching shows by season or episode number '
            'isn\'t currently supported.\n')
        messages.error(request, "Episode title is required for download.")
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
    """
    Move completed downloads from NZBGet to Plex media directories.
    
    @param request: Django request object
    @param plex_dir: Target Plex directory path
    @return: JsonResponse with status and details
    """
    dir_type = plex_dir.split("\\")[-1]  # Get last part of path (TV Shows or Movies)
    print(f'move_downloaded_files_to_{dir_type}')
    print(f'NZBGET_COMPLETE_DIR: {NZBGET_COMPLETE_DIR}')
    print(f'Target Plex Directory: {plex_dir}')
    
    # Validate directories exist
    if not os.path.exists(NZBGET_COMPLETE_DIR):
        error_msg = f"NZBGet complete directory not found: {NZBGET_COMPLETE_DIR}"
        print(f"ERROR: {error_msg}")
        messages.error(request, error_msg)
        return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
    
    if not os.path.exists(plex_dir):
        error_msg = f"Plex directory not found: {plex_dir}. Is your external drive mounted?"
        print(f"ERROR: {error_msg}")
        messages.error(request, error_msg)
        return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
    
    # Get list of files/folders to move
    items_to_move = os.listdir(NZBGET_COMPLETE_DIR)
    if not items_to_move:
        msg = "No files found in NZBGet complete directory."
        print(msg)
        messages.info(request, msg)
        return JsonResponse({'status': 'success', 'message': msg, 'moved_count': 0}, status=200)
    
    print(f"Found {len(items_to_move)} items to move.")
    moved_count = 0
    failed_items = []
    
    for item_name in tqdm(items_to_move, desc="Moving files"):
        try:
            source_path = os.path.join(NZBGET_COMPLETE_DIR, item_name)
            dest_path = os.path.join(plex_dir, item_name)
            
            print(f'Moving: {item_name}')
            
            # Handle existing destination
            if os.path.exists(dest_path):
                print(f'WARNING: {dest_path} already exists. Skipping.')
                failed_items.append({'name': item_name, 'reason': 'Already exists at destination'})
                continue
            
            shutil.move(source_path, dest_path)
            moved_count += 1
            print(f'✓ Successfully moved: {item_name}')
            
        except PermissionError as e:
            error_msg = f"Permission denied moving {item_name}: {e}"
            print(f"ERROR: {error_msg}")
            failed_items.append({'name': item_name, 'reason': 'Permission denied'})
        except Exception as e:
            error_msg = f"Error moving {item_name}: {e}"
            print(f"ERROR: {error_msg}")
            failed_items.append({'name': item_name, 'reason': str(e)})
    
    # Prepare response message
    if moved_count > 0:
        success_msg = f"Successfully moved {moved_count} item(s) to {dir_type}."
        print(success_msg)
        messages.success(request, success_msg)
    
    if failed_items:
        failed_msg = f"Failed to move {len(failed_items)} item(s)."
        print(failed_msg)
        messages.warning(request, failed_msg)
    
    return JsonResponse({
        'status': 'success' if not failed_items else 'partial',
        'message': f'Moved {moved_count} item(s)',
        'moved_count': moved_count,
        'failed_count': len(failed_items),
        'failed_items': failed_items
    }, status=200)


def move_downloaded_tv_show_files_to_plex(request):
    """
    Move downloaded TV show files to Plex and refresh episode database.
    """
    print('move_downloaded_tv_show_files_to_plex')
    
    # Start file movement in background thread
    def move_and_sync():
        json_response = move_downloaded_files_to_plex(request, PLEX_TV_SHOW_DIR)
        
        # If files were moved, sync with Plex
        if json_response.status_code == 200:
            try:
                from .plexController.add_episodes_to_show import main as add_episodes_to_show
                print("Syncing episodes with Plex...")
                add_episodes_to_show()
                print("✓ Episode sync completed.")
            except plexapi.exceptions.NotFound as e:
                error_msg = f'Plex sync error: {e}. Is your external drive mounted?'
                print(f"ERROR: {error_msg}")
                messages.error(request, error_msg)
            except Exception as e:
                error_msg = f'Error syncing with Plex: {e}'
                print(f"ERROR: {error_msg}")
                messages.error(request, error_msg)
    
    # Run in background thread
    move_thread = threading.Thread(target=move_and_sync, daemon=True)
    move_thread.start()
    
    messages.info(request, "File move and Plex sync started. Check console for progress.")
    return redirect(request.META.get('HTTP_REFERER'))


def move_downloaded_movie_files_to_plex(request):
    """
    Move downloaded movie files to Plex directory in background.
    """
    print('move_downloaded_movie_files_to_plex')
    
    # Run in background thread
    def move_movies():
        move_downloaded_files_to_plex(request, PLEX_MOVIES_DIR)
    
    move_thread = threading.Thread(target=move_movies, daemon=True)
    move_thread.start()
    
    messages.info(request, "Movie file move started. Check console for progress.")
    return redirect(request.META.get('HTTP_REFERER'))


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
    
    # Start download in background thread
    download_thread = threading.Thread(
        target=nzb_geek.download_from_results,
        args=(search_results, request),
        daemon=True
    )
    download_thread.start()
    messages.info(request, f"Download started for {movie.name}. Check console for progress.")

    return HttpResponseRedirect(reverse('movies_index'))


def movie_index(request, movie_id):
    print('movie_index')
    movie = Movie.objects.filter(id=movie_id).first()
    index_context = {"title": "Movie", "movie": movie}

    return render(request, "movie.html", index_context)


def cast_member(request, cast_member_id):
    # TODO: GET CAST_MEMBERS OF SHOW IF NONE EXIST WHEN SHOW PAGE IS TRAVELED TO
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


def find_missing_episodes(request, show_id):
    show = Show.objects.get(id=show_id)
    missing_episodes = Episode.objects.filter(show=show, on_disk=False)
    episodes_table = EpisodeTable(missing_episodes)
    episodes_table.paginate(page=request.GET.get("page", 1), per_page=10)

    index_context = {
        "title": "Missing Episodes",
        "show": show,
        "episodes": episodes_table,
    }
    return render(request, "missing_episodes.html", index_context)


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
