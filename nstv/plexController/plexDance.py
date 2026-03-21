"""
Plex Dance - Force Plex library refresh.

Reference: https://www.reddit.com/r/PleX/comments/s14kbf/whats_the_plex_dance_to_get_plex_to_redetect_the/

The "Plex Dance" is a technique to force Plex to re-scan and re-index media files
by temporarily moving them out of the library, then moving them back.

This is useful when Plex is having issues detecting new files or updating metadata.
"""
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

from tqdm import tqdm


def move_files(source_path: str, destination_path: str, operation: str = "moving") -> None:
    """
    Move files from source to destination directory.
    
    Args:
        source_path: Source directory path
        destination_path: Destination directory path
        operation: Description of operation (for display)
        
    Raises:
        ValueError: If paths are missing or invalid
        OSError: If file operations fail
    """
    if not source_path or not destination_path:
        raise ValueError('Both source_path and destination_path are required.')
    
    source_path = Path(source_path)
    destination_path = Path(destination_path)
    
    # Validate source directory
    if not source_path.exists():
        raise OSError(f'Source directory not found: {source_path}')
    if not source_path.is_dir():
        raise OSError(f'Source path is not a directory: {source_path}')
    
    # Create destination directory if needed
    destination_path.mkdir(parents=True, exist_ok=True)
    
    # List files to move
    files = list(source_path.iterdir())
    if not files:
        print(f"  ℹ No files to move from {source_path}")
        return
    
    print(f"  {operation.title()} {len(files)} file(s) from {source_path} to {destination_path}")
    
    for file_path in tqdm(files, desc="Moving files"):
        try:
            destination_file = destination_path / file_path.name
            shutil.move(str(file_path), str(destination_file))
        except Exception as e:
            print(f"  ✗ Error moving {file_path.name}: {e}")
            raise


def plex_dance(
    show_path: Optional[str] = None,
    temp_path: Optional[str] = None,
    wait_for_input: bool = True
) -> None:
    """
    Execute the Plex Dance procedure.
    
    1. Moves media files out of the library
    2. Waits for Plex to notice the deletion
    3. User empties Plex trash
    4. Moves files back into the library
    5. Plex re-scans and re-indexes
    
    Args:
        show_path: Path to show/library folder. Defaults to SHOW_FOLDER_PATH env var
        temp_path: Path to temp folder. Defaults to TEMP_FOLDER_PATH env var
        wait_for_input: If True, wait for user input between moves
        
    Raises:
        ValueError: If required paths are not provided or don't exist
    """
    # Get paths from environment or arguments
    show_path = show_path or os.getenv('SHOW_FOLDER_PATH')
    temp_path = temp_path or os.getenv('TEMP_FOLDER_PATH')
    
    # Validate paths
    if not show_path:
        raise ValueError('SHOW_FOLDER_PATH environment variable not set. Provide show_path argument or set env var.')
    if not temp_path:
        raise ValueError('TEMP_FOLDER_PATH environment variable not set. Provide temp_path argument or set env var.')
    
    show_path = Path(show_path)
    temp_path = Path(temp_path)
    
    print("\n" + "="*60)
    print("🎭 Plex Dance - Force Library Refresh")
    print("="*60)
    
    try:
        # Step 1: Move files to temp location
        print("\n✓ Step 1: Moving files OUT of Plex library")
        move_files(str(show_path), str(temp_path), "removing")
        
        # Step 2: Wait for user to refresh Plex
        if wait_for_input:
            print("\n" + "="*60)
            print("⏸ Step 2: Plex Scan & Trash Cleanup")
            print("="*60)
            print("\nNow do the following:")
            print("1. Open Plex Web UI")
            print("2. Go to Settings → Library → Scan Library Now")
            print("3. Wait for scan to complete")
            print("4. Go to Settings → Library → Empty Trash")
            print("5. Wait for trash to empty")
            print("\nPress ENTER when done...")
            input("> ")
        
        # Step 3: Move files back
        print("\n✓ Step 3: Moving files BACK into Plex library")
        move_files(str(temp_path), str(show_path), "restoring")
        
        print("\n" + "="*60)
        print("✓ Plex Dance Complete!")
        print("="*60)
        print("\nPlex will now scan and re-index the library.")
        print("Check your Plex Web UI to verify files are being detected.")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during Plex Dance: {e}")
        print("\nIMPORTANT: Files may still be in temp location!")
        print(f"Check: {temp_path}")
        raise


def main():
    """Entry point for command-line execution."""
    try:
        plex_dance()
    except Exception as e:
        print(f"✗ Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
