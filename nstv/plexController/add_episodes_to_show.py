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


def add_existing_episodes_for_plex_show(plex_show):
    show_title = plex_show.title
    print('plex_show: ', plex_show)
    print('show_title: ', show_title)
    # check if the show is in the SHOW_ALIASES dict, and if so, use the alias
    if show_title in SHOW_ALIASES.keys():
        show_title = SHOW_ALIASES[plex_show.title]
    django_show_object = Show.objects.get(title=show_title)
    django_episodes = Episode.objects.filter(show=django_show_object)
    # print("django_show_object: ", django_show_object)
    # print("django_episodes: ", django_episodes)

    # match the shows first, then match the episodes of the shows
    for plex_episode in plex_show.episodes():
        if plex_episode.title:
            django_episode = django_episodes.filter(
                title=plex_episode.title,
                season_number=plex_episode.seasonNumber
            ).first()
            if not django_episode:
                django_episode = django_episodes.filter(
                    title=plex_episode.title.replace('.', ''),
                    season_number=plex_episode.seasonNumber
                ).first()
            if django_episode:
                # if the show is on plex, it's on disk, so we can update that if necessary
                django_episode.on_disk = True
                django_episode.save()
            else:
                if plex_show.title in SEASON_TITLE_REPLACEMENTS.keys():
                    if plex_episode.seasonNumber in SEASON_TITLE_REPLACEMENTS[plex_show.title].keys():
                        season_number = SEASON_TITLE_REPLACEMENTS[plex_show.title][plex_episode.seasonName]
                    else:
                        season_number = plex_episode.seasonNumber
                else:
                    season_number = plex_episode.seasonNumber
                django_episode = Episode(
                    show=django_show_object,
                    air_date=plex_episode.originallyAvailableAt,
                    title=plex_episode.title,
                    season_number=season_number,
                    episode_number=plex_episode.index,
                    on_disk=True
                )
                django_episode.save()
                print('episode added to database')

    return


def main():
    account = MyPlexAccount('nicktucker4@gmail.com', os.getenv('PLEX_API_KEY'))
    plex = account.resource(os.getenv('PLEX_SERVER')).connect()  # returns a PlexServer instance

    plex_tv_shows = plex.library.section('TV Shows')
    for plex_show in tqdm(plex_tv_shows.search()):
        add_existing_episodes_for_plex_show(plex_show)
    return


if __name__ == '__main__':
    main()
