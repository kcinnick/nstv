"""
Sync TV episodes from Plex to Django database.

This script connects to your Plex server and imports all episodes for existing shows,
marking them as on_disk=True. Handles special cases like non-standard season numbering
via SEASON_TITLE_REPLACEMENTS mapping.
"""
import os
import re
import sys
from pathlib import Path
from typing import Tuple, Optional

import django
from plexapi.server import PlexServer
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Show, Episode

# Mapping of Plex show title to Django show title
# Use this when Plex title differs from what's in Django
SHOW_ALIASES = {
    # Format: 'Plex Title': 'Django Title'
    '6ixtynin9 the Series': '6ixtynin9',
    "Beachfront Bargain Hunt Renovation": "Beachfront Bargain Hunt: Renovation",
}

# Mapping for non-standard season numbering
# Some shows (especially international) have seasons numbered by year or other schemes
SEASON_TITLE_REPLACEMENTS = {
    # Format: 'Show Title': {'PplexSeason': 'DjangoSeason', ...}
    'Running Man': {
        # Running Man uses year-based seasons (2010, 2011, etc)
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
    },
    'Lupin': {
        # Lupin has special season naming in Plex
        'Season 1 - Part 1 & 2': 'S01',
        'Season 2 - Part 3': 'S02'
    }
}


def get_plex_connection() -> PlexServer:
    """
    Connect to Plex server using credentials from environment variables.
    
    Returns:
        PlexServer: Connected Plex server instance
        
    Raises:
        ValueError: If required environment variables are missing
    """
    plex_api_key = os.getenv('PLEX_API_KEY')
    plex_server = os.getenv('PLEX_SERVER')
    
    if not plex_api_key or not plex_server:
        raise ValueError('Missing PLEX_API_KEY or PLEX_SERVER environment variables.')
    
    try:
        plex = PlexServer(plex_server, plex_api_key)
        print(f"✓ Connected to Plex server: {plex.friendlyName}")
        return plex
    except Exception as e:
        raise ValueError(f'Failed to connect to Plex server: {e}')


def _resolve_season_number(plex_show, plex_episode) -> int:
    """
    Resolve season number, handling special cases via SEASON_TITLE_REPLACEMENTS.
    
    Some shows have non-standard season numbering (e.g., Running Man uses years).
    This function maps those to standard S##format.
    
    Args:
        plex_show: Plex show object
        plex_episode: Plex episode object
        
    Returns:
        int: Resolved season number
    """
    show_replacements = SEASON_TITLE_REPLACEMENTS.get(plex_show.title)
    if not show_replacements:
        return int(plex_episode.seasonNumber)
    
    # Try to match by season name first
    season_name = getattr(plex_episode, 'seasonName', None)
    if season_name and season_name in show_replacements:
        replacement = show_replacements[season_name]
        # Extract number from S## format
        match = re.search(r'S(\d+)', replacement)
        return int(match.group(1)) if match else int(plex_episode.seasonNumber)
    
    # Try to match by S-format key
    fallback_key = f"S{plex_episode.seasonNumber}"
    if fallback_key in show_replacements:
        replacement = show_replacements[fallback_key]
        match = re.search(r'S(\d+)', replacement)
        return int(match.group(1)) if match else int(plex_episode.seasonNumber)
    
    return int(plex_episode.seasonNumber)


def _normalize_season_number(value: Optional[int]) -> Optional[int]:
    """
    Normalize season number to integer format.
    
    Args:
        value: Season number (int, str, or None)
        
    Returns:
        int or None: Normalized season number
        
    Raises:
        ValueError: If value cannot be converted to int
    """
    if value is None:
        return None
    
    if isinstance(value, int):
        return value
    
    value_str = str(value).strip()
    if value_str.isdigit():
        return int(value_str)
    
    # Try to extract number from string like "S01" or "Season 01"
    match = re.search(r"(\d+)", value_str)
    if match:
        return int(match.group(1))
    
    raise ValueError(f"Unable to normalize season number from value: {value}")


def add_existing_episodes_for_plex_show(plex_show) -> Tuple[int, int]:
    """
    Sync episodes for a single show from Plex to Django.

    Creates new episodes and marks existing episodes as on_disk=True.

    Args:
        plex_show: Plex show object from library

    Returns:
        Tuple of (created_count, updated_count)
    """
    # Handle show title aliases (Plex title might differ from Django)
    show_title = plex_show.title
    if show_title in SHOW_ALIASES:
        show_title = SHOW_ALIASES[plex_show.title]

    # Get or create show in Django
    django_show_object = Show.objects.filter(title=show_title).first()
    if not django_show_object:
        django_show_object = Show.objects.create(title=show_title)

    django_episodes = Episode.objects.filter(show=django_show_object)
    created_count = 0
    updated_count = 0

    # Process each episode from Plex
    for plex_episode in plex_show.episodes():
        # Skip episodes without title or season/episode numbers
        if not getattr(plex_episode, 'title', None):
            continue
        if plex_episode.seasonNumber is None or plex_episode.index is None:
            continue

        plex_season_number = _normalize_season_number(plex_episode.seasonNumber)

        # Try to find matching Django episode (exact title match first)
        django_episode = django_episodes.filter(
            title=plex_episode.title,
            season_number=plex_season_number
        ).first()

        # Fallback: try matching without dots (sometimes filenames differ)
        if not django_episode:
            django_episode = django_episodes.filter(
                title=plex_episode.title.replace('.', ''),
                season_number=plex_season_number
            ).first()

        if django_episode:
            # Update existing episode if needed
            if not django_episode.on_disk:
                django_episode.on_disk = True
                django_episode.save()
                updated_count += 1
        else:
            # Create new episode
            season_number = _normalize_season_number(_resolve_season_number(plex_show, plex_episode))
            django_episode = Episode(
                show=django_show_object,
                air_date=plex_episode.originallyAvailableAt,
                title=plex_episode.title,
                season_number=season_number,
                episode_number=plex_episode.index,
                on_disk=True
            )
            django_episode.save()
            created_count += 1

    return created_count, updated_count


def add_episodes_to_nstv(plex: Optional[PlexServer] = None) -> Tuple[int, int]:
    """
    Sync all episodes from Plex library to Django database.
    
    Args:
        plex: Optional PlexServer instance. If None, creates new connection.
        
    Returns:
        Tuple of (total_created, total_updated)
    """
    if plex is None:
        plex = get_plex_connection()
    
    try:
        plex_tv_shows = plex.library.section('TV Shows')
    except Exception as e:
        print(f"✗ Error accessing TV Shows library: {e}")
        return 0, 0
    
    total_created = 0
    total_updated = 0
    failed_count = 0

    print(f"Syncing episodes from Plex...")
    for plex_show in tqdm(plex_tv_shows.search(), desc="Processing shows"):
        try:
            created_count, updated_count = add_existing_episodes_for_plex_show(plex_show)
            total_created += created_count
            total_updated += updated_count
        except Exception as e:
            print(f"✗ Error processing episodes for '{plex_show.title}': {e}")
            failed_count += 1
            continue

    print(f"\n✓ Sync complete: {total_created} created, {total_updated} updated, {failed_count} failed")
    return total_created, total_updated


def main():
    """Entry point for command-line execution."""
    try:
        add_episodes_to_nstv()
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
