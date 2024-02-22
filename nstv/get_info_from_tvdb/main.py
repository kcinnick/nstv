import os
import django
from pprint import pprint
import tvdb_v4_official

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.models import Show, Episode

TVDB_ALIAS = {
    # tvdb title: django title
    '6ixtynin9 The Series': '6ixtynin9',
    "Little Shark's Day Out": "Little Shark's Outings",
    "Into the Wild Colombia": "Into the Wild: Colombia",
    "This Week on the Farm": "This Week On The Farm",
    "The Great British Bake Off": "The Great British Baking Show",
    "Inside Culture": "Inside Culture with Mary Beard",
    "Chateau DIY Living the Dream": "Château DIY",
}

SEASON_TITLE_REPLACEMENTS = {
    # sometimes the season ordering is different from TVDB to NZBGeek.
    # When this happens, we can use the below dict to map the episode correctly.
    'Running Man': {
        'S2010': 'S01',
        'S2011': 'S01',
        'S2012': 'S01',
        'S2013': 'S01',
        'S2014': 'S01',
        'S2015': 'S01',
    }
}

EPISODE_TITLE_REPLACEMENTS = {
    'Running Man': {
        'S01': {
            'Times Square': 'Times Square Mall',
            'Namsan Tower': 'N Seoul Tower',
            'Seoul Museum of History, Gyeonghui Palace': 'Seoul Museum of History and Gyeonghui Palace'
        }
    }
}


def find_tvdb_record_for_series(tvdb_api, series_name):
    print(series_name)
    items = tvdb_api.search(query=series_name, type='series', language='eng')
    if len(items) == 0:
        items = tvdb_api.search(query=TVDB_ALIAS[series_name], type='series', language='eng')
    for i in items:
        translations = i.get('translations')
        try:
            englishTranslation = translations['eng']
        except KeyError:
            print('No english translation found for {}'.format(i['name']))
            continue
        if englishTranslation == series_name:
            print(33)
            # update Show record with tvdb id
            show = Show.objects.get(title=series_name)
            print(show)
            show.tvdb_id = i['id']
            show.save()
            return i
        elif englishTranslation in TVDB_ALIAS.keys():
            print(36)
            if TVDB_ALIAS[englishTranslation] == series_name:
                # update Show record with tvdb id
                show = Show.objects.get(title=series_name)
                print(show)
                show.tvdb_id = i['id']
                show.save()
                return i
            elif TVDB_ALIAS[englishTranslation] == series_name.replace(' the ', ' The '):
                print(45)
                # update Show record with tvdb id
                show = Show.objects.get(title=series_name)
                print(show)
                show.tvdb_id = i['id']
                show.save()
                return i
            elif englishTranslation == series_name.replace(' the ', ' The '):
                print(58)
                show = Show.objects.get(title=series_name)
                print(show)
                show.tvdb_id = i['id']
                show.save()
                return i
            else:
                print(64)
                print(f"{englishTranslation} != {series_name}")
                quit()
        else:
            print(71)
            print(f"{englishTranslation} != {series_name}")
            if englishTranslation == TVDB_ALIAS.get(series_name):
                print(74)
                show = Show.objects.get(title=series_name)
                print(show)
                show.tvdb_id = i['id']
                show.save()
                return i
            else:
                print(80)
                print(f"{englishTranslation} != {TVDB_ALIAS.get(series_name)}")

    raise Exception('No match found.')


def main(show_id=None):
    tvdb = tvdb_v4_official.TVDB(os.getenv('TVDB_API_KEY'))
    shows_to_skip = [
        'Fantastic Foxes: Their Secret World',  # no tvdb record
    ]
    if show_id:
        shows = Show.objects.get(id=show_id)
        shows = [shows]
    else:
        shows = Show.objects.all()
    for show in shows:
        if show.title in shows_to_skip:
            continue
        print('Searching for episodes for {}'.format(show.title))
        nstv_episodes = Episode.objects.filter(show=show)
        # print(show.episodes)
        # print(show)
        show_title = show.title
        tvdb_record = find_tvdb_record_for_series(tvdb, show_title)
        # print(tvdb_record)
        tvdb_series = tvdb.get_series(tvdb_record['id'].split('-')[1])
        show.tvdb_id = tvdb_series['id']
        show.save()
        # print(tvdb_series)
        # add pagination until 0 episodes are found
        page = 0
        all_tvdb_series_episodes = []
        while True:
            tvdb_series_episodes = tvdb.get_series_episodes(tvdb_series['id'], lang='eng', page=page)['episodes']
            all_tvdb_series_episodes.extend(tvdb_series_episodes)
            if len(tvdb_series_episodes) != 500:
                break
            else:
                page += 1
        for tvdb_episode_listing in all_tvdb_series_episodes:
            if tvdb_episode_listing['seasonNumber'] == 0:
                continue
            if show_title in SEASON_TITLE_REPLACEMENTS:
                tvdb_episode_listing['seasonNumber'] = SEASON_TITLE_REPLACEMENTS[show_title]['S' + str(tvdb_episode_listing['seasonNumber'])]
            else:
                print(f'Show title {show_title} not in SEASON_TITLE_REPLACEMENTS.')
            match = False
            # print('---')
            # print(str(tvdb_episode_listing).encode('utf-8'))
            if show_title in EPISODE_TITLE_REPLACEMENTS:
                if str(tvdb_episode_listing['seasonNumber']) in EPISODE_TITLE_REPLACEMENTS[show_title]:
                    if tvdb_episode_listing['name'] in EPISODE_TITLE_REPLACEMENTS[show_title][str(tvdb_episode_listing['seasonNumber'])]:
                        tvdb_episode_listing['name'] = EPISODE_TITLE_REPLACEMENTS.get(show_title)[str(tvdb_episode_listing['seasonNumber'])][tvdb_episode_listing['name']]
            for nstv_episode in nstv_episodes:
                # print('Checking if {} == {}'.format(nstv_episode.title, tvdb_episode_listing['name']))
                if nstv_episode.title == tvdb_episode_listing['name']:
                    print('Matched {}.'.format(nstv_episode.title, tvdb_episode_listing['name']))
                    nstv_episode.season_number = str(tvdb_episode_listing['seasonNumber']).replace('S', '')
                    nstv_episode.episode_number = tvdb_episode_listing['number']
                    nstv_episode.air_date = tvdb_episode_listing['aired']
                    nstv_episode.tvdb_id = tvdb_episode_listing['id']
                    nstv_episode.save()
                    match = True
                    break
            if not match:
                print('No match found for {}'.format(tvdb_episode_listing['name']))
                if tvdb_episode_listing['name'] is None:
                    continue
                print('Creating episode for {}'.format(tvdb_episode_listing['name']))
                if 'S' in str(tvdb_episode_listing['seasonNumber']):
                    tvdb_episode_listing['seasonNumber'] = tvdb_episode_listing['seasonNumber'].replace('S', '')
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
