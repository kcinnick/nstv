#!/usr/bin/env python

"""Tests for `nstv` package."""
from datetime import datetime, timedelta
import os

import pytest

from nstv import nstv
from nstv.download import NZBGeek
from nstv.models import Episode, Show

SKIP_REASON = "not on local, can't hit database."


def test_search_channels():
    json_response = nstv.search_channels(
        start_channel=2, end_channel=29,
        start_date='2021-05-04', end_date='2021-05-05')

    expected_channel_list = [2, 3, 4, 5, 6, 7, 8, 9, 11, 15, 16,
                             17, 20, 22, 23, 24, 25, 27, 28, 29]
    actual_channel_list = []
    for item in json_response:
        actual_channel_list.append(item['channel']['channelNumber'])

    assert expected_channel_list == actual_channel_list


def test_nzbg_login():
    nzb_geek = NZBGeek()
    assert 'User-Agent' in nzb_geek.session.headers.keys()
    nzb_geek.login()
    #  go to dashboard and assert expected info is found
    r = nzb_geek.session.get(
        'https://nzbgeek.info/dashboard.php?myaccount'
    )
    assert 'my account' in str(r.content)


def test_parse_search_channels_response():
    session = nstv.get_db_session()

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

    assert len(shows) > 4
    assert len(episodes) > 10


def test_episode_query():
    db_session = nstv.get_db_session()

    show = db_session.query(Show).where(Show.title == 'The Kitchen').first()
    for episode in show.episodes[:2]:
        assert episode.title in ['Kitchen Cantina', 'Spice It Up!']


def test_search_nzbgeek_for_episode():
    db_session = nstv.get_db_session()
    episode = db_session.query(Episode).where(
        Episode.title == 'Twins for the Win').first()
    nzbgeek = NZBGeek()
    nzbgeek.login()
    nzbgeek.search_nzbgeek_for_episode(episode)
    return


def test_get_nzb_by_season_episode_numbers():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()
    show = db_session.query(Show).where(Show.title == 'Chopped').first()
    nzbgeek.get_nzb(show, season_number=48, episode_number=3)


def test_get_nzb_by_episode_title():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()
    show = db_session.query(Show).where(Show.title == 'Chopped').first()
    nzbgeek.get_nzb(show, episode_title='Mix and Mache')


def test_get_missing_nzb():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    show = Show(title='Chopped', gid='85019')
    with pytest.raises(AttributeError):
        nzbgeek.get_nzb(show, season_number=-99, episode_number=-99)


def test_get_or_create_show():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()
    fake_listing = {'showName': 'thisisforthetest'}

    fake_show = nstv.get_or_create_show(fake_listing, db_session)
    #  assert show is now in the db
    fake_show_entry = db_session.query(Show).where(Show.title == fake_show.title).first()
    assert fake_show_entry

    #  clean up fake show db entry
    db_session.delete(fake_show)
    db_session.commit()


def test_get_or_create_episode():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()
    fake_episode = {
        'episodeTitle': 'thisepisodeisforthetest',
        'listDateTime': '9999-04-04'
    }
    show = nstv.get_or_create_show(
        listing={'showName': 'Chopped'}, db_session=db_session)
    fake_episode = nstv.get_or_create_episode(fake_episode, show, db_session)
    #  assert show is now in the db
    fake_episode_entry = db_session.query(Episode).where(Episode.title == fake_episode.title).first()
    assert fake_episode_entry

    #  clean up fake show db entry
    db_session.delete(fake_episode)
    db_session.commit()


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
def test_login_bounces_if_already_logged_in():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    nzbgeek.login()


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_get_or_create_show_with_title_arg():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    db_session = nstv.get_db_session()
    start_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    search_response = nstv.search_channels(
        start_channel=44,
        end_channel=46,
        start_date=start_date,
        end_date=end_date,
    )

    listings = search_response[0]['listings']
    nstv.get_or_create_show(
        listing=listings[0],
        db_session=db_session,
        title='Seinfeld',
    )


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_assert_error_is_raised_on_bad_search():
    nzbgeek = NZBGeek()
    nzbgeek.login()
    start_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    with pytest.raises(ValueError):
        nstv.search_channels(
            start_channel=44,
            end_channel=12,
            start_date=start_date,
            end_date=end_date,
        )
