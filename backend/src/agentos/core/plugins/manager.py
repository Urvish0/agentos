import importlib.util
import os
import sys
import inspect
import logging
from typing import Dict, List, Type, Any
from .base import BasePlugin, PluginType

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Manages the discovery, loading, and lifecycle of AgentOS plugins.
    """

    def __init__(self):
        self.plugins: Dict[PluginType, List[BasePlugin]] = {
            ptype: [] for ptype in PluginType
        }
        self._loaded_paths: set = set()

    def discover_and_load(self, plugins_dir: str):
        """Scan a directory and load all valid plugins found."""
        if not os.path.exists(plugins_dir):
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return

        # Add plugins_dir to sys.path so plugins can import each other if needed
        if plugins_dir not in sys.path:
            sys.path.append(plugins_dir)

        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                file_path = os.path.join(plugins_dir, filename)
                self.load_plugin(file_path)

    def load_plugin(self, file_path: str):
        """Dynamically load classes from a python file that inherit from BasePlugin."""
        if file_path in self._loaded_paths:
            return
        
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Inspect the module for classes inheriting from BasePlugin
            found = False
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj is not BasePlugin and 
                    not inspect.isabstract(obj)):
                    
                    logger.info(f"Found plugin class: {name} in {file_path}")
                    instance = obj()
                    self.register_plugin(instance)
                    found = True
            
            if not found:
                logger.warning(f"No valid BasePlugin subclasses found in {file_path}")
            
            if found:
                self._loaded_paths.add(file_path)
                logger.info(f"Successfully loaded plugin(s) from: {file_path}")

        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {e}")

    def register_plugin(self, plugin: BasePlugin):
        """Manually register a plugin instance."""
        self.plugins[plugin.plugin_type].append(plugin)
        plugin.on_load()
        logger.info(f"Registered {plugin.plugin_type.value} plugin: {plugin.name} v{plugin.version}")

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """Return all loaded plugins of a specific type."""
        return self.plugins.get(plugin_type, [])

# Global instance
plugin_manager = PluginManager()
