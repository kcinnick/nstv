import os
import django
from pprint import pprint
import tvdb_v4_official
import re
from django.db.models import Count

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
    "Girl From Nowhere": "Girl from Nowhere"
}

SEASON_TITLE_REPLACEMENTS = {
    # sometimes the season ordering is different from TVDB to NZBGeek.
    # When this happens, we can use the below dict to map the episode correctly.
    'Running Man': {
        'S2010': 'S01',
        'S2011': 'S02',
        'S2012': 'S03',
        'S2013': 'S04',
        'S2014': 'S05',
        'S2015': 'S06',
        'S2016': 'S07',
        'S2017': 'S08',
        'S2018': 'S09',
        'S2019': 'S10',
        'S2020': 'S11',
        'S2021': 'S12',
        'S2022': 'S13',
        'S2023': 'S14',
        'S2024': 'S15',
    }
}

EPISODE_TITLE_REPLACEMENTS = {
    'Running Man': {
        'S01': {
            # TVDB episode name: Plex episode name
            'Times Square': 'Times Square Mall',
            'Namsan Tower': 'N Seoul Tower',
            'Seoul Museum of History, Gyeonghui Palace': 'Seoul Museum of History and Gyeonghui Palace',
            'Xi Wi City': 'Men vs Women',
            'Bucheon Museum Manhwa Information Center': 'Museum Comics Information Center',
            'Nakwon Music Instruments Arcade': 'Nakwon Instruments Shopping Center',
            'Ansung Natural Resort': 'The Strongest Guest',
            'COEX Aquarium': 'Running Man Membership Training',
            'National Center for Korean Traditional Performing Arts': '1 vs 8',
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


def get_all_tvdb_episode_listings(tvdb, tvdb_series):
    page = 0
    all_tvdb_series_episodes = []
    while True:
        tvdb_series_episodes = tvdb.get_series_episodes(tvdb_series['id'], lang='eng', page=page)['episodes']
        all_tvdb_series_episodes.extend(tvdb_series_episodes)
        if len(tvdb_series_episodes) != 500:
            break
        else:
            page += 1

    return all_tvdb_series_episodes


def _normalize_title(title):
    if not title:
        return ''
    return re.sub(r'[^a-z0-9]+', '', str(title).lower())


def _to_int(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    value_str = str(value)
    match = re.search(r"(\d+)", value_str)
    if match:
        return int(match.group(1))
    return None


def _resolve_tvdb_season_number(show_title, season_name_or_number):
    if season_name_or_number == 0:
        return 0

    if show_title in SEASON_TITLE_REPLACEMENTS:
        replacement_key = f"S{season_name_or_number}"
        mapped = SEASON_TITLE_REPLACEMENTS[show_title].get(replacement_key, season_name_or_number)
        return _to_int(mapped)

    return _to_int(season_name_or_number)


def upsert_episode_from_tvdb_listing(show, tvdb_episode_listing, show_title):
    episode_title = tvdb_episode_listing.get('name')
    if episode_title is None:
        return None, False

    tvdb_episode_id = tvdb_episode_listing.get('id')
    season_raw = tvdb_episode_listing.get('seasonName') or tvdb_episode_listing.get('seasonNumber')
    season_number = _resolve_tvdb_season_number(show_title, season_raw)
    episode_number = _to_int(tvdb_episode_listing.get('number'))

    existing_episode = None

    if tvdb_episode_id:
        existing_episode = Episode.objects.filter(show=show, tvdb_id=tvdb_episode_id).first()

    if not existing_episode and season_number is not None and episode_number is not None:
        existing_episode = Episode.objects.filter(
            show=show,
            season_number=season_number,
            episode_number=episode_number,
        ).first()

    if not existing_episode and season_number is not None:
        normalized_new_title = _normalize_title(episode_title)
        for candidate in Episode.objects.filter(show=show, season_number=season_number):
            if _normalize_title(candidate.title) == normalized_new_title:
                existing_episode = candidate
                break

    if existing_episode:
        existing_episode.title = episode_title
        existing_episode.season_number = season_number
        existing_episode.episode_number = episode_number
        existing_episode.air_date = tvdb_episode_listing.get('aired')
        if tvdb_episode_id:
            existing_episode.tvdb_id = tvdb_episode_id
        existing_episode.save()
        return existing_episode, False

    created_episode = Episode.objects.create(
        show=show,
        air_date=tvdb_episode_listing.get('aired'),
        title=episode_title,
        season_number=season_number,
        episode_number=episode_number,
        tvdb_id=tvdb_episode_id,
        on_disk=False,
    )
    return created_episode, True


def merge_duplicate_episodes_for_show(show):
    duplicate_groups = (
        Episode.objects.filter(show=show)
        .exclude(season_number__isnull=True)
        .exclude(episode_number__isnull=True)
        .values('season_number', 'episode_number')
        .annotate(total=Count('id'))
        .filter(total__gt=1)
    )

    for duplicate_group in duplicate_groups:
        season_number = duplicate_group['season_number']
        episode_number = duplicate_group['episode_number']
        episode_candidates = list(
            Episode.objects.filter(
                show=show,
                season_number=season_number,
                episode_number=episode_number,
            ).order_by('-on_disk', '-tvdb_id', 'id')
        )
        primary_episode = episode_candidates[0]
        duplicates = episode_candidates[1:]

        for duplicate in duplicates:
            if not primary_episode.on_disk and duplicate.on_disk:
                primary_episode.on_disk = True
            if not primary_episode.tvdb_id and duplicate.tvdb_id:
                primary_episode.tvdb_id = duplicate.tvdb_id
            if not primary_episode.air_date and duplicate.air_date:
                primary_episode.air_date = duplicate.air_date
            if (
                duplicate.title
                and (not primary_episode.title or primary_episode.title.lower().startswith('episode '))
                and not duplicate.title.lower().startswith('episode ')
            ):
                primary_episode.title = duplicate.title

            duplicate.delete()

        primary_episode.save()


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
        show_title = show.title
        tvdb_record = find_tvdb_record_for_series(tvdb, show_title)
        tvdb_series = tvdb.get_series(tvdb_record['id'].split('-')[1])
        show.tvdb_id = tvdb_series['id']
        show.save()

        all_tvdb_series_episodes = get_all_tvdb_episode_listings(tvdb, tvdb_series)

        for tvdb_episode_listing in all_tvdb_series_episodes:
            tvdb_episode_listing_season_name = tvdb_episode_listing.get('seasonName')
            if not tvdb_episode_listing_season_name:
                tvdb_episode_listing_season_name = tvdb_episode_listing.get('seasonNumber')
            if tvdb_episode_listing_season_name == 0:
                continue

            if show_title in EPISODE_TITLE_REPLACEMENTS:
                if str(tvdb_episode_listing_season_name) in EPISODE_TITLE_REPLACEMENTS[show_title]:
                    if tvdb_episode_listing['name'] in EPISODE_TITLE_REPLACEMENTS[show_title][
                        str(tvdb_episode_listing_season_name)]:
                        tvdb_episode_listing['name'] = \
                        EPISODE_TITLE_REPLACEMENTS.get(show_title)[str(tvdb_episode_listing_season_name)][
                            tvdb_episode_listing['name']]

            _, created = upsert_episode_from_tvdb_listing(show, tvdb_episode_listing, show_title)
            if created:
                print('Created episode for {}'.format(tvdb_episode_listing['name']).encode('utf-8'))

        merge_duplicate_episodes_for_show(show)
    return


if __name__ == '__main__':
    main(145)
