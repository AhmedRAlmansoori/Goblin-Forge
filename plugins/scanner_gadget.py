"""
Scanner Gadget for Goblin Forge.

Provides network scanning capabilities via a user-friendly interface.
"""
import os
import asyncio
import subprocess
from pathlib import Path
import json
import logging

from goblin_forge.plugins.base_gadget import BaseGadget

logger = logging.getLogger(__name__)

class ScannerGadget(BaseGadget):
    """Example scanner gadget that demonstrates the Goblin Gadget interface"""
    name = "Network Scanner"
    description = "Scans networks and hosts for open ports and services"
    tab_id = "scanner"
    binary_name = "nmap"  # Executable name (will search in PATH)
    
    def get_modes(self):
        """Return available scanning modes"""
        return [
            {
                "id": "quick_scan",
                "name": "Quick Scan",
                "description": "Fast scan of common ports on a target"
            },
            {
                "id": "full_scan",
                "name": "Full Scan",
                "description": "Complete port scan with service detection"
            },
            {
                "id": "vuln_scan",
                "name": "Vulnerability Scan",
                "description": "Scan for common vulnerabilities"
            },
            {
                "id": "stealth_scan",
                "name": "Stealth Scan",
                "description": "Perform a quiet, stealthy scan"
            },
            {
                "id": "os_detection",
                "name": "OS Detection",
                "description": "Detect operating system of target"
            },
            {
                "id": "custom_scan",
                "name": "Custom Scan",
                "description": "Scan with custom parameters"
            }
        ]
    
    def get_form_schema(self, mode):
        """Return form schema for the specified mode"""
        # Base fields for all modes
        base_schema = {
            "target": {
                "type": "string",
                "label": "Target IP/Hostname",
                "required": True,
                "placeholder": "192.168.1.1 or example.com",
                "description": "IP address or hostname to scan"
            }
        }
        
        # Mode-specific fields
        if mode == "quick_scan":
            return base_schema
            
        elif mode == "full_scan":
            return {
                **base_schema,
                "port_range": {
                    "type": "string",
                    "label": "Port Range",
                    "required": False,
                    "placeholder": "1-65535",
                    "default": "1-1000",
                    "description": "Range of ports to scan (e.g., 1-1000, 80,443,8080)"
                }
            }
            
        elif mode == "vuln_scan":
            return {
                **base_schema,
                "vuln_categories": {
                    "type": "multiselect",
                    "label": "Vulnerability Categories",
                    "options": [
                        {"value": "web", "label": "Web Vulnerabilities"},
                        {"value": "sql", "label": "SQL Injection"},
                        {"value": "rce", "label": "Remote Code Execution"},
                        {"value": "default", "label": "Default Credentials"}
                    ],
                    "default": ["web"],
                    "description": "Types of vulnerabilities to scan for"
                }
            }
            
        elif mode == "stealth_scan":
            return {
                **base_schema,
                "timing": {
                    "type": "select",
                    "label": "Scan Timing",
                    "options": [
                        {"value": "paranoid", "label": "Paranoid (0)"},
                        {"value": "sneaky", "label": "Sneaky (1)"},
                        {"value": "polite", "label": "Polite (2)"},
                        {"value": "normal", "label": "Normal (3)"}
                    ],
                    "default": "sneaky",
                    "description": "Speed and aggressiveness of the scan"
                }
            }
            
        elif mode == "os_detection":
            return base_schema
            
        elif mode == "custom_scan":
            return {
                **base_schema,
                "custom_args": {
                    "type": "string",
                    "label": "Custom Arguments",
                    "required": True,
                    "placeholder": "-sS -sV -p 22,80,443",
                    "description": "Custom scan arguments"
                }
            }
            
        return base_schema
    
    async def execute(self, mode, params, result_dir):
        """Execute the scanner with specified mode and parameters"""
        # Create result directory if it doesn't exist
        result_dir = Path(result_dir)
        result_dir.mkdir(exist_ok=True, parents=True)
        
        # Save parameters for reference
        params_file = result_dir / "params.json"
        with open(params_file, 'w') as f:
            json.dump({
                "mode": mode,
                "params": params
            }, f, indent=2)
        
        # Build command based on mode and parameters
        target = params.get("target", "localhost")
        nmap_path = self.get_binary_path()
        cmd = [nmap_path]  # Use the validated binary path
        
        if mode == "quick_scan":
            cmd.extend(["-F", target])
        elif mode == "full_scan":
            port_range = params.get("port_range", "1-1000")
            cmd.extend(["-p", port_range, "-sV", target])
        elif mode == "vuln_scan":
            categories = params.get("vuln_categories", ["web"])
            cmd.extend(["--script=vuln", target])
        elif mode == "stealth_scan":
            timing = params.get("timing", "sneaky")
            timing_map = {
                "paranoid": "0", "sneaky": "1", 
                "polite": "2", "normal": "3"
            }
            cmd.extend([f"-T{timing_map.get(timing, '1')}", "-sS", target])
        elif mode == "os_detection":
            cmd.extend(["-O", target])
        elif mode == "custom_scan":
            custom_args = params.get("custom_args", "")
            cmd = [nmap_path] + custom_args.split() + [target]
        
        # Log the command
        logger.info(f"Executing scan command: {' '.join(cmd)}")
        
        output_file = result_dir / "scan_results.txt"
        error_file = result_dir / "scan_errors.txt"
        
        try:
            # Execute nmap command with actual binary
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Write output to file
            with open(output_file, 'wb') as f:
                f.write(stdout)
            
            if stderr:
                with open(error_file, 'wb') as f:
                    f.write(stderr)
            
            # Create a summary file
            summary_file = result_dir / "summary.json"
            with open(summary_file, 'w') as f:
                json.dump({
                    "target": target,
                    "command": " ".join(cmd),
                    "mode": mode,
                    "status": "completed" if process.returncode == 0 else "error",
                    "return_code": process.returncode,
                    "result_files": [
                        {"name": "scan_results.txt", "path": str(output_file)}
                    ]
                }, f, indent=2)
            
            return {
                "status": "completed" if process.returncode == 0 else "error",
                "result_file": str(output_file),
                "command": " ".join(cmd),
                "return_code": process.returncode
            }
            
        except Exception as e:
            # Handle execution errors
            error_msg = f"Error executing scan: {str(e)}"
            logger.error(error_msg)
            
            # Write error to file
            with open(error_file, 'w') as f:
                f.write(error_msg)
            
            return {
                "status": "error",
                "error": error_msg,
                "command": " ".join(cmd)
            }

    # Optional method to provide a summary of results
    async def summarize_results(self, result_dir):
        """Generate a human-readable summary of scan results"""
        result_dir = Path(result_dir)
        output_file = result_dir / "scan_results.txt"
        
        if not output_file.exists():
            return {"error": "Results file not found"}
        
        # Read output file
        with open(output_file, 'r') as f:
            content = f.read()
        
        # Extract basic information
        lines = content.split('\n')
        target = None
        command = None
        mode = None
        
        for line in lines:
            if line.startswith("# Scan Results for"):
                target = line.replace("# Scan Results for", "").strip()
            elif line.startswith("# Command:"):
                command = line.replace("# Command:", "").strip()
            elif line.startswith("# Mode:"):
                mode = line.replace("# Mode:", "").strip()
        
        # Extract ports (very basic parsing)
        ports = []
        for line in lines:
            if "/tcp" in line or "/udp" in line:
                parts = line.split()
                if len(parts) >= 3:
                    ports.append({
                        "port": parts[0],
                        "state": parts[1],
                        "service": parts[2]
                    })
        
        return {
            "target": target,
            "mode": mode,
            "ports_found": len(ports),
            "open_ports": ports,
            "command": command
        }