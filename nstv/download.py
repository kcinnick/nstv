import os
import re
from glob import glob

from bs4 import BeautifulSoup
import requests

from nstv.models import Show, Episode
from nstv.nstv import get_db_session


class SearchResult:
    def __init__(self, result_table):
        self.title = result_table.find('a', class_='releases_title').text.strip()
        self.category = result_table.find('a', class_='releases_category_text').text.strip()
        self.file_size = result_table.find('td', class_='releases_size').text.strip()
        self.download_url = result_table.find('a', attrs={'title': 'Download NZB'}).get('href')

    def __str__(self):
        return f"{self.title}, {self.category}"


class NZBGeek:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'https://github.com/kcinnick/nstv'})
        self.db_session = None

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

    def search_nzbgeek_for_episode(self, episode):
        if not self.db_session:
            self.db_session = get_db_session()

        show = self.db_session.query(Show).where(episode.show_id == Show.id).first()
        return show

    def get_gid(self, show_title):
        if not self.db_session:
            self.db_session = get_db_session()

        show = self.db_session.query(Show).where(Show.title == show_title).first()
        return

    def get_nzb(self, show, season_number, episode_number, hd=True):
        """
        Searches and downloads the first result on NZBGeek for the given
        show and episode number. After the file is downloaded, it is moved
        to the directory specified in nzbget's Settings -> Path -> NzbDir
        for downloading and post-processing.
        @param show:  object representing the show the episode belongs to.
        @param season_number:  int
        @param episode_number:  int
        @param hd:  bool, grabs only HD-categorized files if set to True
        @return:
        """
        print(f"\nSearching for {show.title} S{season_number} E{episode_number}")
        url = f'https://nzbgeek.info/geekseek.php?tvid={show.gid}'
        url += f'&season=S{str(season_number).zfill(2)}'
        url += f'&episode=E{str(episode_number).zfill(2)}'
        r = self.session.get(url)
        print(url)

        soup = BeautifulSoup(r.content, 'html.parser')
        results = soup.find_all('table', class_='releases')
        results = [SearchResult(i) for i in results]
        if hd:
            hd_results = [i for i in results if i.category == 'TV > HD']

        import webbrowser
        webbrowser.open(results[0].download_url)
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
