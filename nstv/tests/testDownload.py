import os
import re
from unittest.mock import Mock
from time import sleep

import pytest
from bs4 import BeautifulSoup
from django.http import HttpRequest
from django.test import TestCase
from django.contrib import messages

from nstv.download import NZBGeek, SearchResult, NZBGet
from nstv.models import Show, Episode, Movie, Download
from nstv.views import download_episode, download_movie

NZBGET_NZB_DIR = os.getenv("NZBGET_NZB_DIR")


class NZBGeekTestCase(TestCase):
    def setUp(self):
        # Create a record before each test
        self.zoo_show_record = Show.objects.create(title='The Secret Life of the Zoo')
        self.seinfeld_show_record = Show.objects.create(title='Seinfeld', gid='79169')
        self.movie_record = Movie.objects.create(name='Goldfinger')
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
        gid = self.nzb_geek.get_gid_for_show(self.zoo_show_record.title)
        self.assertEqual('306705', gid)

    def test_get_gid_for_nonexistent_show(self):
        gid = self.nzb_geek.get_gid_for_show('this show does not exist')
        self.assertIsNone(gid)

    def test_get_gid_for_show_with_name_replacement(self):
        gid = self.nzb_geek.get_gid_for_show('6ixtynin9')
        self.assertEqual('438170', gid)

    def test_get_gid_for_movie(self):
        gid = self.nzb_geek.get_gid_for_movie(self.movie_record)
        self.assertEqual('00058150', gid)

    def test_download_from_results(self):
        NZBGEEK_API_KEY = os.getenv("NZBGEEK_API_KEY")
        result_table = BeautifulSoup("""<table border=0 class=releases><tr><td style=width:280px valign=top><a href="?tvid=85284"title="View Show Page"style=text-decoration:none><img src=images/covers/tv/85284.jpg style=padding-top:15px;padding-left:15px class=overlay_poster></a><td valign=top><table border=0 style=padding:15px;width:100%><tr><td colspan=2><a href="?tvid=85284"title="View Show Page"style=text-decoration:none><span class=overlay_title>Saturday Kitchen</span></a><td style=width:150px;vertical-align:top rowspan=6><table border=0 style=width:100%;padding-right:10px;padding-left:10px><tr><td><center><table border=0 style=width:150px><tr><td style=text-align:center colspan=3><span class=overlay_text_bold>overall geek rating</span><tr><td style=width:20px rowspan=3> <td style=text-align:center><img src=images/ratings/rating_0.png style=width:150px;opacity:.3;display:none id=85284_rating_image_0 title="Overall Geek Rating: Not rated yet"><img src=images/ratings/rating_1.png style=width:150px;display:none id=85284_rating_image_1 title="Overall Geek Rating: 1/5 - My Eyes, they burn!"><img src=images/ratings/rating_2.png style=width:150px;display:none id=85284_rating_image_2 title="Overall Geek Rating: 2/5 - I’d like a refund please"><img src=images/ratings/rating_3.png style=width:150px id=85284_rating_image_3 title="Overall Geek Rating: 3/5 - After a couple it wasn’t so bad or did I fall asleep?"><img src=images/ratings/rating_4.png style=width:150px;display:none id=85284_rating_image_4 title="Overall Geek Rating: 4/5 - I’ll delete it if I need the space"><img src=images/ratings/rating_5.png style=width:150px;display:none id=85284_rating_image_5 title="Overall Geek Rating: 5/5 - It’s a keeper!"><br><table border=0 style=width:150px;border-collapse:collapse><tr><td style=text-align:center;width:36px;height:32px><span class=overlay_overall_geek_rating_on title="After a couple it wasn’t so bad or did I fall asleep?"><i class="fa-star fas"></i></span><td style=text-align:center;width:36px;height:32px><span class=overlay_overall_geek_rating_on title="After a couple it wasn’t so bad or did I fall asleep?"><i class="fa-star fas"></i></span><td style=text-align:center;width:36px;height:32px><span class=overlay_overall_geek_rating_on title="After a couple it wasn’t so bad or did I fall asleep?"><i class="fa-star fas"></i></span><td style=text-align:center;width:36px;height:32px><span class=overlay_overall_geek_rating_off title="After a couple it wasn’t so bad or did I fall asleep?"><i class="fa-star far"></i></span><td style=text-align:center;width:36px;height:32px><span class=overlay_overall_geek_rating_off title="After a couple it wasn’t so bad or did I fall asleep?"><i class="fa-star far"></i></span></table><span class=overlay_text_bold>(1 vote)</span><br><br><td style=width:20px id=85284_rating_clear_3 rowspan=3> <tr><td style=text-align:center id=85284_rating_clear_2><span class=overlay_text_bold>click a star to<br>rate this show!</span><tr><td style=text-align:center;height:32px><span class=overlay_text><table border=0 style=width:150px;border-collapse:collapse><tr><td style=text-align:center;width:36px;height:32px id=85284_rating_1><span class=overlay_member_geek_rating_on title="My Eyes, they burn!"onclick=member_85284_rating(1) style=display:inline id=85284_rating_1_icon_on><i class="fa-star fas"></i></span> <span class=overlay_member_geek_rating_off title="My Eyes, they burn!"onclick=member_85284_rating(1) style=display:none id=85284_rating_1_icon_off><i class="fa-star far"></i></span><td style=text-align:center;width:36px;height:32px id=85284_rating_2><span class=overlay_member_geek_rating_on title="I’d like a refund please"onclick=member_85284_rating(2) style=display:inline id=85284_rating_2_icon_on><i class="fa-star fas"></i></span> <span class=overlay_member_geek_rating_off title="I’d like a refund please"onclick=member_85284_rating(2) style=display:none id=85284_rating_2_icon_off><i class="fa-star far"></i></span><td style=text-align:center;width:36px;height:32px id=85284_rating_3><span class=overlay_member_geek_rating_on title="After a couple it wasn’t so bad or did I fall asleep?"onclick=member_85284_rating(3) style=display:inline id=85284_rating_3_icon_on><i class="fa-star fas"></i></span> <span class=overlay_member_geek_rating_off title="After a couple it wasn’t so bad or did I fall asleep?"onclick=member_85284_rating(3) style=display:none id=85284_rating_3_icon_off><i class="fa-star far"></i></span><td style=text-align:center;width:36px;height:32px id=85284_rating_4><span class=overlay_member_geek_rating_on title="I’ll delete it if I need the space"onclick=member_85284_rating(4) style=display:none id=85284_rating_4_icon_on><i class="fa-star fas"></i></span> <span class=overlay_member_geek_rating_off title="I’ll delete it if I need the space"onclick=member_85284_rating(4) id=85284_rating_4_icon_off><i class="fa-star far"></i></span><td style=text-align:center;width:36px;height:32px id=85284_rating_5><span class=overlay_member_geek_rating_on title="It’s a keeper!"onclick=member_85284_rating(5) style=display:none id=85284_rating_5_icon_on><i class="fa-star fas"></i></span> <span class=overlay_member_geek_rating_off title="It’s a keeper!"onclick=member_85284_rating(5) id=85284_rating_5_icon_off><i class="fa-star far"></i></span></table></span><tr id=85284_rating_clear_4><td style=height:15px colspan=3> </tr><script>function member_85284_rating(a){var d=a;$.ajax({type:"POST",url:"tooltips.php?rating_id=85284&uid=237439&type=tv&member_rating="+d,data:{action:"call_this"},success:function(a){a.match(/1/i)?$("#rating_added").fadeIn(1e3,function(){$("#rating_added").fadeOut(5e3)}):a.match(/2/i)?$("#rating_added_failed").fadeIn(1e3,function(){$("#rating_added_failed").fadeOut(5e3)}):a.match(/3/i)&&$("#rating_added_failed").fadeIn(1e3,function(){$("#rating_added_failed").fadeOut(5e3)})}})}</script></table></center></table><tr><td> <tr id=85284_rating_clear_1><td><table border=0 style=width:100%><tr><td colspan=2><span class=overlay_text>Weekend food show full of mouth-watering food, great chefs and celebrity guests.</span><tr><td colspan=2> <tr><td><table border=0><tr><td style=width:150px;vertical-align:top><span class=overlay_text_bold>Genres:</span><td><span class=overlay_text><a href="geekseek.php?c=5000&view=2&genre=Reality"title="View Reality shows"class=cover_text>Reality</a><font class=overlay_text>, </font><a href="geekseek.php?c=5000&view=2&genre=Food"title="View Food shows"class=cover_text>Food</a></span><tr><td style=width:100px;vertical-align:top><span class=overlay_text_bold>Cast:</span><td><span class=overlay_text><a href="geekseek.php?c=5000&view=2&actors=James Martin"title="View shows with James Martin"class=cover_text>James Martin</a><font class=overlay_text>, </font><a href="geekseek.php?c=5000&view=2&actors=Matt Tebbutt"title="View shows with Matt Tebbutt"class=cover_text>Matt Tebbutt</a><font class=overlay_text>, </font><a href="geekseek.php?c=5000&view=2&actors=Antony Worrall Thompson"title="View shows with Antony Worrall Thompson"class=cover_text>Antony Worrall Thompson</a><font class=overlay_text>, </font><a href="geekseek.php?c=5000&view=2&actors=Gregg Wallace"title="View shows with Gregg Wallace"class=cover_text>Gregg Wallace</a>, <a href="geekseek.php?tvid=85284"title="View show page for full cast"class=cover_text>more ...</a></span><tr><td style=width:100px;vertical-align:top><span class=overlay_text_bold>Airs:</span><td><span class=overlay_text>Saturday at 10:00</span><tr><td><span class=overlay_text_bold>Runtime:</span><td><span class=overlay_text>90 mins</span><tr><td style=width:100px;vertical-align:top><span class=overlay_text_bold>Network:</span><td><a href="geekseek.php?c=5000&view=2&network=BBC"title="View shows from BBC"class=cover_text>BBC</a><span class=overlay_text> - Continuing</span><tr><td><span class=overlay_text_bold>First Aired:</span><td><span class=overlay_text>2008-06-21</span><tr><td style=width:100px;vertical-align:top><span class=overlay_text_bold>Content:</span><td><span class=overlay_text>TV-MA</span><tr><td colspan=2> <tr><td><span class=overlay_text_bold>TV Maze Rating:</span><td><span class=overlay_text><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span><span class=overlay_stars><i class="fa-star fas"></i></span></span></table></table><tr><td> <tr><td><table><tr></table><tr><td> </table><tr><td style=padding-left:15px colspan=2><table border=0 class=releases_cover><tr class=releases_cover><td style=width:15px rowspan=2><input id=03797743cea031e37b7ff4effad8385f name=release_8792739 type=checkbox value=03797743cea031e37b7ff4effad8385f><td colspan=6><span class=releases_new title="New Release"><i class="fas fa-fire"></i></span><a href="geekseek.php?guid=03797743cea031e37b7ff4effad8385f"title="View Release"class=releases_title>Saturday.Kitchen.10.Feb.2024.1080p.HEVCsubs.BigJ0554</a><tr><td><table border=0><tr><td><div class="icon icon_nzb"><a href="https://api.nzbgeek.info/api?t=get&id=03797743cea031e37b7ff4effad8385f&apikey=NZBGEEK_API_KEY"title="Download NZB"class=releases_icons></a></div><td><a href="https://api.nzbgeek.info/api?t=get&id=03797743cea031e37b7ff4effad8385f&apikey=NZBGEEK_API_KEY"title="Download NZB"class=releases_icons><i class="fas fa-cloud-download-alt"></i></a><span class=releases_icons title="Add To Cart"onclick=release_8792739_cart() style=cursor:pointer><i class="fa fa-shopping-basket"></i></span><script>function release_8792739_cart(){$.ajax({type:"POST",url:"tooltips.php?c=1&r=release_8792739&d=237439",data:{action:"call_this"},success:function(a){a.match(/1/i)?$("#addtocart").fadeIn(1e3,function(){$("#addtocart").fadeOut(5e3)}):a.match(/2/i)?$("#addtocart_failed").fadeIn(1e3,function(){$("#addtocart_failed").fadeOut(5e3)}):a.match(/3/i)&&$("#addtocart_exists").fadeIn(1e3,function(){$("#addtocart_exists").fadeOut(5e3)})}})}</script><span class=releases_icons title="Report Release"onclick=report_overlay(8792739,237439)><i class="fas fa-flag"></i></span></table><td class=releases_category><a href="?c=5040&view=2"title="View TV > HD"class=releases_category_text>TV > HD</a><td class=releases_age><span class=releases_icon_text>2 hrs ago</span><td class=releases_size><span class=releases_icon_text>1.44 GB</span><td class=releases_files><span class=releases_icon_text>36</span> <span class=releases_icons_stats_no><i class="far fa-file"></i></span><td class=releases_grabs><table border=0 style=width:100%><tr><td class=releases_grabs_icons_grab><span class=releases_icon_text>3</span> <span class=releases_icons_stats_no title=Downloads><i class="fas fa-download"style=color:#069></i></span><td class=releases_grabs_icons><span class=releases_icon_text>0</span> <span class=releases_icons_stats_no title=Comments><i class="far fa-comments"></i></span><td class=releases_grabs_icons><span class=releases_icon_text>0</span> <span class=releases_icons_stats title="Add Thumbs Up"onclick=release_8792739_thumb_up() style=cursor:pointer><i class="far fa-thumbs-up"></i></span><script>function release_8792739_thumb_up(){$.ajax({type:"POST",url:'tooltips.php?thumb=1&u=ntucker1111&i=237439&l=1&ld=&p=0&id=release_8792739&th=1"',data:{action:"call_this"},success:function(e){e.match(/1/i)?$("#thumb_up").fadeIn(1e3,function(){$("#thumb_up").fadeOut(5e3)}):e.match(/2/i)?$("#thumb_down").fadeIn(1e3,function(){$("#thumb_down").fadeOut(5e3)}):e.match(/3/i)?$("#thumb_up_exisits").fadeIn(1e3,function(){$("#thumb_up_exisits").fadeOut(5e3)}):e.match(/4/i)?$("#thumb_down_exisits").fadeIn(1e3,function(){$("#thumb_down_exisits").fadeOut(5e3)}):e.match(/5/i)?$("#thumb_up_removed").fadeIn(1e3,function(){$("#thumb_up_removed").fadeOut(5e3)}):e.match(/6/i)?$("#thumb_down_removed").fadeIn(1e3,function(){$("#thumb_down_removed").fadeOut(5e3)}):e.match(/7/i)&&$("#thumb_failed").fadeIn(1e3,function(){$("#thumb_failed").fadeOut(5e3)})}})}</script><td class=releases_grabs_icons><span class=releases_icon_text>0</span> <span class=releases_icons_stats title="Add Thumbs Down"onclick=release_8792739_thumb_down() style=cursor:pointer><i class="far fa-thumbs-down"></i></span><script>function release_8792739_thumb_down(){$.ajax({type:"POST",url:'tooltips.php?thumb=1&u=ntucker1111&i=237439&l=1&ld=&p=0&id=release_8792739&th=1"',data:{action:"call_this"},success:function(e){e.match(/1/i)?$("#thumb_up").fadeIn(1e3,function(){$("#thumb_up").fadeOut(5e3)}):e.match(/2/i)?$("#thumb_down").fadeIn(1e3,function(){$("#thumb_down").fadeOut(5e3)}):e.match(/3/i)?$("#thumb_up_exisits").fadeIn(1e3,function(){$("#thumb_up_exisits").fadeOut(5e3)}):e.match(/4/i)?$("#thumb_down_exisits").fadeIn(1e3,function(){$("#thumb_down_exisits").fadeOut(5e3)}):e.match(/5/i)?$("#thumb_up_removed").fadeIn(1e3,function(){$("#thumb_up_removed").fadeOut(5e3)}):e.match(/6/i)?$("#thumb_down_removed").fadeIn(1e3,function(){$("#thumb_down_removed").fadeOut(5e3)}):e.match(/7/i)&&$("#thumb_failed").fadeIn(1e3,function(){$("#thumb_failed").fadeOut(5e3)})}})}</script></table></table>""".replace('NZBGEEK_API_KEY', NZBGEEK_API_KEY), 'html.parser')
        fake_result = SearchResult(
            result_table=result_table,
        )
        fake_result.download_url = 'https://api.nzbgeek.info/api?t=get&id=c5aa16e660e438270756004d78c1c33e&apikey={}'.format(
            NZBGEEK_API_KEY)
        with self.settings(
                MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage"
        ):
            request = HttpRequest()
            request._messages = messages.storage.default_storage(request)
            self.nzb_geek.download_from_results([fake_result], request=request)

    def test_download_from_results_empty_result_set_does_not_cause_failure(self):
        empty_result_set = []
        with self.settings(
                MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage"
        ):
            request = HttpRequest()
            request._messages = messages.storage.default_storage(request)
            self.nzb_geek.download_from_results(empty_result_set, request=request)

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

        assert 'The.Secret.Life.of.the.Zoo' in latest_log_contents
        return


class TestDownloadMovie(TestCase):
    def setUp(self):
        self.nzb_geek = NZBGeek()
        self.nzb_geek.login()
        self.movie_record = Movie.objects.create(name='Goldfinger')
        self.movie_record.save()

    def tearDown(self):
        self.movie_record.delete()

    def test_download_movie(self):
        request = Mock()
        request.META = {}
        download_movie(request, self.movie_record.id)
        sleep(5)


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
