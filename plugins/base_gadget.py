# base_gadget.py - The interface all Goblin Gadgets must implement
class BaseGadget:
    name = "Base Gadget"  # Display name
    description = "Base class for all Goblin Gadgets"
    tab_id = "base"  # Unique ID for the tab

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