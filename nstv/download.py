import os
import re
from glob import glob
from pathlib import Path
from time import sleep
from urllib.parse import quote_plus

import django
from django.contrib import messages
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .models import Movie, NZBDownload

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

SHOW_TITLE_REPLACEMENTS = {
    # sometimes the show title differs from what's on plex and
    # what is on nzbgeek. When this happens, we can use the below dict
    # to map the title on plex to the title on nzbgeek.
    # "title on plex": "title on nzbgeek"
    "6ixtynin9": "6ixtynin9 The Series",
    "Crash Course in Romance": "Crash Course In Romance",
    "Little Shark's Day Out": "Little Shark Outings",
    "Reno 911!": "Reno 911",
    "Château DIY": "Chateau DIY Living the Dream",
    "Welcome Back, Kotter": "Welcome Back Kotter",
    "Welcome to Samdal-ri": "Welcome to Samdalri",
    "The Twilight Zone": "The Twilight Zone (1959)",
    "Girl from Nowhere": "Girl From Nowhere",
    "Beachfront Bargain Hunt Renovation": "Beachfront Bargain Hunt: Renovation",
}

SEASON_TITLE_REPLACEMENTS = {
    # sometimes the season ordering is different from TVDB to NZBGeek.
    # When this happens, we can use the below dict to map the episode correctly.
    'Running Man': {
        'S2010': 'S01'
    }
}

NZBGET_NZB_DIR = os.getenv("NZBGET_NZB_DIR")

class NZBGet:
    def __init__(self):
        self.session = requests.Session()

    def save_nzb_download_record(self, result, status):
        nzb_download = NZBDownload.objects.all().filter(nzb_id=result['ID']).first()
        if not nzb_download:
            nzb_download = NZBDownload(
                nzb_id=result['ID'],
                title=result['NZBName'],
                status=status,
            )
            nzb_download.save()
            # print(f"Added {result['NZBName']} to failed downloads.")
        else:
            # print(f"{result['NZBName']} already exists in failed downloads.")
            pass

    def get_and_update_history(self):
        r = self.session.get('http://127.0.0.1:6789/jsonrpc/history?=false')
        results = r.json()['result']
        for result in results:
            status = result['Status']
            if 'FAILURE' in status:
                self.save_nzb_download_record(result, status)
            elif 'SUCCESS' in status:
                self.save_nzb_download_record(result, status)
            elif 'DELETED/' in status:
                self.save_nzb_download_record(result, status)
            elif 'WARNING' in status:
                self.save_nzb_download_record(result, status)
            else:
                print(f"Status for {result['NZBName']} is {status}.")
        return


class SearchResult:
    def __init__(self, result_table):
        if not result_table:
            return
        self.title = result_table.find("a", class_="releases_title")
        self.title = self.title.text.strip()
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
        self.audio_tracks = self.get_audio_tracks(result_table)

    def get_audio_tracks(self, result_table):
        audio_tracks = []
        releases_icons = result_table.find_all('img', class_='releases_icons_flag')
        for release_icon in releases_icons:
            audio_language_title = release_icon.attrs.get('title')
            if audio_language_title:
                audio_tracks.append(audio_language_title.replace('Audio Language: ', ''))

        return audio_tracks

    def __str__(self):
        return f"{self.title}, {self.category}"


class NZBGeek:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "https://github.com/kcinnick/nstv"})
        self.db_session = None
        self.logged_in = False

    def get_parsed_results(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        results = soup.find_all("table", class_="releases")
        parsed_results = [
            SearchResult(result)
            for result in results
            if result.find("a", class_="releases_title")
        ]
        return parsed_results

    def search_and_parse_results(self, url):
        print(f"\nRequesting {url}")
        url = quote_plus(url, safe=':/&=?')  # Replaces ' ' with '%20' and leaves other safe characters unchanged
        parsed_results = self.get_parsed_results(url)

        if not parsed_results and 'browsequality' in url:
            print("No results found for {}. Checking for all qualities.".format(url))
            url = url.split('&view=1&browsequality')[0]
            print(f"\nRequesting {url}")
            parsed_results = self.get_parsed_results(url)

        return parsed_results

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
                print('User is already logged in.')
                return
            else:  # pragma: no cover
                print('Random thing for login was missing but user is not already logged in.')
                print('This should never happen. Something is wrong.  Look at the stacktrace:')
                print('\nHTML Content:', r.content)
                raise e
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

    def get_gid_for_show(self, show_title):
        # print(show_title)
        print("get_gid: " + 'Getting GID for {}'.format(show_title))
        from .models import Show
        show = Show.objects.all().filter(title=show_title).first()

        if show_title in SHOW_TITLE_REPLACEMENTS.keys():
            show_title = SHOW_TITLE_REPLACEMENTS[show_title]
            print("get_gid: " + 'Replacing show title with {}'.format(show_title))

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
            result_title = result.find('span', class_='overlay_title').text.strip()
            # print(result)
            if result_title == show_title:
                show.gid = result.get('href').split('tvid=')[1]
                show.save()
                print("get_gid: " + 'Successfully updated GID for {}'.format(show_title))
                break
            else:
                print(f"download.py: {result.find('span', class_='overlay_title').text.strip()} != {show_title}")
                # check if titles don't match because of year at end
                year_in_title = re.search(r'\((\d{4})\)$', result_title)
                if year_in_title:
                    title_without_year = result_title[:year_in_title.start()].strip()
                    if title_without_year == show_title:
                        show.gid = result.get('href').split('tvid=')[1]
                        show.save()
                        print("get_gid: " + 'Successfully updated GID for {} after removing year.'.format(show_title))
                        break
                else:
                    print("get_gid: " + 'Moving to next result if any.'.format(show_title))

        return show.gid

    def get_gid_for_movie(self, movie):
        print("get_gid_for_movie: " + 'Getting GID for {}'.format(movie.name))
        movie = Movie.objects.all().filter(name=movie.name).first()

        url = "https://nzbgeek.info/geekseek.php?moviesgeekseek=1&c=2000&browseincludewords={}".format(
            movie.name
        ).replace(" ", "%20")
        print("get_gid_for_movie: " + url)
        r = self.session.get(url)

        soup = BeautifulSoup(r.content, "html.parser")
        geekseek_results = soup.find('div', class_='geekseek_results')
        if 'returned 0' in geekseek_results.text:
            print("get_gid_for_movie: " + 'No results found for {}'.format(movie.name))
            return

        releases_tables = soup.find_all("table", class_="releases")
        for releases_table in releases_tables:
            print('-------')
            print("Movie title: ", movie.name)
            releases_item = releases_table.find('td', class_='releases_item_release')
            if releases_item is None:
                print("get_gid_for_movie: " + 'No results found for {}'.format(movie.name))

            releases_item_title_text = releases_item.text.strip()
            movie.name = releases_item_title_text.replace(
                # NZBGeek removes the period after titles
                'Mr. ', 'Mr').replace('Mrs. ', 'Mrs').replace('Ms. ', 'Ms')

            if movie.name in releases_item_title_text:
                # TODO: add year check
                print("get_gid_for_movie: " + 'Found a match for {}'.format(movie.name))
                print(releases_item)
                movie.gid = releases_item.find('a', class_='geekseek_results').get('href').split('?movieid=')[1]
                movie.save()
                print("get_gid_for_movie: " + 'Successfully updated GID for {}'.format(movie.name))
                sleep(5)
                break
            else:
                print(f'{movie.name} not in {releases_item_title_text}')
                continue

        return movie.gid

    def get_nzb_search_results(
            self, show, season_number=None, episode_number=None,
            episode_title=None, hd=True, anime=False
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
        @param anime:  bool, grabs original audio language if set to True
        @return:
        """
        print(f"download.get_nzb_search_results: show.gid == {show.gid} for {show.title}")
        print("download.get_nzb_search_results: is anime is {}".format(anime))
        if not show.gid:
            show.gid = self.get_gid_for_show(show.title)
            if not show.gid:
                raise AttributeError(f"download.get_nzb_search_results: No GID found for {show.title}")
        print(f"show.gid == {show.gid} for {show.title}")
        if season_number == 0:
            url = f'https://nzbgeek.info/geekseek.php?tvid={show.gid}&season=S00&episode=all'
        elif season_number is not None:
            if show.title in SEASON_TITLE_REPLACEMENTS.keys():
                if f'{season_number}' in SEASON_TITLE_REPLACEMENTS[show.title].keys():
                    season_number = SEASON_TITLE_REPLACEMENTS[show.title][f'S{season_number}']
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
            else:
                # look up the season via tvdb + episode title
                url = f"https://nzbgeek.info/geekseek.php?moviesgeekseek=1&c=&browseincludewords={show.title} {episode_title}"
                print(f"\nSearching for {show.title} {episode_title} via URL: {url}")

        parsed_results = self.search_and_parse_results(url)

        if hd:
            results_to_remove = []
            # if hd is True, we want to remove the non-HD-categorized files
            print("download.get_nzb_search_results: Removing non-HD-categorized files.")
            for result in parsed_results.copy():
                if 'HD' in result.category:
                    pass
                else:
                    print(f"download.get_nzb_search_results: Removing {result.title} because it's not HD.")
                    results_to_remove.append(result)
            if len(results_to_remove) == len(parsed_results):
                print("download.get_nzb_search_results: No HD-categorized files found. Ignoring HD filter.")
            else:
                for result in results_to_remove:
                    parsed_results.remove(result)

        if anime:
            # if anime is True, we want to grab the original audio language
            # we determine if anime is True by checking if the plex show genres contain Anime/Animation.
            for result in parsed_results.copy():
                if 'English' in result.audio_tracks and len(result.audio_tracks) == 1:
                    print(f"download.get_nzb_search_results: Removing {result.title} because it's only in English.")
                    parsed_results.remove(result)
                else:
                    pass

        return parsed_results

    def get_nzb_search_results_for_movie(self, movie, quality=None):
        if not movie.gid:
            movie.gid = self.get_gid_for_movie(movie)
            if not movie.gid:
                raise AttributeError(f"download.get_nzb_search_results_for_movie: No GID found for {movie.name}")
        url = f"https://nzbgeek.info/geekseek.php?movieid={movie.gid}&browsestatsordervar=desc"
        if quality:
            url += f"&view=1&browsequality={quality}"

        parsed_results = self.search_and_parse_results(url)

        return parsed_results

    def download_from_results(self, results, request=None):
        """
        Download NZB files from search results and monitor progress in NZBGet.
        
        @param results: List of SearchResult objects to download
        @param request: Django request object (optional, for user feedback messages)
        """
        print("download.download_from_results: Downloading from results.")
        NZBGET_NZB_DIR = os.getenv("NZBGET_NZB_DIR")
        print("NZBGET_NZB_DIR: ", NZBGET_NZB_DIR)
        if not len(results):
            print("No results found.")
            if request:
                messages.warning(request, "No results found for download.")
            return
        else:
            print(f"Found {len(results)} results.")

        result_counter = 0
        for result in tqdm(results):
            result_counter += 1
            result.title = f"{result.title}_{result_counter}"
            print(f"Downloading {result.title} from {result.download_url}")
            r = self.session.get(result.download_url)
            
            # Write NZB file to Downloads folder
            download_path = f"{Path.home()}\\Downloads\\{result.title}.nzb"
            with open(download_path, "wb") as f:
                f.write(r.content)
            print(f"NZB file written to {download_path}")
            
            from time import sleep

            #  Wait until the specific file exists and has content
            tries = 0
            while tries < 10:  # Reduced from 60 to 10 tries
                if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
                    if request:
                        messages.info(request, f"\r{result.title} downloaded!")
                    print(f"\rNZB file downloaded successfully: {download_path}")
                    break
                else:
                    tries += 1
                    sleep(1)  # Reduced from 60s to 1s
                    print(f"\rWaiting for NZB file to be written... {tries}/10")
            
            if not os.path.exists(download_path):
                print(f"ERROR: Failed to download {download_path}. Skipping.")
                continue
            
            # Move the specific file to NZBGet directory
            file_name = f"{result.title}.nzb"
            dest_path = os.path.join(NZBGET_NZB_DIR, file_name)
            
            if os.path.exists(dest_path):
                print(f"File already exists at {dest_path}. Removing and replacing.")
                os.remove(dest_path)
            
            print(f'Moving {file_name} to {NZBGET_NZB_DIR}')
            os.rename(download_path, dest_path)
            print(f"{file_name} moved to {dest_path}.")

            # start monitoring download
            print(f"Starting to monitor NZBGet for {result.title}...")
            nzbget_api = NZBGet()
            monitoring_tries = 0
            max_monitoring_tries = 120  # 10 minutes (120 * 5 seconds)
            
            while monitoring_tries < max_monitoring_tries:
                try:
                    nzbget_api.get_and_update_history()
                except ConnectionError:
                    print('Connection to NZBGet failed. Please check that it\'s running.')
                    break
                except Exception as e:
                    print(f'Error connecting to NZBGet: {e}')
                    break
                    
                sleep(5)
                monitoring_tries += 1
                
                if NZBDownload.objects.all().filter(title=result.title).exists():
                    nzb_download = NZBDownload.objects.all().filter(title=result.title).first()
                    print(f"[{monitoring_tries * 5}s] {result.title} status: {nzb_download.status}")
                    
                    if 'FAILURE' in nzb_download.status:
                        print(f"FAILED: {result.title} has failed to download.")
                        break
                    elif 'SUCCESS' in nzb_download.status:
                        print(f"SUCCESS: {result.title} has successfully downloaded and processed.")
                        if request:
                            messages.success(request, f"{result.title} completed successfully!")
                        return
                    elif 'DELETED/' in nzb_download.status:
                        print(f"DELETED: {result.title} has been deleted from NZBGet.")
                        break
                    elif 'WARNING' in nzb_download.status:
                        print(f"WARNING: {result.title} completed with warnings.")
                        if request:
                            messages.warning(request, f"{result.title} completed with warnings.")
                        return
                    else:
                        # Still downloading/processing
                        if monitoring_tries % 6 == 0:  # Print status every 30 seconds
                            print(f"Status for {result.title}: {nzb_download.status}")
                else:
                    if monitoring_tries % 6 == 0:  # Print every 30 seconds
                        print(f"[{monitoring_tries * 5}s] {result.title} not yet in NZBGet history. Still queued or processing...")
                        
            if monitoring_tries >= max_monitoring_tries:
                print(f"TIMEOUT: Stopped monitoring {result.title} after {max_monitoring_tries * 5} seconds.")
                if request:
                    messages.warning(request, f"Monitoring timeout for {result.title}. Check NZBGet manually.")
            
            print(f'Monitoring completed for {result.title}')

        return
