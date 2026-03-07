"""
Quality analysis for media files.
Compares video/audio quality to determine which duplicate to keep.
"""
from dataclasses import dataclass
from typing import Any, Dict
import re


@dataclass
class QualityScore:
    """Represents quality metrics for a media file."""
    resolution_score: float  # 0-40
    codec_score: float       # 0-25
    bitrate_score: float     # 0-20
    audio_score: float       # 0-10
    filesize_score: float    # 0-5
    total_score: float       # 0-100
    
    resolution: str = ""
    codec: str = ""
    bitrate: int = 0
    audio_codec: str = ""
    file_size: int = 0
    
    def __str__(self):
        return f"{self.total_score:.1f}/100 ({self.resolution}, {self.codec}, {self.bitrate}kbps)"


class QualityAnalyzer:
    """
    Analyzes media quality and generates scores for comparison.
    
    Scoring Algorithm (0-100):
    - Resolution: 40% (4K=40, 1080p=30, 720p=20, SD=10)
    - Codec: 25% (HEVC=25, H.264=20, other=10)
    - Bitrate: 20% (normalized, higher is better)
    - Audio: 10% (Atmos=10, TrueHD=8, DTS=6, AC3=4, AAC=2)
    - File Size: 5% (normalized, larger is better)
    """
    
    # Resolution mappings
    RESOLUTION_SCORES = {
        '4k': 40, '2160p': 40, 'uhd': 40,
        '1080p': 30, 'fhd': 30,
        '720p': 20, 'hd': 20,
        '480p': 10, 'sd': 10,
        '360p': 5,
    }
    
    # Video codec scores
    CODEC_SCORES = {
        'hevc': 25, 'h265': 25, 'h.265': 25, 'x265': 25,
        'h264': 20, 'h.264': 20, 'x264': 20, 'avc': 20,
        'mpeg4': 10, 'xvid': 10, 'divx': 10,
    }
    
    # Audio codec scores
    AUDIO_SCORES = {
        'atmos': 10, 'dolby atmos': 10,
        'truehd': 8, 'dolby truehd': 8,
        'dts-hd': 7, 'dts-hd ma': 7, 'dts-hd.ma': 7,
        'dts': 6, 'dts-es': 6,
        'ac3': 4, 'dolby digital': 4, 'dd': 4,
        'aac': 2,
        'mp3': 1,
    }
    
    def analyze_media(self, media_part: Any) -> QualityScore:
        """
        Analyze a Plex media part and generate quality score.
        
        Args:
            media_part: Plex MediaPart object with video/audio streams
            
        Returns:
            QualityScore object with detailed metrics
        """
        # Extract media properties
        video_stream = None
        audio_stream = None
        
        # Get video and audio streams
        if hasattr(media_part, 'videoStreams') and media_part.videoStreams():
            video_stream = media_part.videoStreams()[0]
        if hasattr(media_part, 'audioStreams') and media_part.audioStreams():
            audio_stream = media_part.audioStreams()[0]
        
        # Extract properties
        resolution = self._get_resolution(video_stream)
        codec = self._get_codec(video_stream)
        bitrate = self._get_bitrate(video_stream)
        audio_codec = self._get_audio_codec(audio_stream)
        file_size = getattr(media_part, 'size', 0) if media_part else 0
        
        # Calculate scores
        resolution_score = self._score_resolution(resolution)
        codec_score = self._score_codec(codec)
        bitrate_score = self._score_bitrate(bitrate)
        audio_score = self._score_audio(audio_codec)
        filesize_score = self._score_filesize(file_size)
        
        total_score = (
            resolution_score +
            codec_score +
            bitrate_score +
            audio_score +
            filesize_score
        )
        
        return QualityScore(
            resolution_score=resolution_score,
            codec_score=codec_score,
            bitrate_score=bitrate_score,
            audio_score=audio_score,
            filesize_score=filesize_score,
            total_score=total_score,
            resolution=resolution,
            codec=codec,
            bitrate=bitrate,
            audio_codec=audio_codec,
            file_size=file_size,
        )
    
    def _get_resolution(self, video_stream) -> str:
        """Extract resolution from video stream."""
        if not video_stream:
            return "unknown"
        
        height = getattr(video_stream, 'height', 0)
        
        if height >= 2160:
            return "4K"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
        else:
            return f"{height}p" if height else "unknown"
    
    def _get_codec(self, video_stream) -> str:
        """Extract video codec from stream."""
        if not video_stream:
            return "unknown"
        
        codec = getattr(video_stream, 'codec', '') or getattr(video_stream, 'codecID', '')
        return str(codec).lower() if codec else "unknown"
    
    def _get_bitrate(self, video_stream) -> int:
        """Extract bitrate from video stream (in kbps)."""
        if not video_stream:
            return 0
        
        bitrate = getattr(video_stream, 'bitrate', 0)
        return int(bitrate) if bitrate else 0
    
    def _get_audio_codec(self, audio_stream) -> str:
        """Extract audio codec from stream."""
        if not audio_stream:
            return "unknown"
        
        codec = getattr(audio_stream, 'codec', '') or getattr(audio_stream, 'audioCodec', '')
        profile = getattr(audio_stream, 'profile', '')
        
        codec_str = str(codec).lower() if codec else ""
        profile_str = str(profile).lower() if profile else ""
        
        # Check for Atmos in profile
        if 'atmos' in profile_str or 'atmos' in codec_str:
            return "Atmos"
        
        return codec_str if codec_str else "unknown"
    
    def _score_resolution(self, resolution: str) -> float:
        """Score resolution (0-40 points)."""
        resolution_lower = resolution.lower()
        
        for key, score in self.RESOLUTION_SCORES.items():
            if key in resolution_lower:
                return float(score)
        
        return 5.0  # Unknown resolution gets minimal score
    
    def _score_codec(self, codec: str) -> float:
        """Score video codec (0-25 points)."""
        codec_lower = codec.lower()
        
        for key, score in self.CODEC_SCORES.items():
            if key in codec_lower:
                return float(score)
        
        return 10.0  # Unknown codec gets middle score
    
    def _score_bitrate(self, bitrate: int) -> float:
        """
        Score bitrate (0-20 points).
        Normalized: 20000+ kbps = 20 points, scales down linearly.
        """
        if bitrate <= 0:
            return 0.0
        
        # Normalize: 20000 kbps = max score of 20
        score = min(20.0, (bitrate / 20000.0) * 20.0)
        return score
    
    def _score_audio(self, audio_codec: str) -> float:
        """Score audio codec (0-10 points)."""
        audio_lower = audio_codec.lower()
        
        for key, score in self.AUDIO_SCORES.items():
            if key in audio_lower:
                return float(score)
        
        return 1.0  # Unknown audio gets minimal score
    
    def _score_filesize(self, file_size: int) -> float:
        """
        Score file size (0-5 points).
        Normalized: 20GB+ = 5 points, scales down linearly.
        """
        if file_size <= 0:
            return 0.0
        
        # Convert to GB
        gb = file_size / (1024 ** 3)
        
        # Normalize: 20GB = max score of 5
        score = min(5.0, (gb / 20.0) * 5.0)
        return score
    
    def compare_quality(self, score1: QualityScore, score2: QualityScore) -> int:
        """
        Compare two quality scores.
        
        Returns:
            1 if score1 is better
            -1 if score2 is better
            0 if equal
        """
        if score1.total_score > score2.total_score:
            return 1
        elif score1.total_score < score2.total_score:
            return -1
        else:
            return 0
    
    def get_quality_dict(self, score: QualityScore) -> Dict[str, Any]:
        """Convert QualityScore to dictionary for JSON storage."""
        return {
            'resolution': score.resolution,
            'codec': score.codec,
            'bitrate': score.bitrate,
            'audio_codec': score.audio_codec,
            'file_size': score.file_size,
            'total_score': score.total_score,
            'resolution_score': score.resolution_score,
            'codec_score': score.codec_score,
            'bitrate_score': score.bitrate_score,
            'audio_score': score.audio_score,
            'filesize_score': score.filesize_score,
        }
