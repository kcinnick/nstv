"""Main module."""
import os
from sqlalchemy import create_engine
from pprint import pprint
import requests
from sqlalchemy.orm import sessionmaker

from nstv.models import Base, Episode, Show


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


def parse_search_channel_response(response):
    return


def main():
    engine = create_engine(
        f'postgresql://postgres:{os.getenv("POSTGRES_PASSWORD")}"'
        f'@127.0.0.1:5432/postgres', echo=True)
    #  create tables in models.py if they don't already exist
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    response = search_channels(start_channel=2, end_channel=29)


if __name__ == '__main__':
    main()
