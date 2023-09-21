import os

import django
from plexapi.myplex import MyPlexAccount

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Show, Episode

account = MyPlexAccount('nicktucker4@gmail.com', os.getenv('PLEX_API_KEY'))
plex = account.resource(os.getenv('PLEX_SERVER')).connect()  # returns a PlexServer instance


def add_shows_to_nstv():
    plex_tv_shows = plex.library.section('TV Shows')
    for show in plex_tv_shows.search():
        print(show.title)
        is_anime = False
        for genre in show.genres:
            if genre == 'Anime':
                is_anime = True
            elif genre == 'Animation':
                is_anime = True
            else:
                is_anime = False
        show_object = Show.objects.all().filter(title=show.title)
        if show_object:
            print('show already exists')
            if is_anime:
                show_object[0].anime = True
                show_object[0].save()
                print('Show {} is anime'.format(show.title))
        else:
            print('show does not exist')
            show_object = Show(title=show.title, anime=is_anime)
            show_object.save()
            print('show added to database')

    return


def main():
    add_shows_to_nstv()
    return


if __name__ == '__main__':
    main()
