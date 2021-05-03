#!/usr/bin/env python

"""Tests for `nstv` package."""
import pytest

"""Main module."""
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


@pytest.mark.skipif(os.getenv("POSTGRES_PASSWORD"), reason="not on local, can't hit database.")
def test_parse_search_channels_response():
    database_url = (
        f'postgresql://postgres:{os.getenv("POSTGRES_PASSWORD")}'
        f'@127.0.0.1:5432/postgres'
    )
    engine = create_engine(database_url, echo=True)

    #  create tables in models.py if they don't already exist
    Base.metadata.create_all(engine)

    #  create db session
    Session = sessionmaker(bind=engine)
    session = Session()

    json_response = nstv.search_channels(start_channel=45, end_channel=46)
    parsed_response = nstv.parse_search_channel_response(
        db_session=session, response=json_response)
