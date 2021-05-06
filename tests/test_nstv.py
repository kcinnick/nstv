#!/usr/bin/env python

"""Tests for `nstv` package."""
import pytest

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nstv import nstv
from nstv.download import NZBGeek
from nstv.models import Base, Episode, Show


def test_search_channels():
    json_response = nstv.search_channels(
        start_channel=2, end_channel=29, start_date='2021-05-04', end_date='2021-05-05')
    from pprint import pprint
    pprint(json_response)
    expected_channel_list = [2, 3, 4, 5, 6, 7, 8, 9, 11, 15, 16,
                             17, 20, 22, 23, 24, 25, 27, 28, 29]
    actual_channel_list = []
    for item in json_response:
        actual_channel_list.append(item['channel']['channelNumber'])

    assert expected_channel_list == actual_channel_list


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason="not on local, can't hit database.")
def test_parse_search_channels_response():
    session = nstv.get_db_session()

    from datetime import datetime, timedelta
    start_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    json_response = nstv.search_channels(
        start_channel=45,
        end_channel=46,
        start_date=start_date,
        end_date=end_date
    )
    shows, episodes = nstv.parse_channel_search_response(
        db_session=session,
        response=json_response
    )

    assert len(shows) > 5
    assert len(episodes) > 10


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason="not on local, can't hit database.")
def test_episode_query():
    db_session = nstv.get_db_session()

    show = db_session.query(Show).where(Show.title == 'The Kitchen').first()
    for episode in show.episodes[:2]:
        assert episode.title in ['Kitchen Cantina', 'Spice It Up!']


def test_login_nzbgeek():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    return


def test_search_nzbgeek():
    db_session = nstv.get_db_session()
    episode = db_session.query(Episode).where(Episode.title == 'Twins for the Win').first()
    nzbgeek = NZBGeek()
    nzbgeek.login()
    nzbgeek.search_nzbgeek(episode)
    return


def test_get_nzb():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()
    show = db_session.query(Show).where(Show.title == 'Chopped').first()
    nzbgeek.get_nzb(show, season_number=1, episode_number=4)
