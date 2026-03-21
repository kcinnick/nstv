"""
Handle deletion of duplicate media files.
Includes safety checks, logging, and Plex library refresh.
"""
import os
from typing import List, Dict, Any
from datetime import datetime
from plexapi.server import PlexServer

from nstv.models import DuplicateDeletionLog, Episode, Movie
from .quality_analyzer import QualityAnalyzer


class DuplicateDeleter:
    """
    Safely delete duplicate media files.
    
    Features:
    - Dry-run mode for testing
    - File validation before deletion
    - Audit logging
    - Plex library refresh
    """
    
    def __init__(self):
        """
        Initialize DuplicateDeleter.
        
        Connects to Plex using PLEX_API_KEY and PLEX_SERVER environment variables.
        """
        plex_api_key = os.getenv('PLEX_API_KEY')
        plex_server = os.getenv('PLEX_SERVER')
        
        if not plex_api_key or not plex_server:
            raise ValueError('Missing PLEX_API_KEY or PLEX_SERVER environment variables.')
        
        try:
            self.plex = PlexServer(plex_server, plex_api_key)
        except Exception as e:
            raise ValueError(f'Failed to connect to Plex server: {e}')
        
        self.analyzer = QualityAnalyzer()
    
    def delete_files(
        self,
        file_paths: List[str],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Delete media files using Plex API.
        
        Args:
            file_paths: List of file paths to delete
            dry_run: If True, simulate deletion without actually deleting
            
        Returns:
            Dictionary with deletion results
        """
        results = {
            'deleted': [],
            'failed': [],
            'total_space_freed': 0,
            'dry_run': dry_run,
        }
        
        for file_path in file_paths:
            try:
                # Find the media object (not just the part) in Plex by file path
                media_info = self._find_media_by_path(file_path)
                
                if not media_info:
                    results['failed'].append({
                        'path': file_path,
                        'error': 'Media not found in Plex'
                    })
                    print(f"[ERROR] Media not found in Plex: {file_path}")
                    continue
                
                episode_or_movie = media_info['parent']
                media_to_delete = media_info['media']
                media_part = media_info['part']
                
                # Get file size before deletion
                file_size = media_part.size or 0
                
                # Get quality info
                quality_info = self._get_quality_info_from_part(media_part)
                
                if dry_run:
                    # Simulate deletion
                    results['deleted'].append({
                        'path': file_path,
                        'size': file_size,
                        'size_gb': round(file_size / (1024**3), 2),
                    })
                    results['total_space_freed'] += file_size
                    print(f"[DRY RUN] Would delete: {file_path} ({file_size / (1024**3):.2f} GB)")
                else:
                    # Actually delete the media version using Plex API
                    try:
                        # Delete the media object (this removes the specific version)
                        media_to_delete.delete()
                        
                        print(f"[SUCCESS] Deleted via Plex API: {file_path} ({file_size / (1024**3):.2f} GB)")
                        
                        # Log the deletion
                        self._log_deletion(
                            file_path=file_path,
                            file_size=file_size,
                            quality_info=quality_info,
                            episode=None,  # Could enhance this later
                            movie=None,     # Could enhance this later
                        )
                        
                        results['deleted'].append({
                            'path': file_path,
                            'size': file_size,
                            'size_gb': round(file_size / (1024**3), 2),
                        })
                        results['total_space_freed'] += file_size
                        
                    except Exception as delete_error:
                        raise Exception(f"Plex API deletion failed: {delete_error}")
                
            except Exception as e:
                results['failed'].append({
                    'path': file_path,
                    'error': str(e)
                })
                print(f"[ERROR] Failed to delete {file_path}: {e}")
        
        # Refresh Plex library if any files were deleted
        if results['deleted'] and not dry_run:
            self._refresh_plex_library()
        
        return results
    
    def _find_media_by_path(self, file_path: str):
        """
        Find a media object and its parent in Plex by file path.
        
        Args:
            file_path: Full path to the media file
            
        Returns:
            Dictionary with 'parent' (episode/movie), 'media', and 'part' or None if not found
        """
        try:
            # Search in all library sections
            for section in self.plex.library.sections():
                if section.type not in ['movie', 'show']:
                    continue
                
                # For TV shows
                if section.type == 'show':
                    for show in section.all():
                        for episode in show.episodes():
                            for media in episode.media:
                                for part in media.parts:
                                    if part.file == file_path:
                                        return {
                                            'parent': episode,
                                            'media': media,
                                            'part': part
                                        }
                
                # For movies
                elif section.type == 'movie':
                    for movie in section.all():
                        for media in movie.media:
                            for part in media.parts:
                                if part.file == file_path:
                                    return {
                                        'parent': movie,
                                        'media': media,
                                        'part': part
                                    }
            
            return None
            
        except Exception as e:
            print(f"Error finding media: {e}")
            return None
    
    def _find_media_part_by_path(self, file_path: str):
        """
        Find a media part in Plex by its file path.
        
        Args:
            file_path: Full path to the media file
            
        Returns:
            Media part object or None if not found
        """
        try:
            # Search in all library sections
            for section in self.plex.library.sections():
                if section.type not in ['movie', 'show']:
                    continue
                
                # For TV shows
                if section.type == 'show':
                    for show in section.all():
                        for episode in show.episodes():
                            for media in episode.media:
                                for part in media.parts:
                                    if part.file == file_path:
                                        return part
                
                # For movies
                elif section.type == 'movie':
                    for movie in section.all():
                        for media in movie.media:
                            for part in media.parts:
                                if part.file == file_path:
                                    return part
            
            return None
            
        except Exception as e:
            print(f"Error finding media part: {e}")
            return None
    
    def _get_quality_info_from_part(self, media_part) -> Dict[str, Any]:
        """
        Get quality information from a Plex media part.
        
        Args:
            media_part: Plex media part object
            
        Returns:
            Dictionary with quality information
        """
        try:
            quality_info = self.analyzer.analyze_media(media_part)
            
            return {
                'resolution': quality_info.resolution,
                'codec': quality_info.codec,
                'bitrate': quality_info.bitrate,
                'audio_codec': quality_info.audio_codec,
                'total_score': quality_info.total_score,
                'file_path': media_part.file,
                'file_size': media_part.size,
                'extracted_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            print(f"Error extracting quality info: {e}")
            return {'file_path': media_part.file if media_part else 'unknown', 'error': str(e)}
    
    def _get_quality_info_from_path(self, file_path: str) -> Dict[str, Any]:
        """
        Get quality information from Plex for a file path.
        
        Args:
            file_path: Full path to media file
            
        Returns:
            Dictionary with quality information
        """
        try:
            # Search Plex for this file
            # This is a simplified approach - in production you might want to
            # pass the plex_media object directly to avoid this lookup
            
            # For now, return basic info from filename
            filename = os.path.basename(file_path)
            
            quality_info = {
                'filename': filename,
                'path': file_path,
                'extracted_at': datetime.now().isoformat(),
            }
            
            # Try to extract quality from filename
            if '2160p' in filename or '4K' in filename.upper():
                quality_info['resolution'] = '4K'
            elif '1080p' in filename:
                quality_info['resolution'] = '1080p'
            elif '720p' in filename:
                quality_info['resolution'] = '720p'
            else:
                quality_info['resolution'] = 'unknown'
            
            if 'HEVC' in filename.upper() or 'H265' in filename.upper() or 'x265' in filename:
                quality_info['codec'] = 'HEVC'
            elif 'H264' in filename.upper() or 'x264' in filename:
                quality_info['codec'] = 'H.264'
            else:
                quality_info['codec'] = 'unknown'
            
            return quality_info
            
        except Exception as e:
            print(f"Error extracting quality info: {e}")
            return {'filename': os.path.basename(file_path), 'error': str(e)}
    
    def _find_episode_by_path(self, file_path: str) -> Episode:
        """
        Find Episode model instance by file path.
        This is a placeholder - in production, pass episode reference directly.
        """
        # Placeholder: Would need to match Plex file paths to Episode records
        return None
    
    def _find_movie_by_path(self, file_path: str) -> Movie:
        """
        Find Movie model instance by file path.
        This is a placeholder - in production, pass movie reference directly.
        """
        # Placeholder: Would need to match Plex file paths to Movie records
        return None
    
    def _log_deletion(
        self,
        file_path: str,
        file_size: int,
        quality_info: Dict[str, Any],
        episode: Episode = None,
        movie: Movie = None,
    ) -> None:
        """
        Log deletion to database for audit trail.
        
        Args:
            file_path: Path to deleted file
            file_size: Size of file in bytes
            quality_info: Dictionary with quality information
            episode: Associated Episode model (if applicable)
            movie: Associated Movie model (if applicable)
        """
        try:
            DuplicateDeletionLog.objects.create(
                file_path=file_path,
                file_size=file_size,
                quality_info=quality_info,
                episode=episode,
                movie=movie,
                reason='Lower quality duplicate',
            )
            print(f"Logged deletion: {file_path}")
        except Exception as e:
            print(f"Error logging deletion: {e}")
    
    def _refresh_plex_library(self) -> None:
        """
        Refresh Plex library to update after deletions.
        """
        try:
            # Refresh all libraries
            for section in self.plex.library.sections():
                if section.type in ['movie', 'show']:
                    print(f"Refreshing Plex library: {section.title}")
                    section.update()
            print("Plex library refresh complete")
        except Exception as e:
            print(f"Error refreshing Plex library: {e}")
    
    def get_deletion_history(self, limit: int = 100) -> List[DuplicateDeletionLog]:
        """
        Get recent deletion history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of DuplicateDeletionLog instances
        """
        return DuplicateDeletionLog.objects.all()[:limit]
