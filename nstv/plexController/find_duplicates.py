"""
Find duplicate media files in Plex library.
Identifies duplicate episodes and movies for review and potential deletion.
"""
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from plexapi.server import PlexServer

from .quality_analyzer import QualityAnalyzer, QualityScore


@dataclass
class DuplicateItem:
    """Represents a single media item that's part of a duplicate group."""
    plex_id: int
    file_path: str
    quality_score: QualityScore
    file_size: int
    is_recommended_keep: bool = False
    is_recommended_delete: bool = False
    
    # Reference to original Plex object (for deletion)
    plex_media: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'plex_id': self.plex_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_size_gb': round(self.file_size / (1024**3), 2),
            'quality': {
                'resolution': self.quality_score.resolution,
                'codec': self.quality_score.codec,
                'bitrate': self.quality_score.bitrate,
                'audio_codec': self.quality_score.audio_codec,
                'total_score': round(self.quality_score.total_score, 1),
            },
            'is_recommended_keep': self.is_recommended_keep,
            'is_recommended_delete': self.is_recommended_delete,
        }


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate media items."""
    media_type: str  # 'episode' or 'movie'
    title: str
    items: List[DuplicateItem]
    
    # For episodes
    show_title: Optional[str] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    
    # For movies
    year: Optional[int] = None
    
    def total_space_savings(self) -> int:
        """Calculate total space that would be saved by deleting recommended items."""
        return sum(
            item.file_size for item in self.items
            if item.is_recommended_delete
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering."""
        return {
            'media_type': self.media_type,
            'title': self.title,
            'show_title': self.show_title,
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'year': self.year,
            'items': [item.to_dict() for item in self.items],
            'total_space_savings': self.total_space_savings(),
            'total_space_savings_gb': round(self.total_space_savings() / (1024**3), 2),
        }


class DuplicateFinder:
    """
    Find duplicate media files in Plex library.
    
    Uses Plex API to scan library and identify:
    - Duplicate TV episodes (same show/season/episode)
    - Duplicate movies (same title, accounting for year)
    """
    
    def __init__(self):
        """
        Initialize DuplicateFinder.
        
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
    
    def find_duplicate_episodes(self, library_name: str = 'TV Shows') -> List[DuplicateGroup]:
        """
        Find duplicate TV episodes in Plex library.
        
        Args:
            library_name: Name of TV Shows library in Plex
            
        Returns:
            List of DuplicateGroup objects
        """
        duplicate_groups = []
        
        try:
            tv_library = self.plex.library.section(library_name)
        except Exception as e:
            print(f"Error accessing library '{library_name}': {e}")
            return []
        
        # Group episodes by show/season/episode
        episode_groups = defaultdict(list)
        
        print(f"Scanning '{library_name}' for duplicate episodes...")
        
        for show in tv_library.all():
            try:
                for episode in show.episodes():
                    # Skip episodes without valid season/episode numbers
                    if episode.seasonNumber is None or episode.episodeNumber is None:
                        continue
                    
                    # Check if this single episode has multiple media files (standard Plex duplicates)
                    if len(episode.media) > 1:
                        print(f"Found duplicate media files for {show.title} S{episode.seasonNumber:02d}E{episode.episodeNumber:02d}: {len(episode.media)} versions")
                        
                        duplicate_items = []
                        for media in episode.media:
                            for part in media.parts:
                                # Analyze quality
                                quality_score = self.analyzer.analyze_media(part)
                                
                                duplicate_item = DuplicateItem(
                                    plex_id=episode.ratingKey,
                                    file_path=part.file,
                                    quality_score=quality_score,
                                    file_size=part.size or 0,
                                    plex_media=part,  # Keep reference for deletion
                                )
                                duplicate_items.append(duplicate_item)
                        
                        # Determine recommendations
                        self._mark_recommendations(duplicate_items)
                        
                        # Create duplicate group
                        group = DuplicateGroup(
                            media_type='episode',
                            title=episode.title,
                            show_title=show.title,
                            season_number=episode.seasonNumber,
                            episode_number=episode.episodeNumber,
                            items=duplicate_items,
                        )
                        duplicate_groups.append(group)
                    
                    # Also track for cross-episode duplicate detection (less common)
                    # Use show.ratingKey to prevent different shows with same title from grouping
                    key = f"{show.ratingKey}|{episode.seasonNumber}|{episode.episodeNumber}"
                    episode_groups[key].append((show, episode))
            except Exception as e:
                print(f"Error scanning show '{show.title}': {e}")
                continue
        
        # Process groups with duplicates across different episode objects (rare case)
        for key, episodes in episode_groups.items():
            if len(episodes) < 2:
                continue  # Not a duplicate
            
            # Key format: "{show.ratingKey}|{season_num}|{episode_num}"
            show_rating_key, season_num, episode_num = key.split('|')
            
            # Get show title from first show in group
            show_title = episodes[0][0].title
            
            # Skip if season or episode number is invalid
            try:
                season_num = int(season_num)
                episode_num = int(episode_num)
            except ValueError:
                continue  # Skip malformed entries
            
            episode_title = episodes[0][1].title
            
            duplicate_items = []
            
            for show, episode in episodes:
                # Get all media parts for this episode
                for media in episode.media:
                    for part in media.parts:
                        # Analyze quality
                        quality_score = self.analyzer.analyze_media(part)
                        
                        duplicate_item = DuplicateItem(
                            plex_id=episode.ratingKey,
                            file_path=part.file,
                            quality_score=quality_score,
                            file_size=part.size or 0,
                            plex_media=part,  # Keep reference for deletion
                        )
                        duplicate_items.append(duplicate_item)
            
            # Only add if we haven't already processed this as a single-episode duplicate
            # (Check if any items are already in duplicate_groups)
            if duplicate_items and not any(
                item.file_path in [di.file_path for group in duplicate_groups for di in group.items]
                for item in duplicate_items
            ):
                # Determine recommendations
                self._mark_recommendations(duplicate_items)
                
                # Create duplicate group
                group = DuplicateGroup(
                    media_type='episode',
                    title=episode_title,
                    show_title=show_title,
                    season_number=season_num,
                    episode_number=episode_num,
                    items=duplicate_items,
                )
                duplicate_groups.append(group)
        
        print(f"Found {len(duplicate_groups)} duplicate episode groups")
        return duplicate_groups
    
    def find_duplicate_movies(self, library_name: str = 'Movies') -> List[DuplicateGroup]:
        """
        Find duplicate movies in Plex library.
        
        Args:
            library_name: Name of Movies library in Plex
            
        Returns:
            List of DuplicateGroup objects
        """
        duplicate_groups = []
        
        try:
            movie_library = self.plex.library.section(library_name)
        except Exception as e:
            print(f"Error accessing library '{library_name}': {e}")
            return []
        
        # Group movies by title (normalized)
        movie_groups = defaultdict(list)
        
        print(f"Scanning '{library_name}' for duplicate movies...")
        
        for movie in movie_library.all():
            try:
                # Check if this single movie has multiple media files (standard Plex duplicates)
                if len(movie.media) > 1:
                    print(f"Found duplicate media files for {movie.title} ({movie.year}): {len(movie.media)} versions")
                    
                    duplicate_items = []
                    for media in movie.media:
                        for part in media.parts:
                            # Analyze quality
                            quality_score = self.analyzer.analyze_media(part)
                            
                            duplicate_item = DuplicateItem(
                                plex_id=movie.ratingKey,
                                file_path=part.file,
                                quality_score=quality_score,
                                file_size=part.size or 0,
                                plex_media=part,  # Keep reference for deletion
                            )
                            duplicate_items.append(duplicate_item)
                    
                    # Determine recommendations
                    self._mark_recommendations(duplicate_items)
                    
                    # Create duplicate group
                    group = DuplicateGroup(
                        media_type='movie',
                        title=movie.title,
                        year=movie.year,
                        items=duplicate_items,
                    )
                    duplicate_groups.append(group)
                
                # Also track for cross-movie duplicate detection (less common)
                title_normalized = self._normalize_movie_title(movie.title)
                key = f"{title_normalized}|{movie.year or 'unknown'}"
                movie_groups[key].append(movie)
            except Exception as e:
                print(f"Error scanning movie '{movie.title}': {e}")
                continue
        
        # Process groups with duplicates across different movie objects (rare case)
        for key, movies in movie_groups.items():
            if len(movies) < 2:
                continue  # Not a duplicate
            
            title_normalized, year = key.split('|')
            movie_title = movies[0].title
            movie_year = movies[0].year
            
            duplicate_items = []
            
            for movie in movies:
                # Get all media parts for this movie
                for media in movie.media:
                    for part in media.parts:
                        # Analyze quality
                        quality_score = self.analyzer.analyze_media(part)
                        
                        duplicate_item = DuplicateItem(
                            plex_id=movie.ratingKey,
                            file_path=part.file,
                            quality_score=quality_score,
                            file_size=part.size or 0,
                            plex_media=part,  # Keep reference for deletion
                        )
                        duplicate_items.append(duplicate_item)
            
            # Only add if we haven't already processed this as a single-movie duplicate
            if duplicate_items and not any(
                item.file_path in [di.file_path for group in duplicate_groups for di in group.items]
                for item in duplicate_items
            ):
                # Determine recommendations
                self._mark_recommendations(duplicate_items)
                
                # Create duplicate group
                group = DuplicateGroup(
                    media_type='movie',
                    title=movie_title,
                    year=movie_year,
                    items=duplicate_items,
                )
                duplicate_groups.append(group)
        
        print(f"Found {len(duplicate_groups)} duplicate movie groups")
        return duplicate_groups
    
    def _normalize_movie_title(self, title: str) -> str:
        """
        Normalize movie title for comparison.
        Removes year if present in title.
        """
        import re
        # Remove year in parentheses or brackets
        title = re.sub(r'\s*[\(\[]?\d{4}[\)\]]?\s*$', '', title)
        return title.strip().lower()
    
    def _mark_recommendations(self, items: List[DuplicateItem]) -> None:
        """
        Mark which items to keep vs delete based on quality scores.
        
        Strategy:
        - Item with highest quality score = KEEP
        - All others = DELETE
        - In case of tie, keep the larger file
        """
        if not items:
            return
        
        # Sort by quality score (descending), then by file size (descending)
        sorted_items = sorted(
            items,
            key=lambda x: (x.quality_score.total_score, x.file_size),
            reverse=True
        )
        
        # Mark best one as keep
        sorted_items[0].is_recommended_keep = True
        
        # Mark rest as delete
        for item in sorted_items[1:]:
            item.is_recommended_delete = True
