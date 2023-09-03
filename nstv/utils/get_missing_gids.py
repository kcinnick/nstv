from nstv.download import NZBGeek
from nstv_fe.nstv_fe.models import Show
from nstv.nstv import get_db_session


def main():
    nzbg = NZBGeek()
    nzbg.login()

    db_session = get_db_session()
    nzbg.db_session = db_session

    shows_missing_gids = Show.objects.filter(gid=None)
    for show in shows_missing_gids:
        print(show)
        nzbg.get_gid(show.title)


if __name__ == '__main__':
    main()
