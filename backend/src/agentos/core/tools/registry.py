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

    async def invoke(self, name: str, **kwargs) -> ToolInvokeResponse:
        """Invoke a tool (sync or async) by name with arguments."""
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
            
            # Check if it's a coroutine or just a function
            import inspect
            if inspect.iscoroutinefunction(handler):
                result = await handler(**kwargs)
            else:
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

    def register_builtin_tools(self):
        """Register all built-in AgentOS tools."""
        from agentos.core.tools.builtins.filesystem import list_directory, read_file, write_file, ListDirArgs, ReadFileArgs, WriteFileArgs
        from agentos.core.tools.builtins.http import http_request, HttpRequestArgs
        from agentos.core.tools.builtins.python_executor import execute_python, PythonExecutorArgs
        from agentos.core.tools.builtins.search import search, SearchArgs

        # Filesystem
        self.register_tool("list_directory", "List files in the sandboxed filesystem", list_directory, ListDirArgs)
        self.register_tool("read_file", "Read text content from a file in the sandbox", read_file, ReadFileArgs)
        self.register_tool("write_file", "Write text content to a file in the sandbox", write_file, WriteFileArgs)
        
        # HTTP
        self.register_tool("http_request", "Make an HTTP GET/POST request to any URL", http_request, HttpRequestArgs)
        
        # Python
        self.register_tool("execute_python", "Execute a Python script for data processing or tool creation", execute_python, PythonExecutorArgs)
        
        # Search
        self.register_tool("search", "Search the web for real-time information using Tavily", search, SearchArgs)

        # Memory (RAG)
        from agentos.core.tools.builtins.memory import save_to_knowledge_base, query_knowledge_base, SaveToKnowledgeBaseArgs, QueryKnowledgeBaseArgs
        self.register_tool("save_to_knowledge_base", "Permanently store information in long-term memory", save_to_knowledge_base, SaveToKnowledgeBaseArgs)
        self.register_tool("query_knowledge_base", "Search for information in long-term knowledge base", query_knowledge_base, QueryKnowledgeBaseArgs)

registry = ToolRegistry()
registry.register_builtin_tools()
