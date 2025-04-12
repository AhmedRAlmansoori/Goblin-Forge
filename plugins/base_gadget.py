# base_gadget.py - The interface all Goblin Gadgets must implement
# class BaseGadget:
#     name = "Base Gadget"  # Display name
#     description = "Base class for all Goblin Gadgets"
#     tab_id = "base"  # Unique ID for the tab

#     # Define available execution modes
#     def get_modes(self):
#         """Return a list of available execution modes"""
#         return []
    
#     # Define form schema for each mode
#     def get_form_schema(self, mode):
#         """Return JSON schema for form inputs for the given mode"""
#         return {}
    
#     # Execute the binary with given mode and parameters
#     async def execute(self, mode, params, result_dir):
#         """Execute the binary with specified mode and parameters"""
#         raise NotImplementedError("Subclasses must implement execute()")

# base_gadget.py - The interface all Goblin Gadgets must implement
import shutil
import os
from pathlib import Path

class BaseGadget:
    name = "Base Gadget"  # Display name
    description = "Base class for all Goblin Gadgets"
    tab_id = "base"  # Unique ID for the tab
    binary_path = None  # Path to the binary (if applicable)
    binary_name = None  # Name of the binary executable

    def __init__(self):
        """Initialize the gadget and validate binary if specified"""
        if self.binary_name:
            self._validate_binary()

    def _validate_binary(self):
        """Validate that the binary exists and is executable"""
        # If binary_path is specified, check that path directly
        if self.binary_path:
            binary_full_path = Path(self.binary_path) / self.binary_name if self.binary_name else Path(self.binary_path)
            if not binary_full_path.exists():
                raise FileNotFoundError(f"Binary not found at specified path: {binary_full_path}")
            if not os.access(binary_full_path, os.X_OK):
                raise PermissionError(f"Binary is not executable: {binary_full_path}")
            return str(binary_full_path)
            
        # Otherwise, check if binary is in PATH
        binary_in_path = shutil.which(self.binary_name)
        if not binary_in_path:
            raise FileNotFoundError(f"Binary '{self.binary_name}' not found in PATH")
        return binary_in_path

    def get_binary_path(self):
        """Get the full path to the binary"""
        if not self.binary_name:
            return None
            
        if self.binary_path:
            return str(Path(self.binary_path) / self.binary_name)
            
        return shutil.which(self.binary_name)

    # Define available execution modes
    def get_modes(self):
        """Return a list of available execution modes"""
        return []
    
    # Define form schema for each mode
    def get_form_schema(self, mode):
        """Return JSON schema for form inputs for the given mode"""
        return {}
    
    # Execute the binary with given mode and parameters
    async def execute(self, mode, params, result_dir):
        """Execute the binary with specified mode and parameters"""
        raise NotImplementedError("Subclasses must implement execute()")