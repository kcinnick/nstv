"""Main module."""
from datetime import datetime, timedelta

import os
from sqlalchemy import create_engine
import requests
from sqlalchemy.orm import sessionmaker


def search_channels(start_channel, end_channel, start_date, end_date):
    """
    start_channel: int
    end_channel: int

    Executes a search for the supplied range of channels from start_channel
    to end_channel and returns the accompanying JSON response object.
    """
    print('\nSearching channels for TV showing details..\n')
    url = f'https://tvtv.us/tvm/t/tv/v4/lineups/95197D/listings/grid?detail='
    url += '%27brief%27&'
    url += f'start={start_date}T04:00:00.000'
    url += 'Z&'
    url += f'end={end_date}T03:59:00.000'
    url += f'Z&startchan={start_channel}&endchan={end_channel}'
    r = requests.get(
        url
    )
    assert r.status_code == 200
    return r.json()


def get_or_create_show(listing, db_session, title=None):
    """
    listing:  JSON object representing an episode listing returned by nstv.search_channels
    db_session:  sqlalchemy.orm.Session object

    Creates and returns new Show object for show indicated in an
    episode listing and commits the object against the database.
    If an object matching the show's title already exists,
    this function only returns the existing show's object.
    """
    #  check if show exists in DB
    if title:
        listing['showName'] = title

    query = db_session.query(Show).filter(Show.title == listing['showName'])
    if query.first():
        print(f"{listing['showName']} already in DB.")
        show = query.first()
        return show

    show = Show(
        title=listing['showName'],
        slug=listing['showName'].replace(
            ' ', '').replace('-', '').replace(',', '').replace(
            '\'', '').lower(),
    )
    #show.get_episodes(db_session)
    db_session.add(show)
    db_session.commit()

    return show


def get_or_create_episode(listing, show, db_session):
    """
    listing:  JSON object representing an episode listing returned by nstv.search_channels
    db_session:  sqlalchemy.orm.Session object

    Creates and returns new Episode object for episode indicated in a
    listing and commits the object against the database.
    If an object matching the episode's title already exists,
    this function only returns the existing episode's object.
    """
    episode_slug = show.slug + listing['episodeTitle'].replace(
        ' ', '').replace('-', '').replace(',', '').lower()
    #  check if episode for show exists in DB
    episode_query = db_session.query(Episode).filter(Episode.slug == episode_slug)
    if episode_query.first():
        episode = episode_query.first()
        print(f"{episode.title} already in DB.")
        return episode

    episode = Episode(
        air_date=listing['listDateTime'],
        title=listing['episodeTitle'],
        slug=episode_slug,
        show_id=show.id
    )
    db_session.add(episode)
    db_session.commit()

    return episode


def parse_channel_search_response(db_session, response):
    """
    db_session:  sqlalchemy.orm.Session object
    response:  JSON object containing a list of episodes returned by a call to search_channels

    Parses the JSON response returned from a search
    into the appropriate episode or show models.
    """
    listings = response[0]['listings']
    shows = []
    episodes = []
    for listing in listings:
        if listing['showName'] == 'Paid Program':
            continue
        show = get_or_create_show(listing, db_session)
        if show not in shows:
            shows.append(show)
        episode = get_or_create_episode(listing, show, db_session)
        if episode not in episodes:
            episodes.append(episode)

    return shows, episodes


def get_db_session():
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
    return session


def main():
    session = get_db_session()

    start_date = (datetime.now() - timedelta(10)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    response = search_channels(
        start_channel=44,
        end_channel=47,
        start_date=start_date,
        end_date=end_date
    )
    parse_channel_search_response(db_session=session, response=response)

    return session  # for use in IDE


if __name__ == '__main__':
    from models import Base, Episode, Show

    main()
else:
    from nstv.models import Base, Episode, Show
