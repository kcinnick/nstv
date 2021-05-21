from nstv.download import NZBGeek
from nstv.models import Show
from nstv.nstv import get_db_session


def main():
    nzbg = NZBGeek()
    nzbg.login()

    db_session = get_db_session()
    nzbg.db_session = db_session

    shows_missing_gids = db_session.query(Show).where(Show.gid == None)
    for show in shows_missing_gids:
        print(show)
        nzbg.get_gid(show.title)


if __name__ == '__main__':
    main()
