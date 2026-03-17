from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

class PluginType(str, Enum):
    TOOL = "tool"
    EVALUATOR = "evaluator"
    MEMORY = "memory"
    TEMPLATE = "template"

class BasePlugin(ABC):
    """
    Abstract Base Class for all AgentOS Plugins.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version of the plugin."""
        pass

    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """Type of the plugin (tool, evaluator, memory, etc.)."""
        pass

    def on_load(self):
        """Called when the plugin is loaded into the system."""
        pass

class ToolPlugin(BasePlugin):
    """Interface for adding new tools/capabilities."""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.TOOL

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool logic."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema definition for the tool (OpenAI/MCP style)."""
        pass

class EvaluatorPlugin(BasePlugin):
    """Interface for adding evaluation metrics."""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.EVALUATOR

    @abstractmethod
    def evaluate(self, input_text: str, output_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the evaluation logic and return scores/metrics."""
        pass
