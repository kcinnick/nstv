import os
import re
from unittest.mock import Mock
from time import sleep

import pytest
from bs4 import BeautifulSoup
from django.test import TestCase

from nstv.download import NZBGeek, SearchResult, NZBGet
from nstv.models import Show, Episode, Download
from nstv.views import download_episode

NZBGET_NZB_DIR = os.getenv("NZBGET_NZB_DIR")


class NZBGeekTestCase(TestCase):
    def setUp(self):
        # Create a record before each test
        self.zoo_show_record = Show.objects.create(title='The Secret Life of the Zoo')
        self.seinfeld_show_record = Show.objects.create(title='Seinfeld', gid='79169')
        self.show_name_with_replacement = Show.objects.create(title='6ixtynin9')
        self.nzb_geek = NZBGeek()
        self.nzb_geek.login()

    def tearDown(self):
        # Delete the record after each test
        self.zoo_show_record.delete()

    def test_login(self):
        self.assertTrue(self.nzb_geek.logged_in)

    def test_login_twice_does_not_cause_failure(self):
        self.nzb_geek.login()
        self.assertTrue(self.nzb_geek.logged_in)

    def test_gid(self):
        gid = self.nzb_geek.get_gid(self.zoo_show_record.title)
        self.assertEqual('306705', gid)

    def test_get_gid_for_nonexistent_show(self):
        gid = self.nzb_geek.get_gid('this show does not exist')
        self.assertIsNone(gid)

    def test_get_gid_for_show_with_name_replacement(self):
        gid = self.nzb_geek.get_gid('6ixtynin9')
        self.assertEqual('438170', gid)

    def test_download_from_results(self):
        NZBGEEK_API_KEY = os.getenv("NZBGEEK_API_KEY")
        fake_result = SearchResult(result_table=None)
        fake_result.download_url = 'https://api.nzbgeek.info/api?t=get&id=c5aa16e660e438270756004d78c1c33e&apikey={}'.format(
            NZBGEEK_API_KEY)
        self.nzb_geek.download_from_results([fake_result])

    def test_download_from_results_empty_result_set_does_not_cause_failure(self):
        empty_result_set = []
        self.nzb_geek.download_from_results(empty_result_set)

    def test_get_nzb_search_results_without_season_number(self):
        search_results = self.nzb_geek.get_nzb_search_results(self.seinfeld_show_record,
                                                              episode_title='The Pony Remark')
        match_regex = re.compile(r'THE.PONY.REMARK', re.IGNORECASE)
        assert len(search_results) > 0
        for search_result in search_results:
            assert match_regex.search(search_result.title)

        return

    def test_get_nzb_search_results_without_season_number_or_episode_title_raises_error(self):
        with pytest.raises(AttributeError):
            self.nzb_geek.get_nzb_search_results(self.seinfeld_show_record)


class SearchResultTestCase(TestCase):
    def setUp(self):
        self.nzb_geek = NZBGeek()
        self.nzb_geek.login()
        self.zoo_show_record = Show.objects.create(title='The Secret Life of the Zoo', id=1)
        self.anime_record = Show.objects.create(title='Death Note', gid='79481', id=2)
        self.zoo_show_record.save()
        self.anime_record.save()
        self.search_results_for_zoo_show = self.nzb_geek.get_nzb_search_results(
            self.zoo_show_record, season_number=10, episode_number=1, hd=True
        )
        self.search_results_for_anime = self.nzb_geek.get_nzb_search_results(
            self.anime_record, season_number=1, episode_number=15, anime=True,
            hd=False
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

    def test_get_audio_tracks_for_anime(self):
        search_result = self.search_results_for_anime[3]
        self.assertTrue(search_result.audio_tracks)
        self.assertTrue('Japanese' in search_result.audio_tracks)

    def test_str_method_for_episode(self):
        search_result = self.search_results_for_zoo_show[0]
        self.assertEqual(
            'The.Secret.Life.of.the.Zoo-S10E01-Extraordinary.Births.HDTV-720p, TV > HD',
            search_result.__str__(),
        )


class TestDownloadEpisode(TestCase):
    def setUp(self):
        self.nzb_geek = NZBGeek()
        self.nzb_geek.login()
        self.zoo_show_record = Show.objects.create(title='The Secret Life of the Zoo', gid='306705')
        self.zoo_show_record.save()
        self.zoo_show_episode = Episode.objects.create(
            show=self.zoo_show_record,
            season_number=10,
            episode_number=6,
            title='Episode 6',
            on_disk=False,
        )

    def tearDown(self):
        self.zoo_show_record.delete()
        self.zoo_show_episode.delete()

    def test_download_episode(self):
        request = Mock()
        request.META = {'HTTP_REFERER': 'http://127.0.0.1:8000/shows/52?page=1'}
        download_episode(request, self.zoo_show_record.id, self.zoo_show_episode.id)
        sleep(5)

        log_path = '\\'.join(NZBGET_NZB_DIR.split('\\')[:-1]) + '\\nzbget.log'

        with open(log_path, 'r') as f:
            log_contents = f.read()

        latest_log_contents = log_contents.split('\n')[-50:]
        latest_log_contents = '\n'.join(latest_log_contents)

        assert 'The.Secret.Life.of.the.Zoo-S10E06-Episode.6.WEBDL-1080p' in latest_log_contents
        return


class TestNZBGet(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_and_update_history(self):
        download_records = Download.objects.all()
        assert len(download_records) == 0
        NZBGet().get_and_update_history()
        download_records = Download.objects.all()
        assert len(download_records) > 0
