#!/usr/bin/env python

"""Tests for `nstv` package."""
import os
from bs4 import BeautifulSoup
import pytest

from nstv import nstv
from nstv.download import NZBGeek, SearchResult
from nstv.models import Episode, Show

SKIP_REASON = "not on local, can't hit database."


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_get_gid():
    # test setup
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()
    worst_cooks_query = db_session.query(Show).where(Show.title == "Worst Cooks in America")
    #  set Worst Cooks GID to 0
    show = worst_cooks_query.first()
    show.gid = 0
    db_session.add(show)
    db_session.commit()
    #  now use get_gid method to reset it to the proper value
    nzbgeek.get_gid('Worst Cooks in America')
    show = worst_cooks_query.first()
    assert show.gid == 134441


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_get_gid_for_show_without_db_entry_raises_error():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    with pytest.raises(AssertionError):
        nzbgeek.get_gid('Medical Frontiers')


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_get_gid_for_slugged_show_name():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    nzbgeek.get_gid(show_title='Diners, Drive-Ins and Dives')


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_get_gid_for_show_without_releases():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()

    nstv.get_or_create_show(
        listing={'showName': 'Sommerdahl', },
        db_session=db_session,
    )


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_get_nzb_without_season_number_or_episode_title_raises_error():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    with pytest.raises(AttributeError):
        nzbgeek.get_nzb(show='Seinfeld')
