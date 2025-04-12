"""
Results manager for Goblin Forge.

Handles the creation, organization, and cleanup of result directories.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class ResultsManager:
    """
    Manages the storage, organization, and cleanup of execution results.
    """
    
    def __init__(self, base_dir="./results", retention_days=7):
        """
        Initialize the ResultsManager.
        
        Args:
            base_dir (str): Base directory for storing results
            retention_days (int): Number of days to retain results before cleanup
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True, parents=True)
        self.retention_days = retention_days
        
    def create_result_directory(self, gadget_name, mode):
        """
        Create a timestamped directory for a specific execution.
        
        Args:
            gadget_name (str): Name of the Goblin Gadget
            mode (str): Execution mode
            
        Returns:
            Path: Path object for the created directory
        """
        # Clean gadget name for filesystem use
        safe_gadget_name = gadget_name.replace(" ", "_").lower()
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory name
        dir_name = f"goblinforge_{timestamp}_{safe_gadget_name}_{mode}"
        
        # Create and return the directory path
        result_dir = self.base_dir / dir_name
        result_dir.mkdir(exist_ok=True)
        
        # Create a metadata file in the directory
        self._create_metadata_file(result_dir, gadget_name, mode, timestamp)
        
        return result_dir
    
    def _create_metadata_file(self, result_dir, gadget_name, mode, timestamp):
        """
        Create a metadata file in the result directory.
        
        Args:
            result_dir (Path): Path to the result directory
            gadget_name (str): Name of the Goblin Gadget
            mode (str): Execution mode
            timestamp (str): Timestamp string
        """
        metadata = {
            "gadget": gadget_name,
            "mode": mode,
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat(),
            "retention_days": self.retention_days
        }
        
        metadata_file = result_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def cleanup_old_results(self):
        """
        Remove result directories older than the retention period.
        
        Returns:
            int: Number of directories removed
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        count = 0
        
        # Iterate through all goblinforge_* directories
        for item in self.base_dir.glob("goblinforge_*"):
            if not item.is_dir():
                continue
                
            # Check directory age by creation time
            try:
                dir_time = datetime.fromtimestamp(item.stat().st_mtime)
                if dir_time < cutoff_date:
                    # Log before removal
                    logger.info(f"Removing old result directory: {item}")
                    
                    # Delete recursively
                    shutil.rmtree(item)
                    count += 1
            except Exception as e:
                logger.error(f"Error while trying to remove directory {item}: {e}")
                
        return count
    
    def get_result_info(self, result_dir):
        """
        Get information about a result directory.
        
        Args:
            result_dir (str or Path): Path to the result directory
            
        Returns:
            dict: Information about the result directory
        """
        path = Path(result_dir)
        if not path.exists() or not path.is_dir():
            return {"error": "Result directory not found"}
        
        # Try to read metadata file
        metadata_file = path / "metadata.json"
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except:
                pass
        
        # Get list of files
        files = []
        try:
            for file_path in path.glob("*"):
                if file_path.is_file() and file_path.name != "metadata.json":
                    files.append({
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "path": str(file_path)
                    })
        except Exception as e:
            return {"error": f"Error reading result directory: {e}"}
        
        return {
            "directory": str(path),
            "metadata": metadata,
            "files": files,
            "creation_time": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
        }
    
    def list_recent_results(self, limit=20):
        """
        List recent result directories.
        
        Args:
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of recent result directories
        """
        results = []
        
        # Get all goblinforge_* directories
        dirs = list(self.base_dir.glob("goblinforge_*"))
        
        # Sort by modification time (newest first)
        dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Take only up to the limit
        dirs = dirs[:limit]
        
        # Get info for each directory
        for path in dirs:
            try:
                # Parse the directory name to extract info
                parts = path.name.split('_')
                if len(parts) >= 4:  # goblinforge_timestamp_gadget_mode
                    timestamp = f"{parts[1]}_{parts[2]}"
                    gadget = parts[3]
                    mode = '_'.join(parts[4:]) if len(parts) > 4 else ""
                    
                    # Get creation time
                    created = datetime.fromtimestamp(path.stat().st_mtime)
                    
                    results.append({
                        "path": str(path),
                        "gadget": gadget,
                        "mode": mode,
                        "created": created.isoformat(),
                        "age_days": (datetime.now() - created).days
                    })
            except Exception as e:
                logger.error(f"Error processing result directory {path}: {e}")
                
        return results