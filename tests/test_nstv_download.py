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
def test_searchresult():
    html = """
    	<table class="releases" border="0">
		<tr>
			<td rowspan="2" style="width: 15px;" class="releases_checkbox_release">
				<input type="checkbox" name="release_29871141" value="d2d4599a82d6bcdd95e1741b9488be5e" id="d2d4599a82d6bcdd95e1741b9488be5e">
			</td>

			<td colspan="6">
				<span title="New Release" class="releases_new"><i class="fas fa-fire"></i></span><a class="releases_title" title="View Release" href="geekseek.php?guid=d2d4599a82d6bcdd95e1741b9488be5e">Chopped.S06E12.Chefs.on.a.Mission.720p.HDTV.x264-W4F-Obfuscated</a>
			</td>
		</tr>
		<tr class="releases">
			<td>
				<table border="0">
					<tr>
						<td>
							<div class="icon icon_nzb"><a title="Download NZB" class="releases_icons" href="https://api.nzbgeek.info/api?t=get&id=d2d4599a82d6bcdd95e1741b9488be5e&apikey=IL6xrC3LBBfBQCRAPpsaNObqfmIkPeYp"></a></div></td><td><a title="Download NZB" class="releases_icons" href="https://api.nzbgeek.info/api?t=get&id=d2d4599a82d6bcdd95e1741b9488be5e&apikey=IL6xrC3LBBfBQCRAPpsaNObqfmIkPeYp"><i class="fas fa-cloud-download-alt"></i></a><span title="Add To Cart" class="releases_icons" onclick="release_29871141_cart()" style="cursor: pointer;"><i class="fa fa-shopping-basket"></i></span>
											<script>
												function release_29871141_cart() {
													$.ajax({
														type: "POST",
														url: 'tooltips.php?c=1&r=release_29871141&d=237439',
														data:{action:'call_this'},
														success:function(data) {
															if (data.match(/1/i)) {
																$("#addtocart").fadeIn(1000,function(){
																	$('#addtocart').fadeOut(5000);
																});
															}else if(data.match(/2/i)) {
																$("#addtocart_failed").fadeIn(1000,function(){
																	$('#addtocart_failed').fadeOut(5000);
																});
															}else if(data.match(/3/i)) {
																$("#addtocart_exists").fadeIn(1000,function(){
																	$('#addtocart_exists').fadeOut(5000);
																});
															};
														}
													});
												}
										</script>
										<span title="Report Release" onclick="report_overlay(29871141, 237439)" class="releases_icons"><i class="fas fa-flag"></i></span></td><td><span class="releases_title">|</span></td><td><span title="View Media Information" onclick="media_overlay(29871141)" class="releases_icons"><i class="fas fa-video"></i></span><img class="releases_icons_flag" title="Audio Language: English" src="images/flags/english.png">
						</td>
					</tr>
				</table>
			</td>
			<td class="releases_category">
				<a class="releases_category_text" title="View TV > HD" href="geekseek.php?tvid=85019c=5040">TV > HD</a>
			</td>
			<td class="releases_age">
				<span class="releases_icon_text">4 yrs ago</span>
			</td>
			<td class="releases_size">
				<span class="releases_icon_text">734.38 MB</span>
			</td>
			<td class="releases_files">
				<span class="releases_icon_text">54</span>
				<span class="releases_icons_stats_no"><i class="far fa-file"></i></span>
			</td>
			<td class="releases_grabs">
				<table style="width:100%;" border="0">
					<tr>
						<td class="releases_grabs_icons_grab">
							<span class="releases_icon_text">840</span> <span title="Downloads" class="releases_icons_stats_no"><i style="color:#006699;" class="fas fa-download"></i></span>						</td>
						<td class="releases_grabs_icons">
							<span class="releases_icon_text">0</span> <span title="Comments" class="releases_icons_stats_no"><i class="far fa-comments"></i></span>
						</td>
						<td class="releases_grabs_icons">
							<span class="releases_icon_text">0</span> <span title="Add Thumbs Up" class="releases_icons_stats" onclick="release_29871141_thumb_up()" style="cursor: pointer;"><i class="far fa-thumbs-up"></i></span>
										<script>
											function release_29871141_thumb_up() {
												$.ajax({
													type: "POST",
													url: 'tooltips.php?thumb=1&u=ntucker1111&i=237439&l=1&p=0&id=release_29871141',
													data:{action:'call_this'},
													success:function(data) {
														if (data.match(/1/i)) {
															$("#thumb_up").fadeIn(1000,function(){
																$('#thumb_up').fadeOut(5000);
															});
														}else if(data.match(/2/i)) {
															$("#thumb_down").fadeIn(1000,function(){
																$('#thumb_down').fadeOut(5000);
															});
														}else if(data.match(/3/i)) {
															$("#thumb_up_exisits").fadeIn(1000,function(){
																$('#thumb_up_exisits').fadeOut(5000);
															});
														}else if(data.match(/4/i)) {
															$("#thumb_down_exisits").fadeIn(1000,function(){
																$('#thumb_down_exisits').fadeOut(5000);
															});
														}else if(data.match(/5/i)) {
															$("#thumb_up_removed").fadeIn(1000,function(){
																$('#thumb_up_removed').fadeOut(5000);
															});
														}else if(data.match(/6/i)) {
															$("#thumb_down_removed").fadeIn(1000,function(){
																$('#thumb_down_removed').fadeOut(5000);
															});
														}else if(data.match(/7/i)) {
															$("#thumb_failed").fadeIn(1000,function(){
																$('#thumb_failed').fadeOut(5000);
															});
														};
													}
												});
											}
										</script>
															</td>
						<td class="releases_grabs_icons">

							<span class="releases_icon_text">0</span> <span title="Add Thumbs Down" class="releases_icons_stats" onclick="release_29871141_thumb_down()" style="cursor: pointer;"><i class="far fa-thumbs-down"></i></span>
										<script>
											function release_29871141_thumb_down() {
												$.ajax({
													type: "POST",
													url: 'tooltips.php?thumb=2&u=ntucker1111&i=237439&l=1&p=0&id=release_29871141',
													data:{action:'call_this'},
													success:function(data) {
														if (data.match(/1/i)) {
															$("#thumb_up").fadeIn(1000,function(){
																$('#thumb_up').fadeOut(5000);
															});
														}else if(data.match(/2/i)) {
															$("#thumb_down").fadeIn(1000,function(){
																$('#thumb_down').fadeOut(5000);
															});
														}else if(data.match(/3/i)) {
															$("#thumb_up_exisits").fadeIn(1000,function(){
																$('#thumb_up_exisits').fadeOut(5000);
															});
														}else if(data.match(/4/i)) {
															$("#thumb_down_exisits").fadeIn(1000,function(){
																$('#thumb_down_exisits').fadeOut(5000);
															});
														}else if(data.match(/5/i)) {
															$("#thumb_up_removed").fadeIn(1000,function(){
																$('#thumb_up_removed').fadeOut(5000);
															});
														}else if(data.match(/6/i)) {
															$("#thumb_down_removed").fadeIn(1000,function(){
																$('#thumb_down_removed').fadeOut(5000);
															});
														}else if(data.match(/7/i)) {
															$("#thumb_failed").fadeIn(1000,function(){
																$('#thumb_failed').fadeOut(5000);
															});
														};
													}
												});
											}
										</script>
															</td>
					</tr>
				</table>
			</td>
		</tr>
	</table>
"""

    soupified_html = BeautifulSoup(html, features='lxml')
    search_result = SearchResult(soupified_html)
    assert search_result.title == 'Chopped.S06E12.Chefs.on.a.Mission.720p.HDTV.x264-W4F-Obfuscated'
    assert search_result.category == 'TV > HD'
    assert search_result.file_size == '734.38 MB'
    assert search_result.download_url == 'https://api.nzbgeek.info/api?t=get&id=d2d4599a82d6bcdd95e1741b9488be5e&apikey=IL6xrC3LBBfBQCRAPpsaNObqfmIkPeYp'
    assert str(search_result) == f'{search_result.title}, {search_result.category}'

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
