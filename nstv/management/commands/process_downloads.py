"""
Django management command to automatically process completed downloads.

This command moves completed downloads from NZBGet to Plex directories and
syncs the database. Can be triggered by:
- NZBGet post-processing script
- Cron job / Windows Task Scheduler
- Manual execution: python manage.py process_downloads
"""
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from plexapi.myplex import MyPlexAccount
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Process completed downloads: move to Plex and sync database'

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
            self.stdout.write(self.style.SUCCESS(f'✓ Moved: {total_moved} items'))
        
        if total_failed > 0:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {total_failed} items'))
        
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
        plex_email = os.getenv('PLEX_EMAIL')
        plex_api_key = os.getenv('PLEX_API_KEY')
        plex_server = os.getenv('PLEX_SERVER')
        
        if not plex_email or not plex_api_key or not plex_server:
            self.stdout.write(self.style.ERROR('Missing Plex credentials in environment variables'))
            self.stdout.write('Required: PLEX_EMAIL, PLEX_API_KEY, PLEX_SERVER')
            return False
        
        try:
            self.stdout.write('Checking Plex server connection...')
            account = MyPlexAccount(plex_email, plex_api_key)
            plex = account.resource(plex_server).connect()
            
            # Try to access a library to confirm connection works
            plex.library.sections()
            
            self.stdout.write(self.style.SUCCESS(f'✓ Plex server "{plex_server}" is accessible'))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Cannot connect to Plex server: {e}'))
            return False

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
        
        # Move files
        moved_count, failed_items = self._move_items(items, plex_dir)
        
        # Sync with Plex database (unless --no-sync or dry-run)
        if not self.no_sync and not self.dry_run and moved_count > 0:
            self._sync_plex_database(media_type)
        
        return moved_count, len(failed_items)

    def _get_items_to_process(self, media_type: str) -> List[str]:
        """
        Get list of items to process from NZBGet directory.
        
        This could be enhanced to filter by naming patterns or metadata.
        For now, processes everything in the directory.
        """
        try:
            all_items = os.listdir(self.nzbget_dir)
            
            # Filter out hidden files and system files
            items = [
                item for item in all_items
                if not item.startswith('.') and not item.startswith('_')
            ]
            
            return items
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading download directory: {e}'))
            return []

    def _move_items(self, items: List[str], dest_dir: str) -> Tuple[int, List[dict]]:
        """
        Move items from NZBGet to Plex directory.
        
        Returns:
            Tuple of (moved_count, failed_items)
        """
        moved_count = 0
        failed_items = []
        
        iterator = tqdm(items, desc="Processing", disable=not self.verbose_mode)
        
        for item_name in iterator:
            try:
                source_path = os.path.join(self.nzbget_dir, item_name)
                dest_path = os.path.join(dest_dir, item_name)
                
                # Check if destination already exists
                if os.path.exists(dest_path):
                    msg = f'SKIP: {item_name} (already exists at destination)'
                    if self.verbose_mode:
                        self.stdout.write(self.style.WARNING(msg))
                    failed_items.append({
                        'name': item_name,
                        'reason': 'Already exists at destination'
                    })
                    continue
                
                # Move file/directory
                if self.dry_run:
                    msg = f'WOULD MOVE: {item_name}'
                    if self.verbose_mode:
                        self.stdout.write(self.style.WARNING(msg))
                    moved_count += 1
                else:
                    shutil.move(source_path, dest_path)
                    msg = f'✓ Moved: {item_name}'
                    if self.verbose_mode:
                        self.stdout.write(self.style.SUCCESS(msg))
                    moved_count += 1
                
            except PermissionError as e:
                msg = f'✗ Permission denied: {item_name}'
                self.stdout.write(self.style.ERROR(msg))
                failed_items.append({
                    'name': item_name,
                    'reason': f'Permission denied: {e}'
                })
            except Exception as e:
                msg = f'✗ Error moving {item_name}: {e}'
                self.stdout.write(self.style.ERROR(msg))
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
            
            self.stdout.write(self.style.SUCCESS('✓ Plex sync completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Plex sync failed: {e}'))
            # Don't raise - files were already moved successfully
