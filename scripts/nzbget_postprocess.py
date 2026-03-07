#!/usr/bin/env python3
"""
NZBGet Post-Processing Script for automatic file processing.

This script is called by NZBGet when a download completes.
It triggers the Django management command to process the downloaded files.

INSTALLATION:
1. Copy this script to NZBGet's scripts directory
2. In NZBGet Settings > Extension Scripts, enable this script
3. Set as a post-processing script
4. Configure the NSTV_PROJECT_PATH variable below

NZBGET POST-PROCESSING SCRIPT
############################################################
### NZBGET POST-PROCESSING SCRIPT                        ###

# Auto-process downloads to Plex.
#
# Automatically moves completed downloads to Plex directories
# and syncs the database.

############################################################
### OPTIONS                                              ###

# Path to NSTV Django project (required)
#NSTV_PROJECT_PATH=C:\\Users\\Nick\\nstv

# Python executable path (optional, uses system python if not set)
#PYTHON_PATH=

# Media type to process (tv|movies|all)
#MEDIA_TYPE=all

# Enable verbose output
#VERBOSE=no

############################################################
### NZBGET POST-PROCESSING SCRIPT                        ###
############################################################
"""

import os
import sys
import subprocess

# Get NZBGet environment variables
nzbget_dir = os.environ.get('NZBPP_DIRECTORY')
nzb_name = os.environ.get('NZBPP_NZBNAME')
nzb_id = os.environ.get('NZBPP_NZBID')
status = os.environ.get('NZBPP_STATUS')
category = os.environ.get('NZBPP_CATEGORY', '').lower()

# Get script options (set in NZBGet)
project_path = os.environ.get('NZBPO_NSTV_PROJECT_PATH', 'C:\\Users\\Nick\\nstv')
python_path = os.environ.get('NZBPO_PYTHON_PATH', 'python')
media_type = os.environ.get('NZBPO_MEDIA_TYPE', 'all')
verbose = os.environ.get('NZBPO_VERBOSE', 'no').lower() == 'yes'

# Logging function
def log(message, level='INFO'):
    print(f'[{level}] {message}')
    sys.stdout.flush()

# Only process successful downloads
if status != 'SUCCESS':
    log(f'Download status is {status}, skipping post-processing', 'WARNING')
    sys.exit(0)

log(f'Processing completed download: {nzb_name}')
log(f'Category: {category}')

# Determine media type from category if possible
if category and media_type == 'all':
    if 'tv' in category or 'show' in category:
        media_type = 'tv'
    elif 'movie' in category or 'film' in category:
        media_type = 'movies'

# Build command
cmd = [
    python_path,
    os.path.join(project_path, 'manage.py'),
    'process_downloads',
    f'--media-type={media_type}',
]

if verbose:
    cmd.append('--verbose')

log(f'Executing: {" ".join(cmd)}')

# Execute Django management command
try:
    result = subprocess.run(
        cmd,
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=600  # 10 minute timeout
    )
    
    if result.stdout:
        log('STDOUT:')
        print(result.stdout)
    
    if result.stderr:
        log('STDERR:', 'WARNING')
        print(result.stderr)
    
    if result.returncode == 0:
        log('Post-processing completed successfully', 'SUCCESS')
        sys.exit(93)  # POSTPROCESS_SUCCESS
    else:
        log(f'Post-processing failed with code {result.returncode}', 'ERROR')
        sys.exit(94)  # POSTPROCESS_ERROR

except subprocess.TimeoutExpired:
    log('Post-processing timed out after 10 minutes', 'ERROR')
    sys.exit(94)
except Exception as e:
    log(f'Post-processing error: {e}', 'ERROR')
    sys.exit(94)
