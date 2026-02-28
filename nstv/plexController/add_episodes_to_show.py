import os

import django
from plexapi.myplex import MyPlexAccount
from tqdm import tqdm

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Show, Episode

SHOW_ALIASES = {
    # plex title: django title
    '6ixtynin9 the Series': '6ixtynin9',
    "Beachfront Bargain Hunt Renovation": "Beachfront Bargain Hunt: Renovation",
}

SEASON_TITLE_REPLACEMENTS = {
    # sometimes the season ordering is different from TVDB to NZBGeek.
    # When this happens, we can use the below dict to map the episode correctly.
    'Running Man': {
        'S2010': 'S01',
        'S2011': 'S02',
        'S2012': 'S03',
        'S2013': 'S04',
        'S2014': 'S05',
        'S2015': 'S06',
        'S2016': 'S07',
        'S2017': 'S08',
        'S2018': 'S09',
        'S2019': 'S10',
        'S2020': 'S11',
        'S2021': 'S12',
        'S2022': 'S13',
        'S2023': 'S14',
        'S2024': 'S15',
    },
    'Lupin': {
        'Season 1 - Part 1 & 2': 'S01',
        'Season 2 - Part 3': 'S02'
    }
}


def get_plex_connection():
    plex_email = os.getenv('PLEX_EMAIL')
    plex_api_key = os.getenv('PLEX_API_KEY')
    plex_server = os.getenv('PLEX_SERVER')
    if not plex_email or not plex_api_key or not plex_server:
        raise ValueError('Missing one of PLEX_EMAIL, PLEX_API_KEY, or PLEX_SERVER environment variables.')

    account = MyPlexAccount(plex_email, plex_api_key)
    return account.resource(plex_server).connect()


def _resolve_season_number(plex_show, plex_episode):
    show_replacements = SEASON_TITLE_REPLACEMENTS.get(plex_show.title)
    if not show_replacements:
        return str(plex_episode.seasonNumber)

    season_name = getattr(plex_episode, 'seasonName', None)
    if season_name and season_name in show_replacements:
        return show_replacements[season_name]

    fallback_key = f"S{plex_episode.seasonNumber}"
    if fallback_key in show_replacements:
        return show_replacements[fallback_key]

    return str(plex_episode.seasonNumber)


def add_existing_episodes_for_plex_show(plex_show):
    show_title = plex_show.title
    if show_title in SHOW_ALIASES:
        show_title = SHOW_ALIASES[plex_show.title]

    django_show_object = Show.objects.filter(title=show_title).first()
    if not django_show_object:
        django_show_object = Show.objects.create(title=show_title)

    django_episodes = Episode.objects.filter(show=django_show_object)
    created_count = 0
    updated_count = 0

    for plex_episode in plex_show.episodes():
        if getattr(plex_episode, 'title', None):
            django_episode = django_episodes.filter(
                title=plex_episode.title,
                season_number=str(plex_episode.seasonNumber)
            ).first()
            if not django_episode:
                django_episode = django_episodes.filter(
                    title=plex_episode.title.replace('.', ''),
                    season_number=str(plex_episode.seasonNumber)
                ).first()
            if django_episode:
                if not django_episode.on_disk:
                    django_episode.on_disk = True
                    django_episode.save()
                    updated_count += 1
            else:
                season_number = _resolve_season_number(plex_show, plex_episode)
                django_episode = Episode(
                    show=django_show_object,
                    air_date=plex_episode.originallyAvailableAt,
                    title=plex_episode.title,
                    season_number=season_number,
                    episode_number=plex_episode.index,
                    on_disk=True
                )
                django_episode.save()
                created_count += 1

    return created_count, updated_count


def add_episodes_to_nstv(plex=None):
    if plex is None:
        plex = get_plex_connection()

    total_created = 0
    total_updated = 0
    plex_tv_shows = plex.library.section('TV Shows')
    for plex_show in tqdm(plex_tv_shows.search()):
        created_count, updated_count = add_existing_episodes_for_plex_show(plex_show)
        total_created += created_count
        total_updated += updated_count
    return total_created, total_updated


def main():
    add_episodes_to_nstv()
    return


if __name__ == '__main__':
    main()
