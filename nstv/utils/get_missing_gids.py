import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.download import NZBGeek
from nstv.models import Show


def main():
    nzbg = NZBGeek()
    nzbg.login()

    shows_missing_gids = Show.objects.filter(gid=None)
    for show in shows_missing_gids:
        print(show)
        nzbg.get_gid(show.title)


if __name__ == '__main__':
    main()
