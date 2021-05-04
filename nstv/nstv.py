"""Main module."""
import os
from sqlalchemy import create_engine
from pprint import pprint
import requests
from sqlalchemy.orm import sessionmaker


def search_channels(start_channel, end_channel):
    """
    start_channel: int
    end_channel: int
    """
    print('\nSearching channels for TV showing details..\n')
    url = f'https://tvtv.us/tvm/t/tv/v4/lineups/95197D/listings/grid?detail='
    url += '%27brief%27&'
    url += 'start=2021-05-01T04:00:00.000'
    url += 'Z&'
    url += 'end=2021-05-02T03:59:00.000'
    url += f'Z&startchan={start_channel}&endchan={end_channel}'
    r = requests.get(
        url
    )
    assert r.status_code == 200
    return r.json()


def build_show_object(listing, db_session):
    show = Show(
        title=listing['showName'],
        slug=listing['showName'].replace(
            ' ', '').replace('-', '').replace(',', '').replace(
            '\'', '').lower(),
    )
    #  check if show exists in DB
    query = db_session.query(Show).filter(Show.title == show.title)
    if query.first():
        print(f"{show.title} already in DB.")
        show = query.first()
    else:
        db_session.add(show)
        db_session.commit()

    return show


def build_episode_object(listing, show, db_session):
    episode = Episode(
        air_date=listing['listDateTime'],
        title=listing['episodeTitle'],
        slug=show.slug + listing['episodeTitle'].replace(
            ' ', '').replace('-', '').replace(',', '').lower(),
        show_id=show.id
    )
    #  check if episode for show exists in DB
    episode_query = db_session.query(Episode).filter(Episode.slug == episode.slug)
    if episode_query.first():
        print(f"{episode.title} already in DB.")
        episode = episode_query.first()
    else:
        db_session.add(episode)
        db_session.commit()

    return episode


def parse_channel_search_response(db_session, response):
    listings = response[0]['listings']
    shows = episodes = []
    for listing in listings:
        if listing['showName'] == 'Paid Program':
            continue
        show = build_show_object(listing, db_session)
        shows.append(show)
        episode = build_episode_object(listing, show, db_session)
        episodes.append(episode)

    return shows, episodes


def main():
    database_url = (
        f'postgresql://postgres:{os.getenv("POSTGRES_PASSWORD")}'
        f'@127.0.0.1:5432/postgres'
    )
    engine = create_engine(database_url, echo=False)

    #  create tables in models.py if they don't already exist
    Base.metadata.create_all(engine)

    #  create db session
    Session = sessionmaker(bind=engine)
    session = Session()
    response = search_channels(start_channel=45, end_channel=46)


if __name__ == '__main__':
    from models import Base, Episode, Show
    main()
else:
    from nstv.models import Base, Episode, Show
