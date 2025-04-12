"""
File and directory handling utilities for Goblin Forge.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta


def create_timestamped_directory(base_dir, prefix, suffix=""):
    """
    Create a timestamped directory for storing results.
    
    Args:
        base_dir (str): Base directory path
        prefix (str): Prefix for directory name
        suffix (str): Optional suffix for directory name
    
    Returns:
        Path: Path object for the created directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"{prefix}_{timestamp}{f'_{suffix}' if suffix else ''}"
    dir_path = Path(base_dir) / dir_name
    dir_path.mkdir(exist_ok=True, parents=True)
    return dir_path


def clean_old_directories(base_dir, prefix, days_to_keep):
    """
    Remove directories older than specified days.
    
    Args:
        base_dir (str): Base directory path
        prefix (str): Prefix to match directories
        days_to_keep (int): Number of days to keep directories
    
    Returns:
        int: Number of directories removed
    """
    base_path = Path(base_dir)
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    count = 0
    
    for item in base_path.glob(f"{prefix}_*"):
        if not item.is_dir():
            continue
            
        # Extract timestamp from directory name
        try:
            # Assuming format is prefix_YYYYMMDD_HHMMSS
            dir_parts = item.name.split('_')
            if len(dir_parts) >= 3:
                date_str = f"{dir_parts[1]}_{dir_parts[2]}"
                dir_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                
                if dir_date < cutoff_date:
                    shutil.rmtree(item)
                    count += 1
        except (ValueError, IndexError):
            # If we can't parse the date, skip this directory
            continue
    
    return count