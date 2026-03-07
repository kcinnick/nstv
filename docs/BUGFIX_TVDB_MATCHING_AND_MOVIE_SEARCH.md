# Bugfix: TVDB Matching and NZBGeek Movie Search

## Issues Fixed

### 1. TVDB Series Matching for Alternative Language Titles
**Problem**: When adding shows with non-English titles (e.g., "Shoujiki Fudousan"), the TVDB import would fail because it only checked for exact matches against the English translation.

**Root Cause**: The `find_tvdb_record_for_series()` function had overly strict matching logic that only compared the search term against the English translation field. For shows where users entered a title in another language (Japanese, Spanish, etc.), no match would be found even though TVDB had the correct show with that title in its translations.

**Example Failure**:
- User adds: "Shoujiki Fudousan"  
- TVDB returns: English="The Honest Realtor", Spanish="Shoujiki Fudousan", Japanese="正直不動産"
- Old code: Only checked if "Shoujiki Fudousan" == "The Honest Realtor" → ❌ No match found
- Error: `Exception: No match found.`

**Solution**: Completely rewrote `find_tvdb_record_for_series()` with a priority-based matching system:

1. **Priority 1**: Exact match with English translation
2. **Priority 2**: Match via TVDB_ALIAS mappings  
3. **Priority 3**: Match in ANY translation (any language)
4. **Priority 4**: Match in aliases list
5. **Priority 5**: If only one result, auto-match with logging

**Test Result**:
```
✓ Matched via spa translation: "Shoujiki Fudousan"
✓ Show.tvdb_id updated to: series-418527
```

### 2. NZBGeek Movie Search (GID Extraction)
**Problem**: Movie searches failed for titles like "2001 A Space Odyssey" even though results existed on NZBGeek.

**Root Cause**: The `get_gid_for_movie()` function was looking for HTML elements with the wrong CSS class (`releases_item_release`) that don't exist in the current NZBGeek HTML structure.

**Actual HTML Structure** (from NZBGeek geekseek):
- TD #0: `releases_checkbox_release` (checkbox)
- TD #1: `releases_image` (contains movieid link) ← GID is here
- TD #2: No class (contains full release title: "2001.A.Space.Odyssey.1968.REPACK.2160p...")
- TD #8+: Category, age, size, etc.

**Old Code Issues**:
1. Searched for non-existent CSS class `releases_item_release`
2. Would crash with AttributeError when trying to access `.text` on None
3. Had logic bugs like modifying `movie.name` during search
4. No proper error handling or logging

**Solution**: Complete rewrite of `get_gid_for_movie()`:

1. Find `releases_image` TD (contains the movieid link)
2. Extract movieid from href: `geekseek.php?movieid=00062622`
3. Find release title in subsequent TDs (usually TD #2)
4. Match movie name against release title with multiple strategies:
   - Direct substring match ("2001 a space odyssey" in "2001.A.Space.Odyssey.1968...")
   - Dot-separated match ("2001.a.space.odyssey")
   - Word-by-word match (all significant words present)
5. Comprehensive logging for debugging
6. Proper error handling (returns None instead of crashing)

**Test Result**:
```
get_gid_for_movie: Found 89 results
get_gid_for_movie: Found match (#1) via direct substring match
  Movie name: '2001 A Space Odyssey'
  Release title: '2001.A.Space.Odyssey.1968.REPACK.2160p.MAX.WEB-DL...'
  GID: 00062622
✓ Successfully updated GID
```

## Files Changed

### `nstv/get_info_from_tvdb/main.py`
- Completely rewrote `find_tvdb_record_for_series()` function
- Added priority-based matching across all translations and aliases
- Added comprehensive logging with ✓/⚠/✗ indicators
- Removed cryptic debug print statements (33, 36, 45, 58, 64, 71, 74, 80)
- Added helpful error messages listing available results when no match found

### `nstv/download.py`
- Rewrote `get_gid_for_movie()` function
- Fixed HTML parsing to match actual NZBGeek structure
- Added multiple matching strategies for movie titles
- Added comprehensive logging and error handling
- Removed buggy logic that modified movie.name during search
- Returns None instead of crashing on no results

## Testing

Both fixes have been tested successfully:

**TVDB Matching**:
- ✅ "Shoujiki Fudousan" → Matched via Spanish translation
- ✅ "The Honest Realtor" → Direct English match
- ✅ Works with existing TVDB_ALIAS entries

**Movie Search**:
- ✅ "2001 A Space Odyssey" → Found GID 00062622
- ✅ Handles special characters and numbers at start of title
- ✅ Matches across different formatting (spaces vs dots)

## Impact

- **Shows**: Users can now add shows using any language title that TVDB has in its translations
- **Movies**: Movie searches will now work reliably for titles with special formatting
- **UX**: Better error messages help diagnose issues when matches fail
- **Reliability**: No more crashes from missing HTML elements or attribute errors

## Related Issues

- Fixes the error: `Exception: No match found.` when importing episodes for non-English titled shows
- Fixes the error: `AttributeError: 'NoneType' object has no attribute 'text'` in movie GID searches
- Improves logging throughout both workflows for better debugging

## Migration Notes

No database changes required. Both fixes are backward compatible with existing data.
