# Feature: Duplicate Media Detection and Cleanup

## Issue Type
**Enhancement / Feature Request**

## Priority
**Medium** - Quality of life improvement for storage management

## Summary
Implement a duplicate media detection and cleanup system that identifies duplicate TV episodes and movies in Plex, compares their quality, and allows users to safely delete lower-quality versions.

## Business Value / User Need
- **Storage Savings**: Automatically identify and remove redundant media files
- **Library Quality**: Ensure the best quality version of each media item is retained
- **Time Savings**: Manual duplicate detection is tedious and error-prone
- **Plex Optimization**: Cleaner library improves Plex performance and user experience

## User Story
```
As a media library administrator
I want to identify and remove duplicate episodes and movies
So that I can free up storage space and maintain only the highest quality versions
```

## Detailed Requirements

### Part 1: Detection & Review Interface
**Location**: New page at `/duplicates` (or similar)

**Functionality**:
1. **Scan Plex Library** for duplicates:
   - TV Episodes: Same show, season, and episode number
   - Movies: Same title (accounting for year variations)

2. **Quality Comparison**:
   - Resolution (4K > 1080p > 720p > SD)
   - Codec (HEVC/H.265 > H.264 > older codecs)
   - Bitrate (higher is better)
   - File size (as secondary indicator)
   - Audio quality (Dolby Atmos > TrueHD > DTS-HD > AC3)

3. **Display Duplicates**:
   - Group duplicates together (e.g., "Game of Thrones S01E01")
   - Show quality metrics for each version side-by-side
   - Highlight recommended version to KEEP (green)
   - Mark recommended version to DELETE (red)
   - Allow manual override of recommendations
   
4. **Statistics Dashboard**:
   - Total duplicates found
   - Potential space savings
   - Quality distribution (how many 720p vs 1080p vs 4K duplicates)

### Part 2: Deletion Interface
**Location**: Same page as Part 1, below the duplicate list

**Functionality**:
1. **Review Before Delete**:
   - Summary of selected deletions
   - Total space to be freed
   - List of files to be deleted

2. **Safety Features**:
   - Confirmation modal with warning
   - Dry-run mode option (show what would be deleted without actually deleting)
   - Undo capability (keep deletion log for 24 hours)

3. **Delete Button**:
   - "Delete Selected Duplicates" button
   - Progress indicator during deletion
   - Success/error reporting
   - Plex library refresh after deletion

## Technical Implementation Plan

### Backend Components

#### 1. Plex Integration (`nstv/plexController/find_duplicates.py`)
```python
class DuplicateFinder:
    def find_duplicate_episodes(self) -> List[DuplicateGroup]
    def find_duplicate_movies(self) -> List[DuplicateGroup]
    def compare_quality(self, media1, media2) -> QualityComparison
    def get_recommended_deletion(self, duplicates) -> MediaItem
```

#### 2. Quality Analysis (`nstv/plexController/quality_analyzer.py`)
```python
class QualityAnalyzer:
    def analyze_video(self, media_item) -> QualityScore
    def compare_resolution(self, res1, res2) -> int
    def compare_codec(self, codec1, codec2) -> int
    def compare_bitrate(self, br1, br2) -> int
    def calculate_overall_score(self, media_item) -> float
```

#### 3. Deletion Manager (`nstv/plexController/duplicate_deletion.py`)
```python
class DuplicateDeleter:
    def delete_media(self, media_item, dry_run=False) -> bool
    def log_deletion(self, media_item)
    def refresh_plex_library(self)
```

#### 4. Django Views (`nstv/views.py`)
```python
def duplicates_index(request)  # Display duplicates
def delete_duplicates(request)  # Handle deletion
def scan_for_duplicates(request)  # Trigger scan
```

#### 5. Models (`nstv/models.py`)
```python
class DuplicateDeletionLog(models.Model):
    deleted_at = DateTimeField()
    file_path = TextField()
    show/movie = ForeignKey()
    file_size = BigIntegerField()
    quality_info = JSONField()
    deleted_by = CharField()  # Future: user tracking
```

### Frontend Components

#### 1. Template (`templates/duplicates.html`)
- Modern purple gradient theme (consistent with existing design)
- Collapsible duplicate groups
- Side-by-side comparison cards
- Quality indicators (badges for resolution, codec, etc.)
- Checkbox selection for deletion
- "Select All Low Quality" button
- Statistics cards at top

#### 2. JavaScript/AJAX
- Real-time quality comparison
- Checkbox management
- Confirmation modals
- Progress tracking during deletion
- Auto-refresh after deletion

### URL Routing
```python
path('duplicates/', duplicates_index, name='duplicates_index')
path('duplicates/scan/', scan_for_duplicates, name='scan_duplicates')
path('duplicates/delete/', delete_duplicates, name='delete_duplicates')
```

## Quality Scoring Algorithm

### Proposed Scoring System (0-100 scale)
```python
score = (
    resolution_score * 0.40 +      # 40% weight (4K=40, 1080p=30, 720p=20, SD=10)
    codec_score * 0.25 +            # 25% weight (HEVC=25, H.264=20, other=10)
    bitrate_score * 0.20 +          # 20% weight (normalized to 0-20)
    audio_score * 0.10 +            # 10% weight (Atmos=10, TrueHD=8, DTS=6, AC3=4)
    file_size_score * 0.05          # 5% weight (larger is better, normalized)
)
```

**Recommendation Logic**:
- KEEP: Highest score in duplicate group
- DELETE: All others in duplicate group
- TIE: Keep newer file (by date added to Plex)

## Safety Considerations

### Deletion Safety
1. **Never delete all copies**: Always keep at least one version
2. **File validation**: Verify file exists before deletion
3. **Plex validation**: Check file is actually in Plex before deleting
4. **Log everything**: Full audit trail of deletions
5. **Dry-run mode**: Test before actual deletion
6. **Confirmation required**: Multi-step confirmation for destructive actions

### Edge Cases to Handle
- File system permissions issues
- Files currently being watched in Plex
- Partial files / incomplete downloads
- Different editions (Director's Cut vs Theatrical)
- Multi-part episodes
- Remuxes vs encodes (user preference)

## UI/UX Mockup (Text Description)

### Duplicates Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Duplicate Media Detection                               │
│  [Scan for Duplicates] [Select All Low Quality] [Delete]   │
├─────────────────────────────────────────────────────────────┤
│  Statistics:                                                │
│  📺 Episodes: 15 duplicates | 💾 Space: 45.2 GB             │
│  🎬 Movies: 8 duplicates   | 💾 Space: 32.8 GB             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ▼ Game of Thrones - S01E01 "Winter Is Coming"            │
│     ┌──────────────────┬──────────────────┐                │
│     │ ✅ KEEP          │ ❌ DELETE        │                │
│     │ 1080p HEVC       │ 720p H.264       │                │
│     │ 2.1 GB, 5000kbps │ 1.2 GB, 2500kbps │                │
│     │ Score: 87/100    │ Score: 52/100    │                │
│     │ [☐ Override]     │ [☑ Delete]       │                │
│     └──────────────────┴──────────────────┘                │
│                                                             │
│  ▼ 2001: A Space Odyssey (1968)                            │
│     ┌──────────────────┬──────────────────┐                │
│     │ ✅ KEEP          │ ❌ DELETE        │                │
│     │ 4K HEVC HDR      │ 1080p H.264      │                │
│     │ 24.5 GB          │ 8.2 GB           │                │
│     │ Score: 95/100    │ Score: 68/100    │                │
│     │ [☐ Override]     │ [☑ Delete]       │                │
│     └──────────────────┴──────────────────┘                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Deletion Summary:                                          │
│  • 23 files selected for deletion                          │
│  • Total space to free: 78.0 GB                            │
│  • [Cancel] [Dry Run] [DELETE SELECTED] 🗑️                 │
└─────────────────────────────────────────────────────────────┘
```

## Testing Plan

### Unit Tests
- Quality scoring algorithm
- Duplicate detection logic
- File deletion with rollback

### Integration Tests
- Plex API interaction
- Database logging
- File system operations

### Manual Testing Scenarios
1. Find duplicates across different shows
2. Compare 4K vs 1080p versions
3. Delete lower quality and verify Plex updates
4. Test dry-run mode
5. Verify deletion logs
6. Test edge cases (missing files, permission errors)

## Dependencies
- Existing: `PlexAPI` (already in requirements.txt)
- Existing: Django Tables2 (for data display)
- New: None required

## Database Migration
```python
# Migration: Add DuplicateDeletionLog model
operations = [
    migrations.CreateModel(
        name='DuplicateDeletionLog',
        fields=[
            ('id', models.AutoField(primary_key=True)),
            ('deleted_at', models.DateTimeField(auto_now_add=True)),
            ('file_path', models.TextField()),
            ('show', models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, to='nstv.Show')),
            ('movie', models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, to='nstv.Movie')),
            ('file_size', models.BigIntegerField()),
            ('quality_info', models.JSONField()),
        ],
    ),
]
```

## Acceptance Criteria
- [ ] Can scan Plex library for duplicate episodes
- [ ] Can scan Plex library for duplicate movies
- [ ] Quality comparison accurately ranks media by resolution, codec, bitrate
- [ ] UI clearly shows which version to keep vs delete
- [ ] Can manually override recommendations
- [ ] Deletion requires confirmation
- [ ] Dry-run mode works correctly
- [ ] Deletion logs are created and stored
- [ ] Plex library refreshes after deletion
- [ ] Space savings statistics are accurate
- [ ] No data loss or accidental deletions in testing
- [ ] UI follows existing design guidelines (purple gradient theme)

## Future Enhancements (Out of Scope for V1)
- Auto-delete mode (with safeguards)
- Scheduled scanning
- Email notifications of duplicates found
- "Favorites" system (never delete certain encoders/groups)
- Integration with download queue (prefer certain quality)
- Multi-user approval workflow
- Comparison with external databases (IMDB ratings, etc.)

## Timeline Estimate
- Backend (duplicate detection): 4-6 hours
- Quality analysis system: 3-4 hours
- Frontend UI: 3-4 hours
- Deletion logic + safety: 2-3 hours
- Testing: 2-3 hours
- **Total**: ~15-20 hours

## References
- Plex Media Server API: https://python-plexapi.readthedocs.io/
- Frontend Design Guidelines: `docs/frontend-design-guidelines.md`
- Git Workflow: `docs/git-workflow.md`
