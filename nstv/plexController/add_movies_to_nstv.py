"""
Sync movies from Plex to Django database.

This script connects to your Plex server and imports all movies,
optionally downloading poster images.
"""
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional, Tuple

import django
import requests
from django.conf import settings
from plexapi.server import PlexServer
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Movie


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


def _extract_director_name(directors: list) -> str:
    """
    Extract director name from Plex director objects.

    Args:
        directors: List of director objects from Plex

    Returns:
        str: Director name or empty string
    """
    if not directors:
        return ''
    first_director = directors[0]
    return getattr(first_director, 'tag', str(first_director))


def _extract_genre_names(genres: list) -> list:
    """
    Extract genre names from Plex genre objects.

    Args:
        genres: List of genre objects from Plex

    Returns:
        list: Genre names as strings
    """
    return [getattr(genre, 'tag', str(genre)) for genre in genres]


def _extract_year_from_title(title: str) -> Tuple[str, Optional[date]]:
    """
    Extract year from movie title if present.

    Handles patterns like:
    - "Red River 1948"
    -"Red River (1948)"

    Args:
        title: Movie title string

    Returns:
        Tuple of (cleaned_title, release_date_or_None)
    """
    # Match 4-digit year at the end of title (optionally in parentheses)
    year_pattern = r'\s*[\(]?(\d{4})[\)]?\s*$'
    match = re.search(year_pattern, title)
    
    if match:
        year = int(match.group(1))
        # Validate year is reasonable (between 1900 and current year + 5)
        current_year = date.today().year
        if 1900 <= year <= current_year + 5:
            cleaned_title = re.sub(year_pattern, '', title).strip()
            release_date = date(year, 1, 1)  # Use Jan 1 as default
            return cleaned_title, release_date
    
    return title, None


def save_movie_poster(
    plex_movie,
    posters_dir: Optional[Path] = None
) -> Optional[str]:
    """
    Download and save movie poster from Plex.

    Args:
        plex_movie: Plex movie object
        posters_dir: Optional directory to save posters. Defaults to templates/static/images/posters

    Returns:
        str: Path to saved poster or None if download failed
    """
    poster_url = getattr(plex_movie, 'posterUrl', None)
    movie_name = getattr(plex_movie, 'title', None) or getattr(plex_movie, 'name', None)

    if not movie_name:
        return None

    if posters_dir is None:
        posters_dir = Path(settings.BASE_DIR) / 'templates' / 'static' / 'images' / 'posters'
    posters_dir = Path(posters_dir)
    posters_dir.mkdir(parents=True, exist_ok=True)

    poster_save_path = posters_dir / f"{movie_name.replace(' ', '_')}.jpg"

    if not poster_url:
        return None

    # Skip if already downloaded
    if poster_save_path.exists():
        return str(poster_save_path)

    try:
        response = requests.get(poster_url, allow_redirects=True, timeout=10)
        response.raise_for_status()
        with open(poster_save_path, 'wb') as file_handle:
            file_handle.write(response.content)
        return str(poster_save_path)
    except Exception as e:
        print(f"  ⚠ Failed to download poster for '{movie_name}': {e}")
        return None


def upsert_movie_from_plex_movie(
    plex_movie,
    download_posters: bool = False
) -> Tuple[Optional[Movie], bool]:
    """
    Create or update a movie in Django from Plex movie object.

    Args:
        plex_movie: Plex movie object from library
        download_posters: If True, download and save poster images

    Returns:
        Tuple of (Movie object or None, created: bool)
    """
    movie_name = getattr(plex_movie, 'title', None) or getattr(plex_movie, 'name', None)
    if not movie_name:
        return None, False

    # Extract year from title if present and clean the title
    cleaned_name, extracted_date = _extract_year_from_title(movie_name)
    
    genre_names = _extract_genre_names(getattr(plex_movie, 'genres', []))
    director_name = _extract_director_name(getattr(plex_movie, 'directors', []))
    release_date = getattr(plex_movie, 'originallyAvailableAt', None)
    
    # Use extracted date if Plex doesn't provide one
    if not release_date and extracted_date:
        release_date = extracted_date

    # Check if movie already exists
    movie_object = Movie.objects.filter(name=cleaned_name).first()
    if movie_object:
        # Update missing fields
        if not movie_object.genre and genre_names:
            movie_object.genre = genre_names
        if not movie_object.director and director_name:
            movie_object.director = director_name
        if not movie_object.on_disk:
            movie_object.on_disk = True
        if not movie_object.release_date and release_date:
            movie_object.release_date = release_date
        if download_posters and not movie_object.poster_path:
            poster_path = save_movie_poster(plex_movie)
            if poster_path:
                movie_object.poster_path = poster_path
        movie_object.save()
        return movie_object, False

    # Create new movie
    poster_path = None
    if download_posters:
        poster_path = save_movie_poster(plex_movie)
    
    movie_object = Movie.objects.create(
        name=cleaned_name,
        release_date=release_date,
        genre=genre_names,
        director=director_name,
        on_disk=True,
        poster_path=poster_path,
    )
    return movie_object, True


def add_movies_to_nstv(
    plex: Optional[PlexServer] = None,
    download_posters: bool = False
) -> int:
    """
    Sync all movies from Plex library to Django database.
    
    Args:
        plex: Optional PlexServer instance. If None, creates new connection.
        download_posters: If True, download poster images from Plex
        
    Returns:
        int: Number of movies created
    """
    if plex is None:
        plex = get_plex_connection()

    try:
        plex_movies = plex.library.section('Movies')
    except Exception as e:
        print(f"✗ Error accessing Movies library: {e}")
        return 0
    
    created_count = 0
    updated_count = 0
    failed_count = 0
    
    print(f"Syncing movies from Plex...")
    for plex_movie in tqdm(plex_movies.search(), desc="Processing movies"):
        try:
            _, created = upsert_movie_from_plex_movie(plex_movie, download_posters=download_posters)
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception as e:
            print(f"✗ Error processing movie '{getattr(plex_movie, 'title', 'Unknown')}': {e}")
            failed_count += 1
            continue
    
    print(f"\n✓ Sync complete: {created_count} created, {updated_count} updated, {failed_count} failed")
    return created_count


def main():
    """Entry point for command-line execution."""
    try:
        add_movies_to_nstv()
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
