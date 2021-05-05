#!/usr/bin/env python

"""Tests for `nstv` package."""
import pytest

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nstv import nstv
from nstv.models import Base, Episode, Show


def test_search_channels():
    json_response = nstv.search_channels(start_channel=2, end_channel=29)
    expected_channel_list = [2, 3, 4, 5, 6, 7, 8, 9, 11, 15, 16,
                             17, 20, 22, 23, 24, 25, 27, 28, 29]
    actual_channel_list = []
    for item in json_response:
        actual_channel_list.append(item['channel']['channelNumber'])

    assert expected_channel_list == actual_channel_list


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason="not on local, can't hit database.")
def test_parse_search_channels_response():
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

    json_response = nstv.search_channels(
        start_channel=45, end_channel=46,
        start_date='2021-05-01',
        end_date='2021-05-02'
    )
    shows, episodes = nstv.parse_channel_search_response(
        db_session=session, response=json_response)
    actual_shows = [i.title for i in shows]
    actual_episodes = [i.title for i in episodes]
    expected_shows = ['Food Paradise', 'Diners, Drive-Ins and Dives']
    expected_episodes = [
        'Local Lowdown', 'Brew-Haha', 'Surf \'n Turf',
        'Wings, Dogs and Claws', 'Fresh, Filled and Fried', 'Funky Finds',
        'Cruisin\' the Italian Countryside', 'Family Matters', 'Chicken Chowfest',
        'Pizza, Pork and Peru', 'Triple D Nation: Fried and Smoked',
        'A World of Barbecue', 'Handy Helpings', 'Takeout: Bold Bites Brought Home',
        'South of the Border', 'You Called It'
    ]

    assert actual_shows == expected_shows
    assert actual_episodes == expected_episodes


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason="not on local, can't hit database.")
def test_episode_query():
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

    show = session.query(Show).where(Show.title == 'The Kitchen').first()
    for episode in show.episodes[:2]:
        assert episode.title in ['Kitchen Cantina', 'Spice It Up!']


