import sys
import inspect
import importlib.util
import os
import json
import shutil
from typing import Dict, List, Set, Optional, Type, Any
import logging
import structlog
from .base import BasePlugin, PluginType, ToolPlugin

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Manages the discovery, loading, and lifecycle of AgentOS plugins.
    Supports hot-reloading: plugins can be enabled/disabled at runtime
    without restarting the backend.
    """

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self._loaded_paths: Set[str] = set()
        self.registry_path: Optional[str] = None
        self._registry_data: Dict[str, bool] = {}  # name -> enabled state
        self._plugin_file_map: Dict[str, str] = {}  # plugin_name -> file_path

    def discover_and_load(self, directory: str):
        """Discover and load all plugins from a directory."""
        if not os.path.isdir(directory):
            logger.warning(f"Plugin directory not found: {directory}")
            return

        self.registry_path = os.path.join(directory, "registry.json")
        if not os.path.exists(self.registry_path):
            self._save_registry()
        else:
            self._load_registry()

        # Add directory to sys.path so plugins can import each other if needed
        if directory not in sys.path:
            sys.path.insert(0, directory)

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                file_path = os.path.join(directory, filename)
                self.load_plugin(file_path)

    def load_plugin(self, file_path: str):
        """Dynamically load classes from a python file that inherit from BasePlugin."""
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
                    
                    instance = obj()
                    # Track which file provides which plugin
                    self._plugin_file_map[instance.name] = file_path
                    
                    # Check if enabled in registry
                    is_enabled = self._registry_data.get(instance.name, True)
                    if not is_enabled:
                        logger.info(f"Plugin {instance.name} is disabled. Skipping registration.")
                        continue

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
        """Manually register a plugin instance and auto-register tools."""
        self.plugins[plugin.name] = plugin
        plugin.on_load()
        logger.info(f"Registered {plugin.plugin_type.value} plugin: {plugin.name} v{plugin.version}")
        
        # Auto-register ToolPlugins with the global ToolRegistry
        if isinstance(plugin, ToolPlugin):
            self._register_tool_plugin(plugin)

    def _register_tool_plugin(self, plugin: ToolPlugin):
        """Bridge a ToolPlugin into the global ToolRegistry."""
        from agentos.core.tools.registry import registry as tool_registry
        schema = plugin.get_schema()
        tool_name = schema.get("name", plugin.name)
        tool_registry.register_tool(
            name=tool_name,
            description=schema.get("description", f"Plugin tool: {plugin.name}"),
            handler=plugin.execute,
            args_schema=None  # Schema is already in OpenAI format
        )
        logger.info(f"Hot-registered tool '{tool_name}' from plugin '{plugin.name}'")

    def _unregister_tool_plugin(self, tool_name: str):
        """Remove a ToolPlugin's tool from the global ToolRegistry."""
        from agentos.core.tools.registry import registry as tool_registry
        if tool_name in tool_registry._tools:
            del tool_registry._tools[tool_name]
            del tool_registry._handlers[tool_name]
            logger.info(f"Hot-unregistered tool '{tool_name}' from ToolRegistry")

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """Return all loaded plugins of a specific type."""
        return [p for p in self.plugins.values() if p.plugin_type == plugin_type]

    def _load_registry(self):
        """Load the plugin registry state from disk."""
        if self.registry_path and os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r") as f:
                    self._registry_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load plugin registry: {e}")
                self._registry_data = {}

    def _save_registry(self):
        """Save the plugin registry state to disk."""
        if self.registry_path:
            try:
                with open(self.registry_path, "w") as f:
                    json.dump(self._registry_data, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to save plugin registry: {e}")

    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin and immediately hot-load it."""
        self._registry_data[name] = True
        self._save_registry()
        
        # Hot-reload: find the file for this plugin and re-load it
        file_path = self._plugin_file_map.get(name)
        if file_path:
            self._loaded_paths.discard(file_path)
            self.load_plugin(file_path)
        elif self.registry_path:
            # Fallback: full re-scan
            plugins_dir = os.path.dirname(self.registry_path)
            self._loaded_paths.clear()
            self.discover_and_load(plugins_dir)
        return True

    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin and immediately unregister its tools."""
        self._registry_data[name] = False
        self._save_registry()
        
        # Unregister tools provided by this plugin
        if name in self.plugins:
            plugin = self.plugins[name]
            if isinstance(plugin, ToolPlugin):
                schema = plugin.get_schema()
                tool_name = schema.get("name", name)
                self._unregister_tool_plugin(tool_name)
            del self.plugins[name]
        return True

    def sync_with_registry(self):
        """
        Re-read registry.json from disk and reconcile in-memory state.
        Call this at the start of every Celery task to pick up changes
        made via the Dashboard API without a backend restart.
        """
        if not self.registry_path:
            return
            
        old_registry = dict(self._registry_data)
        self._load_registry()
        
        for name, enabled in self._registry_data.items():
            was_enabled = old_registry.get(name)
            if enabled and not was_enabled:
                # Newly enabled
                file_path = self._plugin_file_map.get(name)
                if file_path:
                    self._loaded_paths.discard(file_path)
                    self.load_plugin(file_path)
            elif not enabled and was_enabled:
                # Newly disabled
                if name in self.plugins:
                    plugin = self.plugins[name]
                    if isinstance(plugin, ToolPlugin):
                        schema = plugin.get_schema()
                        tool_name = schema.get("name", name)
                        self._unregister_tool_plugin(tool_name)
                    del self.plugins[name]

    def install_plugin_file(self, source_path: str) -> str:
        """Install a plugin file by copying it to the plugins directory."""
        if not self.registry_path:
            raise ValueError("Plugin manager not initialized (no registry path).")
        
        plugins_dir = os.path.dirname(self.registry_path)
        filename = os.path.basename(source_path)
        dest_path = os.path.join(plugins_dir, filename)
        
        shutil.copy2(source_path, dest_path)
        return dest_path

# Global instance
plugin_manager = PluginManager()
