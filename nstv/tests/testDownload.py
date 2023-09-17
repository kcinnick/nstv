from nstv.download import NZBGeek
from nstv.models import Episode, Show


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
