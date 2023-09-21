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



def test_download_from_results():
    nzb_geek = NZBGeek()
    nzb_geek.login()
    unparsed_html = """<table class="releases" border="0">
        <tbody><tr>
            <td rowspan="2" style="width: 15px;" class="releases_checkbox_release">
                <input type="checkbox" name="release_5394775" value="067bb13a748c14fcf5f5b9aad6b8f44c" id="067bb13a748c14fcf5f5b9aad6b8f44c">
            </td>
                        
            <td colspan="6">
                <span title="New Release" class="releases_new"><i class="fas fa-fire"></i></span><a class="releases_title" title="View Release" href="geekseek.php?guid=067bb13a748c14fcf5f5b9aad6b8f44c">Neon.Genesis.Evangelion.S01E26.Take.Care.of.Yourself.AAC5.1.1080p.Bluray.x265-SiQ</a>
            </td>
        </tr>
        <tr class="releases">
            <td>
                <table border="0">
                    <tbody><tr>
                        <td>
                            <div class="icon icon_nzb"><a title="Download NZB" class="releases_icons" href="https://api.nzbgeek.info/api?t=get&amp;id=067bb13a748c14fcf5f5b9aad6b8f44c&amp;apikey=mtxYKmvY5SYOV280ZjzX3RNwfIciqy5i"></a></div></td><td><a title="Download NZB" class="releases_icons" href="https://api.nzbgeek.info/api?t=get&amp;id=067bb13a748c14fcf5f5b9aad6b8f44c&amp;apikey=mtxYKmvY5SYOV280ZjzX3RNwfIciqy5i"><i class="fas fa-cloud-download-alt"></i></a><span title="Add To Cart" class="releases_icons" onclick="release_5394775_cart()" style="cursor: pointer;"><i class="fa fa-shopping-basket"></i></span>
                                            <script>
                                                function release_5394775_cart() {        
                                                    $.ajax({
                                                        type: "POST",
                                                        url: 'tooltips.php?c=1&r=release_5394775&d=237439',
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
                                        <span title="Report Release" onclick="report_overlay(5394775, 237439)" class="releases_icons"><i class="fas fa-flag"></i></span></td><td><span class="releases_title">|</span></td><td><span title="View Media Information" onclick="media_overlay(5394775)" class="releases_icons"><i class="fas fa-video"></i></span><span title="Subtitles: English - Japanese" class="releases_icons"><i class="fas fa-closed-captioning"></i></span><img class="releases_icons_flag" title="Audio Language: English" src="images/flags/english.png">                            
                        </td>
                    </tr>
                </tbody></table>
            </td>
            <td class="releases_category">
                <a class="releases_category_text" title="View TV > Anime" href="geekseek.php?tvid=70350c=5070">TV &gt; Anime</a>
            </td>
            <td class="releases_age">
                <span class="releases_icon_text">9 mths ago</span>
            </td>    
            <td class="releases_size">
                <span class="releases_icon_text">908.76 MB</span>
            </td>
            <td class="releases_files">
                <span class="releases_icon_text">65</span>
                <span class="releases_icons_stats_no"><i class="far fa-file"></i></span>        
            </td>
            <td class="releases_grabs">
                <table style="width:100%;" border="0">
                    <tbody><tr>
                        <td class="releases_grabs_icons_grab">
                            <span class="releases_icon_text">980</span> <span title="Downloads" class="releases_icons_stats_no"><i style="color:#006699;" class="fas fa-download"></i></span>                        </td>
                        <td class="releases_grabs_icons">
                            <span class="releases_icon_text">0</span> <span title="Comments" class="releases_icons_stats_no"><i class="far fa-comments"></i></span> 
                        </td>    
                        <td class="releases_grabs_icons">
                            <span class="releases_icon_text">0</span> <span title="Add Thumbs Up" class="releases_icons_stats" onclick="release_5394775_thumb_up()" style="cursor: pointer;"><i class="far fa-thumbs-up"></i></span>
                                        <script>
                                            function release_5394775_thumb_up() {        
                                                $.ajax({
                                                    type: "POST",
                                                    url: 'tooltips.php?thumb=1&u=ntucker1111&i=237439&l=1&ld=&p=0&id=release_5394775',
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
                        
                            <span class="releases_icon_text">0</span> <span title="Add Thumbs Down" class="releases_icons_stats" onclick="release_5394775_thumb_down()" style="cursor: pointer;"><i class="far fa-thumbs-down"></i></span>
                                        <script>
                                            function release_5394775_thumb_down() {        
                                                $.ajax({
                                                    type: "POST",
                                                    url: 'tooltips.php?thumb=2&u=ntucker1111&i=237439&l=1&ld=&p=0&id=release_5394775',
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
                </tbody></table>
            </td>            
        </tr>
    </tbody></table>"""
    parsed_element = BeautifulSoup(unparsed_html, 'html.parser')
    search_result = SearchResult(parsed_element)
    nzb_geek.download_from_results([search_result])
    return
