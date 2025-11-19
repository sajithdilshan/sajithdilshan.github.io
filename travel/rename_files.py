#!/usr/bin/env python3
"""
Script to rename files in a directory sequentially (1, 2, 3, ...) based on file extension.
"""

import os
import sys
from pathlib import Path


def rename_files_sequentially(directory, extension, prefix="", start_number=1, dry_run=False):
    """
    Rename all files with a given extension in a directory sequentially.
    
    Args:
        directory (str): Path to the directory containing files
        extension (str): File extension to filter (e.g., 'jpg', '.jpg')
        prefix (str): Optional prefix for renamed files (e.g., 'image_')
        start_number (int): Starting number for sequential naming (default: 1)
        dry_run (bool): If True, only show what would be renamed without actually renaming
    
    Returns:
        int: Number of files renamed
    """
    # Normalize the extension (ensure it starts with a dot)
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # Convert to Path object
    dir_path = Path(directory)
    
    # Check if directory exists
    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return 0
    
    if not dir_path.is_dir():
        print(f"Error: '{directory}' is not a directory.")
        return 0
    
    # Get all files with the specified extension
    files = sorted([f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() == extension.lower()])
    
    if not files:
        print(f"No files with extension '{extension}' found in '{directory}'.")
        return 0
    
    print(f"Found {len(files)} file(s) with extension '{extension}'")
    print(f"{'DRY RUN - ' if dry_run else ''}Renaming files...\n")
    
    # Rename files
    renamed_count = 0
    for i, file_path in enumerate(files, start=start_number):
        new_name = f"{prefix}{i}{extension.upper()}"
        new_path = dir_path / new_name
        
        # Skip if the file already has the target name
        if file_path.name == new_name:
            print(f"  Skipping: {file_path.name} (already has target name)")
            continue
        
        # Check if target name already exists
        if new_path.exists() and new_path != file_path:
            print(f"  Warning: Cannot rename {file_path.name} -> {new_name} (target already exists)")
            continue
        
        print(f"  {file_path.name} -> {new_name}")
        
        if not dry_run:
            try:
                file_path.rename(new_path)
                renamed_count += 1
            except Exception as e:
                print(f"    Error renaming {file_path.name}: {e}")
        else:
            renamed_count += 1
    
    print(f"\n{'Would rename' if dry_run else 'Renamed'} {renamed_count} file(s).")
    return renamed_count


def main():
    """Main function to handle command-line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python rename_files.py <directory> <extension> [prefix] [start_number] [--dry-run]")
        print("\nExamples:")
        print("  python rename_files.py ./photos jpg")
        print("  python rename_files.py ./photos .jpg img_ 1")
        print("  python rename_files.py ./photos jpg img_ 1 --dry-run")
        sys.exit(1)
    
    directory = sys.argv[1]
    extension = sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else ""
    start_number = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 1
    dry_run = '--dry-run' in sys.argv
    
    rename_files_sequentially(directory, extension, prefix, start_number, dry_run)


if __name__ == "__main__":
    main()
