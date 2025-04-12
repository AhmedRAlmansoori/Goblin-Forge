import os
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Type

# Import base gadget class
from goblin_forge.plugins.base_gadget import BaseGadget

class PluginLoader:
    """Loads and manages Goblin Gadget plugins"""
    
    def __init__(self, plugin_dir: str = "goblin_forge/plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.gadgets: Dict[str, Type[BaseGadget]] = {}
        
    def discover_gadgets(self) -> List[Type[BaseGadget]]:
        """Discover all Goblin Gadget plugins in the plugin directory"""
        print(f"Scanning for gadgets in {self.plugin_dir}")
        # Skip if we're looking at the base module itself
        self._scan_directory(self.plugin_dir)
        print(f"Found {len(self.gadgets)} gadgets: {list(self.gadgets.keys())}")
        return list(self.gadgets.values())
    
    def _scan_directory(self, directory: Path) -> None:
        """Recursively scan directory for Python modules containing gadgets"""
        for item in directory.iterdir():
            # Skip __pycache__ and similar directories
            if item.name.startswith('__'):
                continue
                
            if item.is_dir():
                # Check if this is a Python package (has __init__.py)
                if (item / "__init__.py").exists():
                    self._scan_directory(item)
            elif item.suffix == '.py' and item.name != "base_gadget.py":
                self._load_gadget_from_file(item)
    
    def _load_gadget_from_file(self, file_path: Path) -> None:
        """Load gadgets from a Python file"""
        # Create module name from file path
        relative_path = file_path.relative_to(self.plugin_dir.parent)
        module_name = '.'.join(relative_path.with_suffix('').parts)
        
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                print(f"Failed to load spec for {file_path}")
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find all gadget classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseGadget) and 
                    obj is not BaseGadget):
                    gadget_id = obj.tab_id
                    self.gadgets[gadget_id] = obj
                    print(f"Loaded gadget: {obj.name} ({gadget_id})")
        except Exception as e:
            print(f"Error loading gadget from {file_path}: {e}")
    
    def get_gadget(self, gadget_id: str) -> Type[BaseGadget]:
        """Get a specific gadget by ID"""
        return self.gadgets.get(gadget_id)
    
    def instantiate_gadget(self, gadget_id: str) -> BaseGadget:
        """Instantiate a gadget by ID"""
        gadget_class = self.get_gadget(gadget_id)
        if gadget_class:
            return gadget_class()
        return None
