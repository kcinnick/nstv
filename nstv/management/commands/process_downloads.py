"""
Django management command to automatically process completed downloads.

This command moves completed downloads from NZBGet to Plex directories and
syncs the database. Can be triggered by:
- NZBGet post-processing script
- Cron job / Windows Task Scheduler
- Manual execution: python manage.py process_downloads
"""
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from plexapi.server import PlexServer


class Command(BaseCommand):
    help = 'Process completed downloads: move to Plex and sync database'
    
    # Regex patterns to detect media types
    # TV Show patterns: S##E## notation
    TV_SHOW_PATTERN = re.compile(
        r'[Ss]\d{1,2}[Ee]\d{1,2}',  # S01E01, s01e01, S2023E15, etc.
        re.IGNORECASE
    )
    
    # Movie patterns: Year in (YYYY), [YYYY], or followed by quality
    MOVIE_PATTERN = re.compile(
        r'(\([\d]{4}\))|(\[[\d]{4}\])|(\d{4}\s*(?:1080p|720p|2160p|480p|4k|uhd|hdtv|webrip|bluray))',
        re.IGNORECASE
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--media-type',
            type=str,
            choices=['tv', 'movies', 'all'],
            default='all',
            help='Process only TV shows, movies, or both (default: all)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be moved without actually moving files'
        )
        parser.add_argument(
            '--no-sync',
            action='store_true',
            help='Skip Plex database sync after moving files'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.dry_run = options['dry_run']
        self.no_sync = options['no_sync']
        self.verbose_mode = options['verbose']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No files will be moved'))
        
        # Get environment variables
        self.nzbget_dir = os.getenv("NZBGET_COMPLETE_DIR")
        self.tv_dir = os.getenv("PLEX_TV_SHOW_DIR")
        self.movies_dir = os.getenv("PLEX_MOVIES_DIR")
        
        # Validate configuration
        self._validate_config()
        
        # Check if Plex is accessible
        if not self._check_plex_connection():
            self.stdout.write(self.style.ERROR('Plex server is not accessible. Aborting.'))
            self.stdout.write('Ensure Plex is running and environment variables are set correctly.')
            return
        
        media_type = options['media_type']
        total_moved = 0
        total_failed = 0
        
        if media_type in ['tv', 'all']:
            self.stdout.write('\n' + '=' * 80)
            self.stdout.write(self.style.HTTP_INFO('Processing TV Shows'))
            self.stdout.write('=' * 80)
            moved, failed = self._process_media_type('tv', self.tv_dir)
            total_moved += moved
            total_failed += failed
        
        if media_type in ['movies', 'all']:
            self.stdout.write('\n' + '=' * 80)
            self.stdout.write(self.style.HTTP_INFO('Processing Movies'))
            self.stdout.write('=' * 80)
            moved, failed = self._process_media_type('movies', self.movies_dir)
            total_moved += moved
            total_failed += failed
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.HTTP_INFO('SUMMARY'))
        self.stdout.write('=' * 80)
        if self.dry_run:
            self.stdout.write(f'Would move: {total_moved} items')
        else:
            self.stdout.write(self.style.SUCCESS(f'[OK] Moved: {total_moved} items'))
        
        if total_failed > 0:
            self.stdout.write(self.style.ERROR(f'[FAIL] Failed: {total_failed} items'))
        
        if total_moved == 0 and total_failed == 0:
            self.stdout.write(self.style.WARNING('No items to process'))

    def _validate_config(self):
        """Validate required environment variables and directories."""
        if not self.nzbget_dir:
            raise CommandError('NZBGET_COMPLETE_DIR environment variable not set')
        
        if not os.path.exists(self.nzbget_dir):
            raise CommandError(f'NZBGet directory not found: {self.nzbget_dir}')
        
        if not self.tv_dir:
            self.stdout.write(self.style.WARNING('PLEX_TV_SHOW_DIR not set - TV processing disabled'))
        elif not os.path.exists(self.tv_dir):
            self.stdout.write(self.style.WARNING(f'TV directory not found: {self.tv_dir}'))
        
        if not self.movies_dir:
            self.stdout.write(self.style.WARNING('PLEX_MOVIES_DIR not set - Movie processing disabled'))
        elif not os.path.exists(self.movies_dir):
            self.stdout.write(self.style.WARNING(f'Movies directory not found: {self.movies_dir}'))

    def _check_plex_connection(self) -> bool:
        """
        Check if Plex server is accessible.
        
        Returns:
            True if Plex is accessible, False otherwise
        """
        plex_api_key = os.getenv('PLEX_API_KEY')
        plex_server = os.getenv('PLEX_SERVER')
        
        if not plex_api_key or not plex_server:
            self.stdout.write(self.style.ERROR('Missing Plex credentials in environment variables'))
            self.stdout.write('Required: PLEX_API_KEY, PLEX_SERVER')
            return False
        
        try:
            self.stdout.write('Checking Plex server connection...')
            plex = PlexServer(plex_server, plex_api_key)
            
            # Try to access a library to confirm connection works
            plex.library.sections()
            
            self.stdout.write(self.style.SUCCESS(f'[OK] Plex server "{plex_server}" is accessible'))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAIL] Cannot connect to Plex server: {e}'))
            return False
    
    def _detect_media_type(self, item_name: str) -> str:
        """
        Detect whether an item is a TV show or movie based on filename.
        
        Returns:
            'tv', 'movies', or 'unknown'
        """
        # Check for TV show patterns (S##E## notation)
        if self.TV_SHOW_PATTERN.search(item_name):
            return 'tv'
        
        # Check for movie patterns (year in parentheses or brackets)
        if self.MOVIE_PATTERN.search(item_name):
            return 'movies'
        
        # If no clear pattern, try some heuristics
        movie_keywords = ['1080p', '720p', '2160p', 'x264', 'x265', 'h264', 'h265', 
                         'webrip', 'bluray', 'bdrip', 'dvdrip']
        if any(keyword in item_name.lower() for keyword in movie_keywords):
            if not self.TV_SHOW_PATTERN.search(item_name):
                return 'movies'
        
        return 'unknown'
    
    def _extract_show_name(self, item_name: str) -> str:
        """
        Extract show name from filename by removing season/episode notation.
        
        Example: "Breaking Bad S05E16" -> "Breaking Bad"
        """
        show_name = re.sub(r'[Ss]\d{1,2}[Ee]\d{1,2}.*', '', item_name).strip()
        show_name = re.sub(r'[\.\-\_]*(1080p|720p|480p|2160p|HDTV|WEBRIP|etc).*', '', 
                          show_name, flags=re.IGNORECASE).strip()
        return show_name
    
    def _extract_movie_name(self, item_name: str) -> str:
        """
        Extract movie name from filename by removing quality indicators.
        
        Example: "Inception (2010) 1080p" -> "Inception (2010)"
        """
        match = re.search(r'^(.+?(?:\(\d{4}\)|\[\d{4}\])?)', item_name)
        if match:
            movie_name = match.group(1).strip()
            movie_name = re.sub(r'[\.\-\_]+$', '', movie_name)
            return movie_name
        return item_name

    def _process_media_type(self, media_type: str, plex_dir: str) -> Tuple[int, int]:
        """
        Process downloads for a specific media type.
        
        Returns:
            Tuple of (moved_count, failed_count)
        """
        if not plex_dir or not os.path.exists(plex_dir):
            self.stdout.write(self.style.WARNING(f'Skipping {media_type} - directory not available'))
            return 0, 0
        
        # Get items from download directory
        items = self._get_items_to_process(media_type)
        
        if not items:
            self.stdout.write(f'No {media_type} files to process')
            return 0, 0
        
        self.stdout.write(f'Found {len(items)} items to process')
        
        # Move files (pass media_type for proper organization)
        moved_count, failed_items = self._move_items(items, plex_dir, media_type)
        
        # Sync with Plex database (unless --no-sync or dry-run)
        if not self.no_sync and not self.dry_run and moved_count > 0:
            self._sync_plex_database(media_type)
        
        return moved_count, len(failed_items)

    def _get_items_to_process(self, media_type: str) -> List[str]:
        """
        Get list of items to process from NZBGet directory, filtered by media type.
        
        TV Shows: Files/folders matching S##E## pattern
        Movies: Files/folders matching (YYYY) or [YYYY] pattern
        """
        try:
            all_items = os.listdir(self.nzbget_dir)
            
            # Filter out hidden files and system files
            items = [
                item for item in all_items
                if not item.startswith('.') and not item.startswith('_')
            ]
            
            # Filter by media type
            filtered_items = []
            for item in items:
                detected_type = self._detect_media_type(item)
                if detected_type == media_type:
                    filtered_items.append(item)
                elif detected_type == 'unknown' and self.verbose_mode:
                    # For unknown items, be conservative and skip them
                    self.stdout.write(
                        self.style.WARNING(f'Skipping unknown item: {item}')
                    )
            
            return filtered_items
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading download directory: {e}'))
            return []

    def _move_items(self, items: List[str], dest_dir: str, media_type: str = None) -> Tuple[int, List[dict]]:
        """
        Move items from NZBGet to Plex directory, organized by show/movie name.
        
        For TV Shows: dest_dir/[Show Name]/[item_name]
        For Movies: dest_dir/[Movie Name]/[item_name]
        
        Returns:
            Tuple of (moved_count, failed_items)
        """
        moved_count = 0
        failed_items = []
        
        for idx, item_name in enumerate(items, 1):
            try:
                source_path = os.path.join(self.nzbget_dir, item_name)
                
                # Determine organization folder based on media type
                detected_type = self._detect_media_type(item_name)
                
                if detected_type == 'tv':
                    # Extract show name and organize into show folder
                    show_name = self._extract_show_name(item_name)
                    org_folder = os.path.join(dest_dir, show_name)
                elif detected_type == 'movies':
                    # Extract movie name and organize into movie folder
                    movie_name = self._extract_movie_name(item_name)
                    org_folder = os.path.join(dest_dir, movie_name)
                else:
                    # Unknown - skip
                    self.stdout.write(
                        self.style.WARNING(f'[{idx}/{len(items)}] SKIP (unknown): {item_name}')
                    )
                    failed_items.append({
                        'name': item_name,
                        'reason': 'Could not determine if TV show or movie'
                    })
                    continue
                
                dest_path = os.path.join(org_folder, item_name)
                
                # Show progress
                self.stdout.write(f'\n[{idx}/{len(items)}] Processing: {item_name}')
                self.stdout.write(f'  Organization: {os.path.basename(org_folder)}/')
                
                # Create organization folder if needed
                if not os.path.exists(org_folder):
                    os.makedirs(org_folder, exist_ok=True)
                
                # Check if destination already exists
                if os.path.exists(dest_path):
                    msg = f'  SKIP: Already exists at destination'
                    self.stdout.write(self.style.WARNING(msg))
                    failed_items.append({
                        'name': item_name,
                        'reason': 'Already exists at destination'
                    })
                    continue
                
                # Get file/directory size for progress indication
                if os.path.isfile(source_path):
                    size_gb = os.path.getsize(source_path) / (1024**3)
                    self.stdout.write(f'  Size: {size_gb:.2f} GB')
                elif os.path.isdir(source_path):
                    # Calculate directory size
                    total_size = sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, _, filenames in os.walk(source_path)
                        for filename in filenames
                    )
                    size_gb = total_size / (1024**3)
                    self.stdout.write(f'  Size: {size_gb:.2f} GB (directory)')
                
                # Move file/directory
                if self.dry_run:
                    self.stdout.write(self.style.WARNING('  WOULD MOVE'))
                    moved_count += 1
                else:
                    self.stdout.write('  Moving... (this may take a while for large files)')
                    shutil.move(source_path, dest_path)
                    self.stdout.write(self.style.SUCCESS('  [OK] Moved successfully'))
                    moved_count += 1
                
            except PermissionError as e:
                self.stdout.write(self.style.ERROR(f'  [FAIL] Permission denied: {e}'))
                failed_items.append({
                    'name': item_name,
                    'reason': f'Permission denied: {e}'
                })
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [FAIL] Error: {e}'))
                failed_items.append({
                    'name': item_name,
                    'reason': str(e)
                })
        
        return moved_count, failed_items

    def _sync_plex_database(self, media_type: str):
        """
        Sync Django database with Plex library.
        
        Calls the appropriate sync script based on media type.
        """
        self.stdout.write('\nSyncing with Plex library...')
        
        try:
            if media_type == 'tv':
                # Import here to avoid circular dependency
                from nstv.plexController.add_episodes_to_show import main as sync_episodes
                from nstv.plexController.add_shows_to_nstv import main as sync_shows
                
                self.stdout.write('  - Syncing shows...')
                sync_shows()
                self.stdout.write('  - Syncing episodes...')
                sync_episodes()
                
            elif media_type == 'movies':
                from nstv.plexController.add_movies_to_nstv import main as sync_movies
                
                self.stdout.write('  - Syncing movies...')
                sync_movies()
            
            self.stdout.write(self.style.SUCCESS('[OK] Plex sync completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAIL] Plex sync failed: {e}'))
            # Don't raise - files were already moved successfully
