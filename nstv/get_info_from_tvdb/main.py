import os
import django
from datetime import datetime
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
    """
    Find TVDB record for a series by searching and matching across multiple fields.
    
    Matching priority:
    1. Exact match in English translation
    2. Match in TVDB_ALIAS mappings
    3. Match in any translation (any language)
    4. Match in aliases list
    5. If only one result, accept it with logging
    """
    print(f'Searching TVDB for: {series_name}')
    
    # Try direct search first
    items = tvdb_api.search(query=series_name, type='series', language='eng')
    
    # If no results and series has an alias, try that
    if len(items) == 0 and series_name in TVDB_ALIAS:
        print(f'No direct results, trying alias: {TVDB_ALIAS[series_name]}')
        items = tvdb_api.search(query=TVDB_ALIAS[series_name], type='series', language='eng')
    
    if len(items) == 0:
        raise Exception(f'No TVDB results found for "{series_name}"')
    
    # Normalize series name for comparison
    series_name_lower = series_name.lower()
    series_name_normalized = series_name.replace(' the ', ' The ')
    
    for i in items:
        translations = i.get('translations', {})
        aliases = i.get('aliases', [])
        
        # Get English translation (if available)
        english_translation = translations.get('eng')
        if not english_translation:
            print(f'Warning: No English translation for {i.get("name")}')
            continue
        
        # Priority 1: Exact match with English translation
        if english_translation == series_name or english_translation == series_name_normalized:
            print(f'✓ Matched via English translation: "{english_translation}"')
            show = Show.objects.get(title=series_name)
            show.tvdb_id = i['id']
            show.save()
            return i
        
        # Priority 2: Match via TVDB_ALIAS
        if english_translation in TVDB_ALIAS and TVDB_ALIAS[english_translation] == series_name:
            print(f'✓ Matched via TVDB_ALIAS: "{english_translation}" -> "{series_name}"')
            show = Show.objects.get(title=series_name)
            show.tvdb_id = i['id']
            show.save()
            return i
        
        if series_name in TVDB_ALIAS and TVDB_ALIAS[series_name] == english_translation:
            print(f'✓ Matched via TVDB_ALIAS reverse: "{series_name}" -> "{english_translation}"')
            show = Show.objects.get(title=series_name)
            show.tvdb_id = i['id']
            show.save()
            return i
        
        # Priority 3: Match in any translation (any language)
        for lang_code, translation in translations.items():
            if translation and translation.lower() == series_name_lower:
                print(f'✓ Matched via {lang_code} translation: "{translation}"')
                show = Show.objects.get(title=series_name)
                show.tvdb_id = i['id']
                show.save()
                return i
        
        # Priority 4: Match in aliases
        for alias in aliases:
            if alias and alias.lower() == series_name_lower:
                print(f'✓ Matched via alias: "{alias}"')
                show = Show.objects.get(title=series_name)
                show.tvdb_id = i['id']
                show.save()
                return i
    
    # Priority 5: If only one result and no exact match, accept it with logging
    if len(items) == 1:
        result = items[0]
        english_translation = result.get('translations', {}).get('eng', result.get('name'))
        print(f'⚠ Only one TVDB result found - auto-matching:')
        print(f'  Search term: "{series_name}"')
        print(f'  TVDB title: "{english_translation}"')
        print(f'  TVDB ID: {result.get("id")}')
        print(f'  Available translations: {list(result.get("translations", {}).values())}')
        print(f'  Aliases: {result.get("aliases", [])}')
        
        show = Show.objects.get(title=series_name)
        show.tvdb_id = result['id']
        show.save()
        return result
    
    # No match found
    print(f'✗ No match found for "{series_name}" among {len(items)} results:')
    for idx, item in enumerate(items[:5], 1):
        eng_title = item.get('translations', {}).get('eng', item.get('name'))
        print(f'  {idx}. {eng_title} (ID: {item.get("id")})')
    
    raise Exception(f'No match found for "{series_name}". Please add to TVDB_ALIAS or verify the title.')


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
        
        # Update show metadata from TVDB
        show.tvdb_id = tvdb_series['id']
        
        # Populate extended metadata fields
        if tvdb_series.get('overview'):
            show.overview = tvdb_series['overview']
        
        if tvdb_series.get('firstAired'):
            try:
                show.first_aired = datetime.strptime(tvdb_series['firstAired'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if tvdb_series.get('status'):
            # TVDB status can be: Continuing, Ended, Upcoming
            show.status = tvdb_series['status'].get('name') if isinstance(tvdb_series['status'], dict) else tvdb_series['status']
        
        if tvdb_series.get('originalNetwork'):
            show.network = tvdb_series['originalNetwork']
        
        if tvdb_series.get('genres'):
            # genres is a list of genre objects or strings
            genres = []
            for genre in tvdb_series['genres']:
                if isinstance(genre, dict):
                    genres.append(genre.get('name', ''))
                else:
                    genres.append(str(genre))
            show.genre = [g for g in genres if g]  # Remove empty strings
        
        if tvdb_series.get('image'):
            # image is typically the full URL to the poster
            show.poster_url = tvdb_series['image']
        
        # Note: Skipping score/rating for now as TVDB's score is not a 0-10 rating
        # but rather a popularity score that can be very large (thousands)
        # if tvdb_series.get('score'):
        #     try:
        #         show.rating = round(float(tvdb_series['score']), 1)
        #     except (ValueError, TypeError):
        #         pass
        
        show.save()
        print(f'Updated metadata for {show.title}')

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
