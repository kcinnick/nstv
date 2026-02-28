import os
import sys
from pathlib import Path

import django
from plexapi.myplex import MyPlexAccount
import requests
from django.conf import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Movie


def get_plex_connection():
    plex_email = os.getenv('PLEX_EMAIL')
    plex_api_key = os.getenv('PLEX_API_KEY')
    plex_server = os.getenv('PLEX_SERVER')
    if not plex_email or not plex_api_key or not plex_server:
        raise ValueError('Missing one of PLEX_EMAIL, PLEX_API_KEY, or PLEX_SERVER environment variables.')

    account = MyPlexAccount(plex_email, plex_api_key)
    return account.resource(plex_server).connect()


def _extract_director_name(directors):
    if not directors:
        return ''
    first_director = directors[0]
    return getattr(first_director, 'tag', str(first_director))


def _extract_genre_names(genres):
    return [getattr(genre, 'tag', str(genre)) for genre in genres]


def save_movie_poster(plex_movie, posters_dir=None):
    poster_url = getattr(plex_movie, 'posterUrl', None)
    movie_name = getattr(plex_movie, 'title', None) or getattr(plex_movie, 'name', None)
    if not movie_name:
        return None

    if posters_dir is None:
        posters_dir = Path(settings.BASE_DIR) / 'templates' / 'static' / 'images' / 'posters'
    posters_dir = Path(posters_dir)
    posters_dir.mkdir(parents=True, exist_ok=True)

    poster_save_path = posters_dir / f"{movie_name.replace(' ', '_')}.jpg"

    if poster_url and not poster_save_path.exists():
        response = requests.get(poster_url, allow_redirects=True, timeout=10)
        response.raise_for_status()
        with open(poster_save_path, 'wb') as file_handle:
            file_handle.write(response.content)
    elif not poster_url:
        return None

    return str(poster_save_path)


def upsert_movie_from_plex_movie(plex_movie, download_posters=False):
    movie_name = getattr(plex_movie, 'title', None) or getattr(plex_movie, 'name', None)
    if not movie_name:
        return None, False

    genre_names = _extract_genre_names(getattr(plex_movie, 'genres', []))
    director_name = _extract_director_name(getattr(plex_movie, 'directors', []))
    release_date = getattr(plex_movie, 'originallyAvailableAt', None)

    movie_object = Movie.objects.filter(name=movie_name).first()
    if movie_object:
        if not movie_object.genre and genre_names:
            movie_object.genre = genre_names
        if not movie_object.director and director_name:
            movie_object.director = director_name
        if not movie_object.on_disk:
            movie_object.on_disk = True
        if not movie_object.release_date and release_date:
            movie_object.release_date = release_date
        if download_posters and not movie_object.poster_path:
            movie_object.poster_path = save_movie_poster(plex_movie)
        movie_object.save()
        return movie_object, False

    movie_object = Movie.objects.create(
        name=movie_name,
        release_date=release_date,
        genre=genre_names,
        director=director_name,
        on_disk=True,
        poster_path=save_movie_poster(plex_movie) if download_posters else None,
    )
    return movie_object, True


def add_movies_to_nstv(plex=None, download_posters=False):
    if plex is None:
        plex = get_plex_connection()

    created_count = 0
    plex_movies = plex.library.section('Movies')
    for plex_movie in plex_movies.search():
        _, created = upsert_movie_from_plex_movie(plex_movie, download_posters=download_posters)
        if created:
            created_count += 1

    return created_count


def main():
    add_movies_to_nstv()
    return


if __name__ == '__main__':
    main()
