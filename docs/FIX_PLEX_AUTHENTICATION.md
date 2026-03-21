# Plex Authentication Fix - Debug Guide

## Problem
```
plexapi.exceptions.Unauthorized: (401) unauthorized; https://plex.tv/api/v2/users/signin
"User could not be authenticated. This IP appears to be having trouble signing in to an account (detected repeated failures)"
```

## Root Cause
The original code was trying to use `MyPlexAccount` with an email and API key:
```python
account = MyPlexAccount(plex_email, plex_api_key)
```

**This is wrong!** `MyPlexAccount` expects:
- Username/email + **PASSWORD** (not API key)
- It authenticates to plex.tv servers
- It was causing repeated authentication failures, leading to IP blocking

## Solution
Changed to direct Plex server connection using API key:
```python
plex = PlexServer(plex_server, plex_api_key)
```

**This is correct because:**
- Uses API key directly (no password needed)
- Connects to local Plex server (no plex.tv authentication)
- Much faster and more reliable
- No IP blocking issues

## What Was Changed
**File:** `nstv/plexController/add_episodes_to_show.py`

1. **Import** (line 7):
   - Changed: `from plexapi.myplex import MyPlexAccount`
   - To: `from plexapi.server import PlexServer`

2. **Function** `get_plex_connection()` (lines 52-73):
   - Removed: `MyPlexAccount(plex_email, plex_api_key)` authentication
   - Added: Direct `PlexServer(plex_server, plex_api_key)` connection
   - Removed: Need for PLEX_EMAIL (API key is all that's needed)

## Required Environment Variables
Your `.env` file needs:
```
PLEX_SERVER=http://localhost:32400
PLEX_API_KEY=your_actual_api_key_here
```

NOTE: `PLEX_EMAIL` is no longer required!

## How to Get Your API Key
1. Go to: https://app.plex.tv/desktop
2. Settings → Account
3. Copy your access token (this is the API key)

## Testing
```powershell
# Make sure your .env has correct values
python nstv/plexController/add_episodes_to_show.py
```

You should see:
```
Plex connection details:
  Server: http://localhost:32400
  API Key: ***
✓ Connected to Plex server: [Your Server Name]
```

## If Still Having Issues
1. **Check PLEX_SERVER format:**
   - Should be: `http://localhost:32400` or `http://192.168.1.100:32400`
   - NOT: `localhost:32400` (needs http://)

2. **Verify API key is correct:**
   - Go to plex.tv/account and check your token
   - Make sure it's not expired

3. **Check Plex is running:**
   - Visit `http://localhost:32400` in browser
   - Should load Plex Web interface

4. **Verify TV Shows library exists:**
   - Your Plex server must have a library called "TV Shows"

