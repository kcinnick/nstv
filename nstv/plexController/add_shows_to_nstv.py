"""
Sync TV shows from Plex to Django database.

This script connects to your Plex server and imports all TV shows into the NSTV database,
automatically detecting anime based on genres.
"""
import os
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
from nstv.models import Show


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


def _is_anime_by_genres(genres: list) -> bool:
    """
    Detect if show is anime based on genres.

    Args:
        genres: List of genre objects from Plex

    Returns:
        bool: True if anime or animation genre is present
    """
    normalized_genres = [str(genre).strip().lower() for genre in genres]
    return 'anime' in normalized_genres or 'animation' in normalized_genres


def upsert_show_from_plex_show(plex_show) -> Tuple[Show, bool]:
    """
    Create or update a show in Django from Plex show object.

    Args:
        plex_show: Plex show object from library

    Returns:
        Tuple of (Show object, created: bool)
    """
    is_anime = _is_anime_by_genres(getattr(plex_show, 'genres', []))
    show_title = plex_show.title

    show_object = Show.objects.filter(title=show_title).first()
    if show_object:
        # Update anime flag if needed
        if is_anime and not show_object.anime:
            show_object.anime = True
            show_object.save()
        return show_object, False

    # Create new show
    show_object = Show.objects.create(title=show_title, anime=is_anime)
    return show_object, True


def add_shows_to_nstv(plex: Optional[PlexServer] = None) -> int:
    """
    Sync all TV shows from Plex library to Django database.

    Args:
        plex: Optional PlexServer instance. If None, creates new connection.

    Returns:
        int: Number of shows created
    """
    if plex is None:
        plex = get_plex_connection()

    try:
        plex_tv_shows = plex.library.section('TV Shows')
    except Exception as e:
        print(f"✗ Error accessing TV Shows library: {e}")
        return 0
    
    created_count = 0
    updated_count = 0
    failed_count = 0

    print(f"Syncing TV shows from Plex...")
    for show in tqdm(plex_tv_shows.search(), desc="Processing shows"):
        try:
            _, created = upsert_show_from_plex_show(show)
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception as e:
            print(f"✗ Error processing show '{show.title}': {e}")
            failed_count += 1
            continue

    print(f"\n✓ Sync complete: {created_count} created, {updated_count} updated, {failed_count} failed")
    return created_count


def main():
    """Entry point for command-line execution."""
    try:
        add_shows_to_nstv()
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
