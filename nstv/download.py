import os
import re

from bs4 import BeautifulSoup
import requests

from nstv.models import Show, Episode
from nstv.nstv import get_db_session


class NZBGeek:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'https://github.com/kcinnick/nstv'})

    def login(self):
        # get nzbgeek csrf token
        r = self.session.get('https://nzbgeek.info/logon.php')
        random_thing = re.search(
            '<input type="hidden" name="random_thing" id="random_thing" value="(\w+)">',
            str(r.content)
        ).group(1)
        # login to nzbgeek
        nzbgeek_login_url = 'https://nzbgeek.info/logon.php'
        login_payload = {
            "logon": "logon",
            "random_thing": random_thing,
            "username": os.getenv('NZBGEEK_USERNAME'),
            "password": os.getenv('GEEK_KEY')
        }
        self.session.post(nzbgeek_login_url, login_payload)
        r = self.session.get('https://nzbgeek.info/dashboard.php')
        assert os.getenv('NZBGEEK_USERNAME') in str(r.content)

    @staticmethod
    def search_nzbgeek_for_episode(episode):
        db_session = get_db_session()
        show = db_session.query(Show).where(episode.show_id == Show.id).first()
        return show

    def get_nzb(self, show, season_number, episode_number):
        db_session = get_db_session()
        url = f'https://nzbgeek.info/geekseek.php?tvid={show.gid}'
        url += f'&season=S{str(season_number).zfill(2)}'
        url += f'&episode=E{str(episode_number).zfill(2)}'
        r = self.session.get(url)
        print(url)

        soup = BeautifulSoup(r.content, 'html.parser')
        first_download_link = soup.find('a', attrs={'title': 'Download NZB'}).get('href')
        print(first_download_link)
        r = self.session.get(first_download_link)
        print('\nNZB file downloaded.')
