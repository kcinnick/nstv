import os

import django
from plexapi.myplex import MyPlexAccount

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Show, Episode

account = MyPlexAccount('nicktucker4@gmail.com', os.getenv('PLEX_API_KEY'))
plex = account.resource(os.getenv('PLEX_SERVER')).connect()  # returns a PlexServer instance

plex_tv_shows = plex.library.section('TV Shows')


def add_existing_episodes_for_plex_show(plex_show):
    django_show_object = Show.objects.get(title=plex_show.title)
    django_episodes = Episode.objects.filter(show=django_show_object)
    print("django_show_object: ", django_show_object)
    print("django_episodes: ", django_episodes)

    # match the shows first, then match the episodes of the shows
    for plex_episode in plex_show.episodes():
        if plex_episode.title:
            django_episode = django_episodes.filter(title=plex_episode.title).first()
            if django_episode:
                print('episode already exists')
            else:
                django_episode = Episode(
                    show=django_show_object,
                    air_date=plex_episode.originallyAvailableAt,
                    title=plex_episode.title,
                    season_number=plex_episode.seasonNumber,
                    number=plex_episode.index,
                )
                django_episode.save()
                print('episode added to database')

    return


def main():
    for plex_show in plex_tv_shows.search():
        add_existing_episodes_for_plex_show(plex_show)
    return


if __name__ == '__main__':
    main()
