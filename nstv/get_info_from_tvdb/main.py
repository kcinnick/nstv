import os
import django
from pprint import pprint
import tvdb_v4_official

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.models import Show, Episode

TVDB_ALIAS = {
    '6ixtynin9': '6ixtynin9 The Series'
}

def find_tvdb_record_for_series(tvdb_api, series_name):
    if series_name in TVDB_ALIAS:
        series_name = TVDB_ALIAS[series_name]
    items = tvdb_api.search(query=series_name, type='series', language='eng')
    print(items)
    for i in items:
        translations = i.get('translations')
        englishTranslation = translations['eng']
        if englishTranslation == series_name:
            return i
        else:
            print(f"{englishTranslation} != {series_name}")
    print('No match found.')
    raise Exception


def main():
    tvdb = tvdb_v4_official.TVDB(os.getenv('TVDB_API_KEY'))
    shows = Show.objects.get(title='6ixtynin9')
    shows = [shows]
    for show in shows:
        nstv_episodes = Episode.objects.filter(show=show)
        print(show.episodes)
        print(show)
        tvdb_record = find_tvdb_record_for_series(tvdb, show.title)
        print(tvdb_record)
        tvdb_series = tvdb.get_series(tvdb_record['id'].split('-')[1])
        tvdb_series_episodes = tvdb.get_series_episodes(tvdb_series['id'], lang='eng')
        tvdb_episode_listings = tvdb_series_episodes['episodes']
        for tvdb_episode_listing in tvdb_episode_listings:
            match = False
            print('---')
            print(tvdb_episode_listing)
            for nstv_episode in nstv_episodes:
                print('Checking if {} == {}'.format(nstv_episode.title, tvdb_episode_listing['name']))
                if nstv_episode.title == tvdb_episode_listing['name']:
                    print('Matched {} with {}'.format(nstv_episode.title, tvdb_episode_listing['name']))
                    match = True
                    break
            if not match:
                print('No match found for {}'.format(tvdb_episode_listing['name']))
                print('Creating episode for {}'.format(tvdb_episode_listing['name']))
                Episode.objects.create(
                    show=show,
                    air_date=tvdb_episode_listing['aired'],
                    title=tvdb_episode_listing['name'],
                    season_number=tvdb_episode_listing['seasonNumber'],
                    episode_number=tvdb_episode_listing['number'],
                    on_disk=False
                )
    return


if __name__ == '__main__':
    main()
