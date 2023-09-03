from nstv.download import NZBGeek
from nstv_fe.nstv_fe.models import Show
from nstv.nstv import get_db_session
from django import setup
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nstv_fe.nstv_fe.settings')
setup()


def main():
    nzbg = NZBGeek()
    nzbg.login()

    shows_missing_gids = Show.objects.filter(gid=None)
    print(shows_missing_gids)
    for show in shows_missing_gids:
        print(show.gid)
        nzbg.get_gid(show.title)


if __name__ == '__main__':
    main()
