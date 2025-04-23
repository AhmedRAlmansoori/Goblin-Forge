# Creating Plugins for Goblin Forge

Goblin Forge's plugin system, known as "Goblin Gadgets," makes it easy to add new tools to the platform. This guide will walk you through creating your own gadgets, whether they're pure Python implementations or wrappers around external binary tools.

## Quick Links

- [Understanding Goblin Gadgets](#understanding-goblin-gadgets)
- [Quick Start](#quick-start)
- [Creating a Pure Python Gadget](#creating-a-pure-python-gadget)
- [Creating a Binary-Based Gadget](#creating-a-binary-based-gadget)
- [File Upload Feature](#file-upload-feature)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Testing](#testing)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Understanding Goblin Gadgets

Goblin Gadgets are Python classes that inherit from the `BaseGadget` class. Each gadget represents a tool with multiple operation modes, each having its own set of parameters.

### Key Components of a Gadget

1. **Class Attributes**:
   - `name`: Display name shown in the UI
   - `description`: Short description of what the gadget does
   - `tab_id`: Unique identifier for the gadget (no spaces)
   - `binary_name` (optional): Name of binary executable
   - `binary_path` (optional): Path to binary executable

2. **Required Methods**:
   - `get_modes()`: Returns available operation modes
   - `get_form_schema(mode)`: Returns UI form fields for a mode
   - `execute(mode, params, result_dir)`: Runs the actual operation

3. **Optional Methods**:
   - `summarize_results(result_dir)`: Generates a summary of results
   - `get_result_details(result_dir)`: Gets detailed info about a result

## Quick Start

Here's a minimal example to get you started:

```python
from goblin_forge.plugins.base_gadget import BaseGadget

class HelloWorldGadget(BaseGadget):
    name = "Hello World"
    description = "A simple greeting gadget"
    tab_id = "hello_world"
    
    def get_modes(self):
        return [{
            "id": "greet",
            "name": "Greet",
            "description": "Say hello to someone"
        }]
    
    def get_form_schema(self, mode):
        return {
            "name": {
                "type": "string",
                "label": "Name",
                "required": True,
                "placeholder": "Enter your name"
            }
        }
    
    async def execute(self, mode, params, result_dir):
        name = params.get("name", "World")
        return {
            "status": "completed",
            "message": f"Hello, {name}!"
        }
```

## Creating a Pure Python Gadget

Let's create a simple text processing gadget that uses Python's built-in functions.

### Step 1: Create a new Python file

Create a file named `text_processor_gadget.py` in the `goblin_forge/plugins/` directory:

```python
"""
Text Processor Gadget for Goblin Forge.

Provides text transformation and analysis capabilities.
"""
import os
import json
import re
from pathlib import Path
import logging

from goblin_forge.plugins.base_gadget import BaseGadget

logger = logging.getLogger(__name__)

class TextProcessorGadget(BaseGadget):
    """A gadget for processing and analyzing text"""
    name = "Text Processor"
    description = "Process and analyze text in various ways"
    tab_id = "text_processor"
    
    def get_modes(self):
        """Return available text processing modes"""
        return [
            {
                "id": "count_words",
                "name": "Word Count",
                "description": "Count words, characters, and lines in text"
            },
            {
                "id": "find_replace",
                "name": "Find & Replace",
                "description": "Find and replace text patterns"
            }
        ]
    
    def get_form_schema(self, mode):
        """Return form schema for the specified mode"""
        if mode == "count_words":
            return {
                "input_text": {
                    "type": "textarea",
                    "label": "Input Text",
                    "required": True,
                    "placeholder": "Enter text to analyze"
                }
            }
        elif mode == "find_replace":
            return {
                "input_text": {
                    "type": "textarea",
                    "label": "Input Text",
                    "required": True
                },
                "find_pattern": {
                    "type": "string",
                    "label": "Find Pattern",
                    "required": True
                },
                "replace_with": {
                    "type": "string",
                    "label": "Replace With",
                    "required": True
                }
            }
        return {}
    
    async def execute(self, mode, params, result_dir):
        """Execute the selected text processing mode"""
        if mode == "count_words":
            text = params.get("input_text", "")
            words = len(text.split())
            chars = len(text)
            lines = len(text.splitlines())
            
            return {
                "status": "completed",
                "word_count": words,
                "char_count": chars,
                "line_count": lines
            }
        elif mode == "find_replace":
            text = params.get("input_text", "")
            pattern = params.get("find_pattern", "")
            replacement = params.get("replace_with", "")
            
            result = text.replace(pattern, replacement)
            
            return {
                "status": "completed",
                "result": result
            }
        return {"error": "Invalid mode"}
```

## Creating a Binary-Based Gadget

Let's create a gadget that wraps around a command-line tool.

```python
"""
Network Scanner Gadget for Goblin Forge.

Provides network scanning capabilities using nmap.
"""
import asyncio
import json
from pathlib import Path
import logging

from goblin_forge.plugins.base_gadget import BaseGadget

logger = logging.getLogger(__name__)

class ScannerGadget(BaseGadget):
    """A gadget for network scanning"""
    name = "Network Scanner"
    description = "Scan networks and hosts"
    tab_id = "scanner"
    binary_name = "nmap"
    
    def get_modes(self):
        """Return available scanning modes"""
        return [
            {
                "id": "quick_scan",
                "name": "Quick Scan",
                "description": "Perform a quick port scan"
            },
            {
                "id": "full_scan",
                "name": "Full Scan",
                "description": "Perform a comprehensive scan"
            }
        ]
    
    def get_form_schema(self, mode):
        """Return form schema for the specified mode"""
        base_schema = {
            "target": {
                "type": "string",
                "label": "Target",
                "required": True,
                "placeholder": "IP address or hostname"
            }
        }
        
        if mode == "full_scan":
            return {
                **base_schema,
                "scan_type": {
                    "type": "select",
                    "label": "Scan Type",
                    "options": [
                        {"value": "tcp", "label": "TCP Scan"},
                        {"value": "udp", "label": "UDP Scan"}
                    ],
                    "default": "tcp"
                }
            }
        return base_schema
    
    async def execute(self, mode, params, result_dir):
        """Execute the selected scanning mode"""
        target = params.get("target")
        if not target:
            return {"error": "No target specified"}
            
        # Create result directory
        result_dir = Path(result_dir)
        result_dir.mkdir(exist_ok=True)
        
        # Build command based on mode
        if mode == "quick_scan":
            cmd = [self.binary_name, "-F", target]
        elif mode == "full_scan":
            scan_type = params.get("scan_type", "tcp")
            cmd = [self.binary_name, "-sS" if scan_type == "tcp" else "-sU", target]
        else:
            return {"error": "Invalid mode"}
            
        # Execute command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Save results
        result_file = result_dir / "scan_results.txt"
        with open(result_file, "wb") as f:
            f.write(stdout)
            
        return {
            "status": "completed",
            "result_file": str(result_file)
        }
```

## File Upload Feature

Goblin Forge supports file uploads through its API. Here's how to handle file uploads in your gadget:

```python
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
    name = "File Processor"
    description = "Process uploaded files with various operations"
    tab_id = "file_processor"
    
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
        # Move the uploaded file to the task's result directory
        input_file = params.get("input_file")
        if input_file:
            input_path = Path(input_file)
            if input_path.exists():
                # Create an 'input' subdirectory in the result directory
                input_dir = Path(result_dir) / "input"
                input_dir.mkdir(exist_ok=True)
                
                # Copy the file to the input directory
                new_path = input_dir / input_path.name
                shutil.copy2(input_file, new_path)
                
                # Update the input file path in params
                params["input_file"] = str(new_path)
        
        if mode == "file_analyzer":
            return await self._analyze_file(params, result_dir)
        elif mode == "file_converter":
            return await self._convert_file(params, result_dir)
        return {"error": "Invalid mode"}
```

## Best Practices

1. **Error Handling**:
   - Always validate input parameters
   - Use try-except blocks for file operations
   - Return meaningful error messages
   - Log errors appropriately

2. **Resource Management**:
   - Clean up temporary files
   - Use context managers for file operations
   - Monitor memory usage
   - Handle large files efficiently

3. **Security**:
   - Validate file paths
   - Sanitize user input
   - Use secure file permissions
   - Implement rate limiting if needed

4. **Performance**:
   - Use async/await for I/O operations
   - Implement caching where appropriate
   - Optimize file operations
   - Use efficient data structures

## Common Patterns

1. **File Processing**:
   ```python
   async def process_file(self, input_path, output_path):
       with open(input_path, 'rb') as infile:
           with open(output_path, 'wb') as outfile:
               # Process file
               pass
   ```

2. **Command Execution**:
   ```python
   async def run_command(self, cmd):
       process = await asyncio.create_subprocess_exec(
           *cmd,
           stdout=asyncio.subprocess.PIPE,
           stderr=asyncio.subprocess.PIPE
       )
       stdout, stderr = await process.communicate()
       return stdout, stderr
   ```

3. **Result Handling**:
   ```python
   def save_results(self, result_dir, data):
       result_file = Path(result_dir) / "results.json"
       with open(result_file, 'w') as f:
           json.dump(data, f, indent=2)
       return str(result_file)
   ```

## Testing

1. **Unit Tests**:
   ```python
   import pytest
   from goblin_forge.plugins.my_gadget import MyGadget
   
   def test_gadget_initialization():
       gadget = MyGadget()
       assert gadget.name == "My Gadget"
       assert gadget.tab_id == "my_gadget"
   
   def test_get_modes():
       gadget = MyGadget()
       modes = gadget.get_modes()
       assert len(modes) > 0
       assert all('id' in mode for mode in modes)
   ```

2. **Integration Tests**:
   ```python
   async def test_gadget_execution():
       gadget = MyGadget()
       with tempfile.TemporaryDirectory() as temp_dir:
           result = await gadget.execute(
               "test_mode",
               {"param": "value"},
               temp_dir
           )
           assert result["status"] == "completed"
   ```

## Security Considerations

1. **Input Validation**:
   - Validate all user input
   - Sanitize file paths
   - Check file permissions
   - Validate file types

2. **File Operations**:
   - Use secure file paths
   - Implement proper error handling
   - Clean up temporary files
   - Set appropriate file permissions

3. **Command Execution**:
   - Sanitize command arguments
   - Use absolute paths for binaries
   - Implement timeouts
   - Handle command failures

## Troubleshooting

1. **Common Issues**:
   - Plugin not appearing in UI
   - File upload failures
   - Command execution errors
   - Permission issues

2. **Debugging Tips**:
   - Check logs for errors
   - Verify file permissions
   - Test commands manually
   - Check network connectivity

3. **Performance Issues**:
   - Monitor resource usage
   - Check for memory leaks
   - Optimize file operations
   - Implement caching

## Glossary

- **Gadget**: A plugin that provides specific functionality
- **Mode**: A specific operation within a gadget
- **Minion**: A worker process that executes tasks
- **Result Directory**: Where task outputs are stored
- **Form Schema**: Definition of input fields for a mode