import os
import re

from bs4 import BeautifulSoup

from nstv.download import NZBGeek, SearchResult
from nstv.models import Show

NZBGET_NZB_DIR = os.getenv("NZBGET_NZB_DIR")


def test_login():
    nzb_geek = NZBGeek()
    nzb_geek.login()
    assert nzb_geek.logged_in is True
    return


def test_get_gid():
    nzb_geek = NZBGeek()
    nzb_geek.login()
    show = Show.objects.all().filter(title='The Secret Life of the Zoo').first()
    show.gid = None
    gid = nzb_geek.get_gid(show.title)
    assert gid == '306705'
    return


def test_get_nzb_search_results_attributes():
    nzb_geek = NZBGeek()
    nzb_geek.login()
    show = Show.objects.get(title='Neon Genesis Evangelion')
    results = nzb_geek.get_nzb_search_results(
        show, season_number=1, episode_number=4,
        episode_title='Hedgehog\'s Dilemma', anime=True
    )
    for result in results:
        assert result.category == 'TV > Anime'
        assert re.search('[[eE]vangelion', result.title)

