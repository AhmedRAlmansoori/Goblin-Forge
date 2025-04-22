# goblin_forge/plugins/file_processor_gadget.py
"""
File Processor Gadget for Goblin Forge.

Provides file uploading and processing capabilities.
"""
import os
import asyncio
import json
from pathlib import Path
import shutil
import logging

from goblin_forge.plugins.base_gadget import BaseGadget

logger = logging.getLogger(__name__)

class FileProcessorGadget(BaseGadget):
    name = "File Processor"  # Display name
    description = "Process uploaded files with various operations"
    tab_id = "file_processor"  # Unique ID for the tab
        
    def get_modes(self):
        """Return available file processing modes"""
        return [
            {
                "id": "file_analyzer",
                "name": "File Analyzer",
                "description": "Analyze uploaded files and provide basic information"
            },
            {
                "id": "file_converter",
                "name": "File Converter",
                "description": "Convert files between different formats"
            }
        ]
        
    def get_form_schema(self, mode):
        """Return form schema for the specified mode"""
        if mode == "file_analyzer":
            return {
                "input_file": {
                    "type": "file",
                    "label": "Input File",
                    "description": "Select a file to analyze",
                    "required": True
                },
                "analysis_type": {
                    "type": "select",
                    "label": "Analysis Type",
                    "description": "Choose what information to extract",
                    "required": True,
                    "options": [
                        {"value": "basic", "label": "Basic Information"},
                        {"value": "detailed", "label": "Detailed Analysis"}
                    ]
                }
            }
        elif mode == "file_converter":
            return {
                "input_file": {
                    "type": "file",
                    "label": "Input File",
                    "description": "Select a file to convert",
                    "required": True
                },
                "output_format": {
                    "type": "select",
                    "label": "Output Format",
                    "description": "Choose the target format",
                    "required": True,
                    "options": [
                        {"value": "txt", "label": "Text File"},
                        {"value": "pdf", "label": "PDF"},
                        {"value": "csv", "label": "CSV"}
                    ]
                }
            }
        return {}
        
    async def execute(self, mode, params, result_dir):
        """Execute file processing operation"""
        if mode == "file_analyzer":
            return await self._analyze_file(params, result_dir)
        elif mode == "file_converter":
            return await self._convert_file(params, result_dir)
        return {"error": "Invalid mode"}
        
    async def _analyze_file(self, parameters, result_dir):
        """Process file info mode"""
        input_file = parameters.get("input_file")
        analysis_type = parameters.get("analysis_type", "basic")
        
        if not input_file or not os.path.exists(input_file):
            return {"error": "Input file not found"}
            
        file_path = Path(input_file)
        result = {
            "filename": file_path.name,
            "size": os.path.getsize(input_file),
            "extension": file_path.suffix,
            "created": os.path.getctime(input_file),
            "modified": os.path.getmtime(input_file)
        }
        
        if analysis_type == "detailed":
            # Add more detailed analysis here
            result["detailed_info"] = {
                "is_readable": os.access(input_file, os.R_OK),
                "is_writable": os.access(input_file, os.W_OK),
                "is_executable": os.access(input_file, os.X_OK)
            }
            
        # Save the analysis results
        with open(os.path.join(result_dir, "analysis_results.json"), "w") as f:
            json.dump(result, f, indent=2)
            
        return {"status": "success", "message": "File analysis completed"}
        
    async def _convert_file(self, parameters, result_dir):
        """Convert file to different format"""
        input_file = parameters.get("input_file")
        output_format = parameters.get("output_format")
        
        if not input_file or not os.path.exists(input_file):
            return {"error": "Input file not found"}
            
        # In a real implementation, you would perform the actual conversion here
        # For this example, we'll just copy the file with a new extension
        input_path = Path(input_file)
        output_path = Path(result_dir) / f"{input_path.stem}.{output_format}"
        
        shutil.copy2(input_file, output_path)
        
        return {
            "status": "success",
            "message": f"File converted to {output_format}",
            "output_file": str(output_path)
        }
    
    def _human_readable_size(self, size_bytes):
        """Convert size in bytes to a human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def _format_timestamp(self, timestamp):
        """Format timestamp to a readable date/time"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def _is_binary(self, file_path):
        """Check if a file is binary"""
        try:
            with open(file_path, 'r') as f:
                f.read(1024)
                return False
        except UnicodeDecodeError:
            return True