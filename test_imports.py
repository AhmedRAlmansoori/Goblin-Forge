"""
Test script to verify imports are working correctly.
"""

try:
    from goblin_forge.core.plugin_loader import PluginLoader
    from goblin_forge.core.minion_manager import MinionManager
    from goblin_forge.plugins.base_gadget import BaseGadget
    
    print("Import test successful! Your package structure is working correctly.")
    
    # Test plugin loader
    loader = PluginLoader()
    gadgets = loader.discover_gadgets()
    print(f"Found {len(gadgets)} gadgets:")
    for gadget_class in gadgets:
        print(f"  - {gadget_class.name} ({gadget_class.tab_id})")
    
except ImportError as e:
    print(f"Import test failed: {e}")
    print("Check your directory structure and __init__.py files.")