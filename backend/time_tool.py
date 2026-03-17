import datetime
from agentos.core.plugins.base import ToolPlugin, PluginType

class TimePlugin(ToolPlugin):
    """
    A simple plugin that provides the current system time.
    """

    @property
    def name(self) -> str:
        return "time_tool"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, **kwargs) -> str:
        """Returns the current UTC time."""
        now = datetime.datetime.now(datetime.timezone.utc)
        return f"The current UTC time is: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_schema(self):
        """No parameters needed for this tool."""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
