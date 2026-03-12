"""
Tool Registry for AgentOS.
"""

from typing import Any, Callable, Dict, List, Optional, Type
import structlog
from pydantic import BaseModel
from agentos.core.tools.models import ToolDefinition, ToolInvokeResponse

logger = structlog.get_logger()

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable] = {}

    def register_tool(
        self, 
        name: str, 
        description: str, 
        handler: Callable, 
        args_schema: Optional[Type[BaseModel]] = None
    ):
        params = args_schema.model_json_schema() if args_schema else {}
        definition = ToolDefinition(
            name=name,
            description=description,
            parameters=params
        )
        self._tools[name] = definition
        self._handlers[name] = handler
        logger.info("Tool registered", name=name)

    def get_tool_definition(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def invoke(self, name: str, **kwargs) -> ToolInvokeResponse:
        handler = self._handlers.get(name)
        if not handler:
            return ToolInvokeResponse(
                tool_name=name,
                output=None,
                error=f"Tool '{name}' not found",
                success=False
            )

        try:
            logger.info("Invoking tool", name=name, args=kwargs)
            result = handler(**kwargs)
            return ToolInvokeResponse(
                tool_name=name,
                output=result,
                success=True
            )
        except Exception as e:
            logger.error("Tool execution failed", name=name, error=str(e))
            return ToolInvokeResponse(
                tool_name=name,
                output=None,
                error=str(e),
                success=False
            )

registry = ToolRegistry()

# Example Tool
def get_weather(location: str):
    return f"The weather in {location} is sunny and 25°C (Simulated)."

class WeatherArgs(BaseModel):
    location: str

registry.register_tool(
    name="get_weather",
    description="Get current weather for a specific city or region",
    handler=get_weather,
    args_schema=WeatherArgs
)
