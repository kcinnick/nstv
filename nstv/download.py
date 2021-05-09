import os
import re
from glob import glob

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
            "password": os.getenv('NZBGEEK_PASSWORD')
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
        """
        Searches and downloads the first result on NZBGeek for the given
        show and episode number. After the file is downloaded, it is moved
        to the directory specified in nzbget's Settings -> Path -> NzbDir
        for downloading and post-processing.
        @param show:  object representing the show the episode belongs to.
        @param season_number:  int
        @param episode_number:  int
        @return:
        """
        print(f"\nSearching for {show.title} S{season_number} E{episode_number}")
        url = f'https://nzbgeek.info/geekseek.php?tvid={show.gid}'
        url += f'&season=S{str(season_number).zfill(2)}'
        url += f'&episode=E{str(episode_number).zfill(2)}'
        r = self.session.get(url)
        print(url)

        soup = BeautifulSoup(r.content, 'html.parser')
        first_download_link = soup.find('a', attrs={'title': 'Download NZB'})
        if first_download_link:
            first_download_link = first_download_link.get('href')
        else:
            raise AttributeError

        import webbrowser
        webbrowser.open(first_download_link)
        from time import sleep
        #  wait until file is downloaded
        nzb_files = glob('/home/nick/Downloads/*.nzb')
        while len(nzb_files) == 0:
            sleep(1)
            nzb_files = glob('/home/nick/Downloads/*.nzb')
        print('\nNZB file downloaded.')

        for file in nzb_files:
            file_name = file.split("/")[-1]
            dest_path = f'/home/nick/PycharmProjects/nstv/nzbs/{file_name}'
            os.rename(file, f'/home/nick/PycharmProjects/nstv/nzbs/{file_name}')
            print(f"{file_name} moved to {dest_path}.")
