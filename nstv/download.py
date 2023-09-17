import os
import re
import webbrowser
from glob import glob
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

import requests
from bs4 import BeautifulSoup

SHOW_TITLE_REPLACEMENTS = {
    # sometimes the show title differs from what's on plex and
    # what is on nzbgeek. When this happens, we can use the below dict
    # to map the title on plex to the title on nzbgeek.
    # "title on plex": "title on nzbgeek"
    "6ixtynin9": "6ixtyNin9 The Series"
}


class SearchResult:
    def __init__(self, result_table):
        self.title = result_table.find("a", class_="releases_title").text.strip()
        self.category = result_table.find(
            "a", class_="releases_category_text"
        ).text.strip()
        self.file_size = result_table.find("td", class_="releases_size").text.strip()
        self.download_url = result_table.find("a", attrs={"title": "Download NZB"}).get(
            "href"
        )
        grabs = result_table.find("td", class_='releases_grabs').text.strip().split()[
            0]  # list is of downloads, comments, thumbs-ups, and thumbs-downs
        self.grabs = grabs

    def __str__(self):
        return f"{self.title}, {self.category}"


class NZBGeek:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "https://github.com/kcinnick/nstv"})
        self.db_session = None
        self.logged_in = False

    def login(self):
        # get nzbgeek csrf token
        r = self.session.get("https://nzbgeek.info/logon.php")
        try:
            random_thing = re.search(
                r'<input type="hidden" name="random_thing" id="random_thing" value="(\w+)">',
                str(r.content),
            ).group(1)
        except AttributeError as e:
            #  occurs if user is already logged in
            if os.getenv('NZBGEEK_USERNAME') in str(r.content):
                return
            else:  # pragma: no cover
                print('Random thing for login was missing but user is not already logged in.')
                print('This should never happen. Something is wrong.  Look at the stacktrace:')
                print('\nHTML Content:', r.content)
                raise e
                #  until, (or if ever) the above occurs, we'll remove the noqa's above and test it accordingly.
                #  until then, unsure how to test it.
        # login to nzbgeek
        nzbgeek_login_url = "https://nzbgeek.info/logon.php"
        login_payload = {
            "logon": "logon",
            "random_thing": random_thing,
            "username": os.getenv("NZBGEEK_USERNAME"),
            "password": os.getenv("NZBGEEK_PASSWORD"),
        }
        self.session.post(nzbgeek_login_url, login_payload)
        r = self.session.get("https://nzbgeek.info/dashboard.php")
        assert os.getenv("NZBGEEK_USERNAME") in str(r.content)
        self.logged_in = True

    def get_gid(self, show_title):
        if show_title in SHOW_TITLE_REPLACEMENTS.keys():
            replacement = True
        else:
            replacement = False
        print(show_title)
        print("get_gid: " + 'Getting GID for {}'.format(show_title))
        from .models import Show
        if replacement:
            show = Show.objects.all().filter(title=show_title).first()
        else:
            show = Show.objects.all().filter(title=show_title).first()

        assert show  # raise failure if show doesn't appear to be in DB

        url = "https://nzbgeek.info/geekseek.php?moviesgeekseek=1&c=5000&browseincludewords={}".format(
            show_title
        ).replace(" ", "%20")
        print("get_gid: " + url)
        r = self.session.get(url)

        soup = BeautifulSoup(r.content, "html.parser")
        geekseek_results = soup.find('div', class_='geekseek_results')
        if 'returned 0' in geekseek_results.text:
            print("get_gid: " + 'No results found for {}'.format(show_title))
            return

        releases_tables = soup.find_all("table", class_="releases")
        for releases_table in releases_tables:
            release_table = releases_table.find('table')
            result = release_table.find('a', title='View Show Page')
            print(result)
            if result.find('span', class_='overlay_title').text.strip() == show_title:
                show.gid = result.get('href').split('tvid=')[1]
                show.save()
                print("get_gid: " + 'Successfully updated GID for {}'.format(show_title))
                break
            elif show_title in SHOW_TITLE_REPLACEMENTS.keys():
                show.gid = result.get('href').split('tvid=')[1]
                show.save()
                print("get_gid: " + 'Successfully updated GID for {}'.format(show_title))
                break
            else:
                print(f"download.py: {result.find('span', class_='overlay_title').text.strip()} != {show_title}")
                print("get_gid: " + 'Moving to next result if any.'.format(show_title))

        return show.gid

    def get_nzb(
            self, show, season_number=None, episode_number=None, episode_title=None, hd=True
    ):
        """
        Searches and downloads the first result on NZBGeek for the given
        show and episode number. After the file is downloaded, it is moved
        to the directory specified in nzbget's Settings -> Path -> NzbDir
        for downloading and post-processing.
        @param show:  object representing the show the episode belongs to.
        @param season_number:  int
        @param episode_number:  int
        @param episode_title:  str, optional. If given, searches via show and episode title.
        @param hd:  bool, grabs only HD-categorized files if set to True
        @return:
        """
        print("Season number: ", season_number)
        print("Episode number: ", episode_number)
        if not show.gid:
            show.gid = self.get_gid(show.title)
        print(f"show.gid == {show.gid} for {show.title}")
        if season_number:
            print(f"\nSearching for {show.title} S{season_number} E{episode_number}")
            url = f"https://nzbgeek.info/geekseek.php?tvid={show.gid}"
            url += f"&season=S{str(season_number).zfill(2)}"
            url += f"&episode=E{str(episode_number).zfill(2)}"
        else:
            if not episode_title:
                raise AttributeError(
                    "get_nzb needs either season_number & episode_number"
                    " or an episode title."
                )
            url = f"https://nzbgeek.info/geekseek.php?tvid={show.gid}"
            raise NotImplementedError
            # &season=S01&episode=E05

        r = self.session.get(url)
        print(f"\nRequesting {url}")

        soup = BeautifulSoup(r.content, "html.parser")
        results = soup.find_all("table", class_="releases")
        results = [SearchResult(i) for i in results]
        if hd:
            results = [i for i in results if i.category in ["TV > HD", 'TV > Anime']]

        # sort results by grabs

        if not len(results):
            print("No results found.")
            return
        webbrowser.open(results[0].download_url)
        from time import sleep

        #  wait until file is downloaded
        nzb_files = glob(f"{Path.home()}\\Downloads\\*.nzb")
        while len(nzb_files) == 0:
            sleep(1)
            nzb_files = glob(f"{Path.home()}\\Downloads\\*.nzb")
        print("\nNZB file downloaded.")

        for file in nzb_files:
            file_name = file.split("\\")[-1]
            dest_path = f"{Path.home()}\\PycharmProjects\\djangoProject\\nstv\\nzbs\\{file_name}"
            if not os.path.exists(dest_path):
                os.rename(file, dest_path)
            print(f"{file_name} moved to {dest_path}.")
        return
