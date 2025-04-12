# Creating Plugins for Goblin Forge

Goblin Forge's plugin system, known as "Goblin Gadgets," makes it easy to add new tools to the platform. This guide will walk you through creating your own gadgets, whether they're pure Python implementations or wrappers around external binary tools.

## Table of Contents

1. [Understanding Goblin Gadgets](#understanding-goblin-gadgets)
2. [Creating a Pure Python Gadget](#creating-a-pure-python-gadget)
3. [Creating a Binary-Based Gadget](#creating-a-binary-based-gadget)
4. [Testing Your Gadget](#testing-your-gadget)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

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
            },
            {
                "id": "extract_emails",
                "name": "Extract Emails",
                "description": "Extract email addresses from text"
            },
            {
                "id": "sort_lines",
                "name": "Sort Lines",
                "description": "Sort lines alphabetically"
            }
        ]
    
    def get_form_schema(self, mode):
        """Return form schema for the specified mode"""
        # Base field for most modes
        base_schema = {
            "input_text": {
                "type": "textarea",
                "label": "Input Text",
                "required": True,
                "placeholder": "Enter text to process",
                "description": "The text you want to analyze or transform"
            }
        }
        
        # Mode-specific fields
        if mode == "find_replace":
            return {
                **base_schema,
                "find_pattern": {
                    "type": "string",
                    "label": "Find Pattern",
                    "required": True,
                    "placeholder": "Text to find",
                    "description": "The text or regular expression to find"
                },
                "replace_with": {
                    "type": "string",
                    "label": "Replace With",
                    "required": True,
                    "placeholder": "Text to replace with",
                    "description": "The text to replace matches with"
                },
                "use_regex": {
                    "type": "select",
                    "label": "Use Regular Expressions",
                    "options": [
                        {"value": "yes", "label": "Yes"},
                        {"value": "no", "label": "No"}
                    ],
                    "default": "no",
                    "description": "Whether to interpret the find pattern as a regular expression"
                }
            }
        elif mode == "sort_lines":
            return {
                **base_schema,
                "sort_order": {
                    "type": "select",
                    "label": "Sort Order",
                    "options": [
                        {"value": "asc", "label": "Ascending (A-Z)"},
                        {"value": "desc", "label": "Descending (Z-A)"}
                    ],
                    "default": "asc",
                    "description": "The order in which to sort the lines"
                },
                "ignore_case": {
                    "type": "select",
                    "label": "Ignore Case",
                    "options": [
                        {"value": "yes", "label": "Yes"},
                        {"value": "no", "label": "No"}
                    ],
                    "default": "yes",
                    "description": "Whether to ignore case when sorting"
                }
            }
        
        return base_schema
    
    async def execute(self, mode, params, result_dir):
        """Execute the selected text processing mode"""
        # Create result directory if it doesn't exist
        result_dir = Path(result_dir)
        result_dir.mkdir(exist_ok=True, parents=True)
        
        # Get input text
        input_text = params.get("input_text", "")
        if not input_text:
            return {
                "status": "error",
                "error": "No input text provided"
            }
        
        # Process based on mode
        result = ""
        metadata = {}
        
        try:
            if mode == "count_words":
                # Count words, characters, and lines
                words = len(input_text.split())
                chars = len(input_text)
                lines = len(input_text.splitlines())
                
                result = f"Word count: {words}\nCharacter count: {chars}\nLine count: {lines}"
                metadata = {
                    "word_count": words,
                    "character_count": chars,
                    "line_count": lines
                }
                
            elif mode == "find_replace":
                # Get parameters
                find_pattern = params.get("find_pattern", "")
                replace_with = params.get("replace_with", "")
                use_regex = params.get("use_regex", "no") == "yes"
                
                if use_regex:
                    # Use regular expression
                    result = re.sub(find_pattern, replace_with, input_text)
                    replacements = len(re.findall(find_pattern, input_text))
                else:
                    # Simple string replacement
                    result = input_text.replace(find_pattern, replace_with)
                    replacements = input_text.count(find_pattern)
                
                metadata = {
                    "pattern": find_pattern,
                    "replacement": replace_with,
                    "regex_used": use_regex,
                    "replacements_made": replacements
                }
                
            elif mode == "extract_emails":
                # Extract email addresses using regex
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, input_text)
                
                result = "\n".join(emails)
                metadata = {
                    "emails_found": len(emails),
                    "unique_emails": len(set(emails))
                }
                
            elif mode == "sort_lines":
                # Get parameters
                sort_order = params.get("sort_order", "asc")
                ignore_case = params.get("ignore_case", "yes") == "yes"
                
                # Split into lines and filter out empty ones
                lines = [line for line in input_text.splitlines() if line.strip()]
                
                # Sort based on parameters
                if ignore_case:
                    lines.sort(key=lambda x: x.lower())
                else:
                    lines.sort()
                
                # Reverse if descending order
                if sort_order == "desc":
                    lines.reverse()
                
                result = "\n".join(lines)
                metadata = {
                    "line_count": len(lines),
                    "sort_order": sort_order,
                    "case_sensitive": not ignore_case
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown mode: {mode}"
                }
        
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return {
                "status": "error",
                "error": f"Error processing text: {str(e)}"
            }
        
        # Write results to files
        output_file = result_dir / "result.txt"
        with open(output_file, 'w') as f:
            f.write(result)
        
        metadata_file = result_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Return success with result information
        return {
            "status": "completed",
            "result_file": str(output_file),
            "result_preview": result[:500] + ("..." if len(result) > 500 else ""),
            "metadata": metadata
        }
```

### Step 2: Register the Gadget

Your gadget will be automatically discovered by Goblin Forge's plugin loader as long as:

1. It's in the `goblin_forge/plugins/` directory
2. It inherits from `BaseGadget`
3. It's not named `base_gadget.py`

There's no need for explicit registration.

## Creating a Binary-Based Gadget

Now let's create a gadget that wraps around an external binary tool (in this case, ImageMagick's `convert` utility).

### Step 1: Create a new Python file

Create a file named `image_converter_gadget.py` in the `goblin_forge/plugins/` directory:

```python
"""
Image Converter Gadget for Goblin Forge.

Provides image conversion and manipulation capabilities via ImageMagick.
"""
import os
import asyncio
import json
from pathlib import Path
import logging
import shutil

from goblin_forge.plugins.base_gadget import BaseGadget

logger = logging.getLogger(__name__)

class ImageConverterGadget(BaseGadget):
    """Image conversion and manipulation using ImageMagick"""
    name = "Image Converter"
    description = "Convert and manipulate images using ImageMagick"
    tab_id = "image_converter"
    binary_name = "convert"  # ImageMagick's convert command
    
    def get_modes(self):
        """Return available image processing modes"""
        return [
            {
                "id": "convert_format",
                "name": "Convert Format",
                "description": "Convert an image to a different format"
            },
            {
                "id": "resize_image",
                "name": "Resize Image",
                "description": "Resize an image to specific dimensions"
            },
            {
                "id": "apply_filter",
                "name": "Apply Filter",
                "description": "Apply visual filters to an image"
            },
            {
                "id": "add_text",
                "name": "Add Text",
                "description": "Add text overlay to an image"
            }
        ]
    
    def get_form_schema(self, mode):
        """Return form schema for the specified mode"""
        # Base field for all modes
        base_schema = {
            "input_file": {
                "type": "string",
                "label": "Input Image Path",
                "required": True,
                "placeholder": "/path/to/image.jpg",
                "description": "Path to the image you want to process"
            }
        }
        
        # Mode-specific fields
        if mode == "convert_format":
            return {
                **base_schema,
                "output_format": {
                    "type": "select",
                    "label": "Output Format",
                    "options": [
                        {"value": "jpg", "label": "JPEG"},
                        {"value": "png", "label": "PNG"},
                        {"value": "gif", "label": "GIF"},
                        {"value": "bmp", "label": "BMP"},
                        {"value": "tiff", "label": "TIFF"}
                    ],
                    "default": "png",
                    "description": "The format to convert the image to"
                },
                "quality": {
                    "type": "string",
                    "label": "Quality (1-100)",
                    "required": False,
                    "placeholder": "90",
                    "default": "90",
                    "description": "Quality setting for the output image (for JPEG, PNG)"
                }
            }
        elif mode == "resize_image":
            return {
                **base_schema,
                "width": {
                    "type": "string",
                    "label": "Width (pixels)",
                    "required": True,
                    "placeholder": "800",
                    "description": "Desired width in pixels"
                },
                "height": {
                    "type": "string",
                    "label": "Height (pixels)",
                    "required": True,
                    "placeholder": "600",
                    "description": "Desired height in pixels"
                },
                "maintain_aspect": {
                    "type": "select",
                    "label": "Maintain Aspect Ratio",
                    "options": [
                        {"value": "yes", "label": "Yes"},
                        {"value": "no", "label": "No"}
                    ],
                    "default": "yes",
                    "description": "Whether to maintain the original aspect ratio"
                }
            }
        elif mode == "apply_filter":
            return {
                **base_schema,
                "filter_type": {
                    "type": "select",
                    "label": "Filter Type",
                    "options": [
                        {"value": "grayscale", "label": "Grayscale"},
                        {"value": "sepia", "label": "Sepia Tone"},
                        {"value": "blur", "label": "Blur"},
                        {"value": "sharpen", "label": "Sharpen"},
                        {"value": "edge", "label": "Edge Detection"}
                    ],
                    "default": "grayscale",
                    "description": "The type of filter to apply"
                },
                "intensity": {
                    "type": "string",
                    "label": "Intensity (1-10)",
                    "required": False,
                    "placeholder": "5",
                    "default": "5",
                    "description": "Intensity of the filter effect (for applicable filters)"
                }
            }
        elif mode == "add_text":
            return {
                **base_schema,
                "text_content": {
                    "type": "string",
                    "label": "Text Content",
                    "required": True,
                    "placeholder": "Your text here",
                    "description": "The text to add to the image"
                },
                "position": {
                    "type": "select",
                    "label": "Position",
                    "options": [
                        {"value": "top", "label": "Top"},
                        {"value": "center", "label": "Center"},
                        {"value": "bottom", "label": "Bottom"}
                    ],
                    "default": "bottom",
                    "description": "Where to place the text"
                },
                "font_size": {
                    "type": "string",
                    "label": "Font Size",
                    "required": False,
                    "placeholder": "24",
                    "default": "24",
                    "description": "Size of the font in points"
                },
                "font_color": {
                    "type": "string",
                    "label": "Font Color",
                    "required": False,
                    "placeholder": "white",
                    "default": "white",
                    "description": "Color name or hex code for the text"
                }
            }
        
        return base_schema
    
    async def execute(self, mode, params, result_dir):
        """Execute the image processing operation"""
        # Create result directory if it doesn't exist
        result_dir = Path(result_dir)
        result_dir.mkdir(exist_ok=True, parents=True)
        
        # Get the path to the convert binary
        convert_bin = self.get_binary_path()
        if not convert_bin:
            return {
                "status": "error",
                "error": "ImageMagick 'convert' binary not found"
            }
        
        # Get input file and validate
        input_file = params.get("input_file", "")
        if not input_file or not os.path.exists(input_file):
            return {
                "status": "error",
                "error": f"Input file not found: {input_file}"
            }
        
        # Determine output file name
        input_path = Path(input_file)
        output_file = None
        cmd = [convert_bin]
        
        try:
            # Configure command based on mode
            if mode == "convert_format":
                output_format = params.get("output_format", "png")
                quality = params.get("quality", "90")
                
                output_file = result_dir / f"converted.{output_format}"
                cmd.extend([
                    input_file,
                    "-quality", quality,
                    str(output_file)
                ])
                
            elif mode == "resize_image":
                width = params.get("width", "800")
                height = params.get("height", "600")
                maintain_aspect = params.get("maintain_aspect", "yes") == "yes"
                
                output_file = result_dir / f"resized{input_path.suffix}"
                
                if maintain_aspect:
                    cmd.extend([
                        input_file,
                        "-resize", f"{width}x{height}",
                        str(output_file)
                    ])
                else:
                    cmd.extend([
                        input_file,
                        "-resize", f"{width}x{height}!",
                        str(output_file)
                    ])
                
            elif mode == "apply_filter":
                filter_type = params.get("filter_type", "grayscale")
                intensity = params.get("intensity", "5")
                
                output_file = result_dir / f"filtered{input_path.suffix}"
                
                if filter_type == "grayscale":
                    cmd.extend([
                        input_file,
                        "-colorspace", "Gray",
                        str(output_file)
                    ])
                elif filter_type == "sepia":
                    cmd.extend([
                        input_file,
                        "-sepia-tone", f"{intensity}0%",
                        str(output_file)
                    ])
                elif filter_type == "blur":
                    cmd.extend([
                        input_file,
                        "-blur", f"0x{intensity}",
                        str(output_file)
                    ])
                elif filter_type == "sharpen":
                    cmd.extend([
                        input_file,
                        "-sharpen", f"0x{intensity}",
                        str(output_file)
                    ])
                elif filter_type == "edge":
                    cmd.extend([
                        input_file,
                        "-edge", intensity,
                        str(output_file)
                    ])
                
            elif mode == "add_text":
                text_content = params.get("text_content", "")
                position = params.get("position", "bottom")
                font_size = params.get("font_size", "24")
                font_color = params.get("font_color", "white")
                
                output_file = result_dir / f"text_overlay{input_path.suffix}"
                
                # Map position to gravity
                gravity_map = {
                    "top": "North",
                    "center": "Center",
                    "bottom": "South"
                }
                gravity = gravity_map.get(position, "South")
                
                cmd.extend([
                    input_file,
                    "-gravity", gravity,
                    "-pointsize", font_size,
                    "-fill", font_color,
                    "-annotate", "+0+20", text_content,
                    str(output_file)
                ])
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown mode: {mode}"
                }
            
            # Log the command
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Check for errors
            if process.returncode != 0:
                logger.error(f"Error processing image: {stderr.decode()}")
                error_file = result_dir / "error.txt"
                with open(error_file, 'w') as f:
                    f.write(stderr.decode())
                
                return {
                    "status": "error",
                    "error": f"Error processing image: {stderr.decode()}",
                    "command": " ".join(cmd)
                }
            
            # Save a copy of the original image for comparison
            original_copy = result_dir / f"original{input_path.suffix}"
            shutil.copy2(input_file, original_copy)
            
            # Create metadata
            metadata = {
                "input_file": input_file,
                "output_file": str(output_file),
                "mode": mode,
                "parameters": params,
                "command": " ".join(cmd)
            }
            
            metadata_file = result_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Return success
            return {
                "status": "completed",
                "result_file": str(output_file),
                "original_file": str(original_copy),
                "metadata": metadata,
                "command": " ".join(cmd)
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                "status": "error",
                "error": f"Error processing image: {str(e)}",
                "command": " ".join(cmd) if cmd else "No command generated"
            }
```

### Step 2: Ensure Binary Availability

For binary-based gadgets to work, the binary must be installed and accessible on the system. In this case, you need ImageMagick installed.

- **Linux**: `sudo apt install imagemagick`
- **macOS**: `brew install imagemagick`
- **Windows**: Download and install from the [ImageMagick website](https://imagemagick.org/script/download.php)

The `BaseGadget` class handles checking for the binary and will automatically look for it in your system's PATH or at the specified `binary_path`.

## Testing Your Gadget

### Manual Testing

1. Start or restart the Goblin Forge application
2. Check if your gadget appears in the tabs
3. Try each mode with sample inputs
4. Verify that the results are correct

### Writing Unit Tests

Create a test file in the `tests/` directory:

```python
# test_text_processor.py
import asyncio
import tempfile
from pathlib import Path

from goblin_forge.plugins.text_processor_gadget import TextProcessorGadget

def test_word_count():
    gadget = TextProcessorGadget()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        params = {
            "input_text": "This is a test.\nIt has two lines and nine words."
        }
        
        result = asyncio.run(gadget.execute("count_words", params, temp_dir))
        
        assert result["status"] == "completed"
        assert "Word count: 9" in result["result_preview"]
        assert result["metadata"]["word_count"] == 9
        assert result["metadata"]["line_count"] == 2
```

## Advanced Features

### Adding Custom Validation

You can add custom validation logic to check user inputs before execution:

```python
def validate_params(self, mode, params):
    """Validate parameters before execution"""
    if mode == "resize_image":
        try:
            width = int(params.get("width", ""))
            height = int(params.get("height", ""))
            
            if width <= 0 or height <= 0:
                return False, "Width and height must be positive numbers"
                
            if width > 10000 or height > 10000:
                return False, "Width and height cannot exceed 10000 pixels"
                
        except ValueError:
            return False, "Width and height must be valid numbers"
    
    return True, "Parameters are valid"
```

Then call this from your `execute` method:

```python
# In execute method
valid, message = self.validate_params(mode, params)
if not valid:
    return {
        "status": "error",
        "error": message
    }
```

### Adding Progress Reporting

For long-running tasks, you can provide progress updates:

```python
# In a long-running part of your execute method
progress_file = result_dir / "progress.json"
for i in range(10):
    # Do a part of the work...
    
    # Update progress
    with open(progress_file, 'w') as f:
        json.dump({
            "progress": (i + 1) * 10,
            "status": "Processing..."
        }, f)
    
    await asyncio.sleep(1)  # Simulate work
```

## Troubleshooting

### Common Issues

1. **Gadget Not Appearing**: Make sure your class inherits from `BaseGadget` and is in the correct directory.

2. **Binary Not Found**: Check that the binary is installed and in your PATH. You can specify a custom path with `binary_path`.

3. **Execution Errors**: Check your error handling. All exceptions should be caught and returned with a meaningful error message.

4. **Parameter Issues**: Ensure that your `get_form_schema` method returns the correct schema for each mode and that required parameters are validated.

### Debugging Tips

1. **Logging**: Use the `logger` to log important information:
   ```python
   logger.debug("Detailed debug info")
   logger.info("General information")
   logger.warning("Warning message")
   logger.error("Error message")
   ```

2. **Result Directory**: Inspect the files in the result directory for clues about what went wrong.

3. **Manual Testing**: Try executing your binary commands manually to check if they work as expected.

4. **Check Return Values**: Make sure your `execute` method always returns a dictionary with at least a `status` key.

---

By following this guide, you should be able to create and integrate both Python-based and binary-based gadgets into the Goblin Forge platform. The plugin system is designed to be flexible, allowing you to wrap virtually any tool or functionality into a user-friendly interface.