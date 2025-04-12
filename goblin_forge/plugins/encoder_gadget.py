"""
Encoder & Decoder Gadget for Goblin Forge.

Provides text encoding and decoding capabilities in various formats.
"""
import os
import base64
import urllib.parse
import json
import hashlib
from pathlib import Path

from goblin_forge.plugins.base_gadget import BaseGadget

class EncoderGadget(BaseGadget):
    """Example encoder/decoder gadget"""
    name = "Encoder & Decoder"
    description = "Encodes and decodes text in various formats"
    tab_id = "encoder"
    # This gadget doesn't use an external binary, so we don't set binary_name
    
    def get_modes(self):
        """Return available encoding/decoding modes"""
        return [
            {
                "id": "base64_encode",
                "name": "Base64 Encode",
                "description": "Encode text to Base64"
            },
            {
                "id": "base64_decode",
                "name": "Base64 Decode",
                "description": "Decode Base64 to text"
            },
            {
                "id": "hex_encode",
                "name": "Hex Encode",
                "description": "Encode text to hexadecimal"
            },
            {
                "id": "hex_decode",
                "name": "Hex Decode",
                "description": "Decode hexadecimal to text"
            },
            {
                "id": "url_encode",
                "name": "URL Encode",
                "description": "Encode text for URLs"
            },
            {
                "id": "url_decode",
                "name": "URL Decode",
                "description": "Decode URL-encoded text"
            },
            {
                "id": "hash_md5",
                "name": "Hash (MD5)",
                "description": "Generate MD5 hash of text"
            },
            {
                "id": "hash_sha256",
                "name": "Hash (SHA-256)",
                "description": "Generate SHA-256 hash of text"
            }
        ]
    
    def get_form_schema(self, mode):
        """Return form schema for the specified mode"""
        if "decode" in mode:
            return {
                "input": {
                    "type": "textarea",
                    "label": "Encoded Text",
                    "required": True,
                    "placeholder": "Enter encoded text to decode",
                    "description": "The text you want to decode"
                }
            }
        elif "hash" in mode:
            return {
                "input": {
                    "type": "textarea",
                    "label": "Text to Hash",
                    "required": True,
                    "placeholder": "Enter text to hash",
                    "description": "The text you want to generate a hash for"
                }
            }
        else:
            return {
                "input": {
                    "type": "textarea",
                    "label": "Text to Encode",
                    "required": True,
                    "placeholder": "Enter text to encode",
                    "description": "The text you want to encode"
                }
            }
    
    async def execute(self, mode, params, result_dir):
        """Execute encoding/decoding operation"""
        result_dir = Path(result_dir)
        result_dir.mkdir(exist_ok=True, parents=True)
        
        input_text = params.get("input", "")
        result = ""
        error = None
        
        # Process based on mode
        try:
            if mode == "base64_encode":
                result = base64.b64encode(input_text.encode()).decode()
            elif mode == "base64_decode":
                result = base64.b64decode(input_text.encode()).decode()
            elif mode == "hex_encode":
                result = input_text.encode().hex()
            elif mode == "hex_decode":
                result = bytes.fromhex(input_text).decode()
            elif mode == "url_encode":
                result = urllib.parse.quote(input_text)
            elif mode == "url_decode":
                result = urllib.parse.unquote(input_text)
            elif mode == "hash_md5":
                result = hashlib.md5(input_text.encode()).hexdigest()
            elif mode == "hash_sha256":
                result = hashlib.sha256(input_text.encode()).hexdigest()
            else:
                error = f"Unknown mode: {mode}"
        except Exception as e:
            error = f"Error processing {mode}: {str(e)}"
            result = "ERROR: " + str(e)
        
        # Save result
        output_file = result_dir / "result.txt"
        with open(output_file, 'w') as f:
            f.write(result)
        
        # Save metadata
        metadata = {
            "mode": mode,
            "input_length": len(input_text),
            "output_length": len(result),
            "error": error
        }
        
        metadata_file = result_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "status": "completed" if not error else "error",
            "result_file": str(output_file),
            "result_preview": result[:100] + ("..." if len(result) > 100 else ""),
            "error": error
        }

    async def get_result_details(self, result_dir):
        """Get detailed information about the result"""
        result_dir = Path(result_dir)
        
        # Read the result file
        result_file = result_dir / "result.txt"
        if not result_file.exists():
            return {"error": "Result file not found"}
        
        with open(result_file, 'r') as f:
            result_content = f.read()
        
        # Read metadata if available
        metadata_file = result_dir / "metadata.json"
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except:
                pass
        
        return {
            "mode": metadata.get("mode", "unknown"),
            "input_length": metadata.get("input_length", 0),
            "output_length": metadata.get("output_length", len(result_content)),
            "result": result_content,
            "error": metadata.get("error")
        }