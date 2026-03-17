from agentos.core.plugins.base import ToolPlugin
from typing import Any, Dict

class WeatherPlugin(ToolPlugin):
    """A sample plugin that provides weather information."""

    @property
    def name(self) -> str:
        return "weather_tool"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, city: str) -> str:
        # Mock logic
        return f"The weather in {city} is sunny, 25°C."

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "get_weather",
            "description": "Get current weather in a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name"}
                },
                "required": ["city"]
            }
        }
