import os

import django
from plexapi.myplex import MyPlexAccount
from tqdm import tqdm

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Show, Episode

account = MyPlexAccount('nicktucker4@gmail.com', os.getenv('PLEX_API_KEY'))
plex = account.resource(os.getenv('PLEX_SERVER')).connect()  # returns a PlexServer instance

plex_tv_shows = plex.library.section('TV Shows')

SHOW_ALIASES = {
    # plex title: django title
    '6ixtynin9 the Series': '6ixtynin9'
}


def add_existing_episodes_for_plex_show(plex_show):
    print("plex_show: ", plex_show.title)
    if plex_show.title in SHOW_ALIASES:
        plex_show.title = SHOW_ALIASES[plex_show.title]
    django_show_object = Show.objects.get(title=plex_show.title)
    django_episodes = Episode.objects.filter(show=django_show_object)
    #print("django_show_object: ", django_show_object)
    #print("django_episodes: ", django_episodes)

    # match the shows first, then match the episodes of the shows
    for plex_episode in plex_show.episodes():
        if plex_episode.title:
            django_episode = django_episodes.filter(title=plex_episode.title).first()
            if django_episode:
                #print('episode already exists')
                # if the show is on plex, it's on disk, so we can update that if necessary
                django_episode.on_disk = True
                django_episode.save()
            else:
                django_episode = Episode(
                    show=django_show_object,
                    air_date=plex_episode.originallyAvailableAt,
                    title=plex_episode.title,
                    season_number=plex_episode.seasonNumber,
                    episode_number=plex_episode.index,
                    on_disk=True
                )
                django_episode.save()
                print('episode added to database')

    return


def main():
    for plex_show in tqdm(plex_tv_shows.search()):
        add_existing_episodes_for_plex_show(plex_show)
    return


if __name__ == '__main__':
    main()
