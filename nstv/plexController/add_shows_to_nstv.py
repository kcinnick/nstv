import os

import django
from plexapi.myplex import MyPlexAccount

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Show


def get_plex_connection():
    plex_email = os.getenv('PLEX_EMAIL')
    plex_api_key = os.getenv('PLEX_API_KEY')
    plex_server = os.getenv('PLEX_SERVER')
    if not plex_email or not plex_api_key or not plex_server:
        raise ValueError('Missing one of PLEX_EMAIL, PLEX_API_KEY, or PLEX_SERVER environment variables.')

    account = MyPlexAccount(plex_email, plex_api_key)
    return account.resource(plex_server).connect()


def _is_anime_by_genres(genres):
    normalized_genres = [str(genre).strip().lower() for genre in genres]
    return 'anime' in normalized_genres or 'animation' in normalized_genres


def upsert_show_from_plex_show(plex_show):
    is_anime = _is_anime_by_genres(getattr(plex_show, 'genres', []))
    show_title = plex_show.title
    show_object = Show.objects.filter(title=show_title).first()
    if show_object:
        if is_anime and not show_object.anime:
            show_object.anime = True
            show_object.save()
        return show_object, False

    show_object = Show.objects.create(title=show_title, anime=is_anime)
    return show_object, True


def add_shows_to_nstv(plex=None):
    if plex is None:
        plex = get_plex_connection()

    created_count = 0
    plex_tv_shows = plex.library.section('TV Shows')
    for show in plex_tv_shows.search():
        _, created = upsert_show_from_plex_show(show)
        if created:
            created_count += 1

    return created_count


def main():
    add_shows_to_nstv()
    return


if __name__ == '__main__':
    main()
