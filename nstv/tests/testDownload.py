import os
import re

import pytest
from bs4 import BeautifulSoup
from django.test import TestCase

from nstv.download import NZBGeek, SearchResult
from nstv.models import Show

NZBGET_NZB_DIR = os.getenv("NZBGET_NZB_DIR")


class NZBGeekTestCase(TestCase):
    def setUp(self):
        # Create a record before each test
        self.show_record = Show.objects.create(title='The Secret Life of the Zoo')
        self.nzb_geek = NZBGeek()
        self.nzb_geek.login()

    def tearDown(self):
        # Delete the record after each test
        self.show_record.delete()

    def test_login(self):
        self.assertTrue(self.nzb_geek.logged_in)

    def test_gid(self):
        gid = self.nzb_geek.get_gid(self.show_record.title)
        self.assertEqual(gid, '306705')


class SearchResultTestCase(TestCase):
    def setUp(self):
        self.nzb_geek = NZBGeek()
        self.nzb_geek.login()
        self.zoo_show_record = Show.objects.create(title='The Secret Life of the Zoo', gid='306705', id=1)
        self.anime_record = Show.objects.create(title='Death Note', gid='79481', id=2)
        self.zoo_show_record.save()
        self.anime_record.save()
        self.search_results_for_zoo_show = self.nzb_geek.get_nzb_search_results(
            self.zoo_show_record, season_number=10, episode_number=1
        )
        self.search_results_for_anime = self.nzb_geek.get_nzb_search_results(
            self.anime_record, season_number=1, episode_number=15, anime=True
        )

    def tearDown(self):
        self.zoo_show_record.delete()
        self.anime_record.delete()

    def test_search_results(self):
        self.assertTrue(self.search_results_for_anime)
        self.assertTrue(self.search_results_for_zoo_show)

    def test_search_result(self):
        search_result = self.search_results_for_zoo_show[0]
        self.assertIsInstance(search_result, SearchResult)
        self.assertTrue(search_result.title)
        self.assertTrue(search_result.category)
        self.assertTrue(search_result.file_size)
        self.assertTrue(search_result.download_url)
        self.assertTrue(search_result.grabs)
        self.assertTrue(search_result.audio_tracks)

    def test_get_audio_tracks(self):
        search_result = self.search_results_for_zoo_show[0]
        self.assertTrue(search_result.audio_tracks)
        self.assertEqual(search_result.audio_tracks, ['English'])

    def test_get_audio_tracks_for_anime(self):
        search_result = self.search_results_for_anime[0]
        self.assertTrue(search_result.audio_tracks)
        self.assertTrue('Japanese' in search_result.audio_tracks)
