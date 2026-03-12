"""
MCP Manager for AgentOS.

Handles connections to external Model Context Protocol (MCP) servers
and bridges their tools to the global ToolRegistry.
"""

import asyncio
import structlog
from typing import Dict, List, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agentos.core.tools.registry import registry as tool_registry
from agentos.core.tools.models import ToolDefinition

logger = structlog.get_logger()

class MCPManager:
    """
    Manages MCP server lifecycles and tool registration.
    """
    def __init__(self):
        self._sessions: Dict[str, ClientSession] = {}
        self._exit_stacks: Dict[str, Any] = {} # Storing context managers

    async def connect_stdio(self, name: str, command: str, args: List[str] = None, env: Dict[str, str] = None):
        """
        Connect to an MCP server via stdio.
        """
        if name in self._sessions:
            logger.info("MCP server already connected", name=name)
            return

        logger.info("Connecting to MCP server (stdio)", name=name, command=command)
        
        server_params = StdioServerParameters(
            command=command,
            args=args or [],
            env=env
        )

        # Use an exit stack pattern or similar to keep the connection alive
        # For simplicity in this manager, we'll use a long-lived task or store the context
        
        try:
            # Note: stdio_client is an async context manager
            async def _run_session():
                try:
                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            self._sessions[name] = session
                            logger.info("MCP session initialized", name=name)
                            
                            # Sync tools immediately
                            await self.sync_tools(name)
                            
                            stop_event = asyncio.Event()
                            self._exit_stacks[name] = stop_event
                            await stop_event.wait()
                except Exception as e:
                    logger.error("MCP session task failed", name=name, error=str(e), exc_info=True)
                finally:
                    self._sessions.pop(name, None)
                    self._exit_stacks.pop(name, None)

            # Start in background
            asyncio.create_task(_run_session())
            
            # Wait for session to be ready (up to 10 seconds)
            for _ in range(100):
                if name in self._sessions:
                    logger.info("MCP server connected and ready", name=name)
                    return
                await asyncio.sleep(0.1)
            
            error_msg = f"Timeout waiting for MCP server '{name}' to connect"
            logger.error(error_msg)
            raise TimeoutError(error_msg)
                
        except Exception as e:
            logger.error("Failed to start MCP connection task", name=name, error=str(e))
            raise e

    async def sync_tools(self, server_name: str):
        """
        Fetch tools from an MCP server and register them in the global registry.
        """
        session = self._sessions.get(server_name)
        if not session:
            logger.error("No session found for server", server_name=server_name)
            return

        try:
            response = await session.list_tools()
            for tool in response.tools:
                # Prefix tool name to avoid collisions: server_name__tool_name
                scoped_name = f"{server_name}__{tool.name}"
                
                # Define a wrapper handler that calls the MCP session
                async def mcp_handler(s_name=server_name, t_name=tool.name, **kwargs):
                    sess = self._sessions.get(s_name)
                    if not sess:
                        raise RuntimeError(f"Session for {s_name} lost")
                    result = await sess.call_tool(t_name, arguments=kwargs)
                    
                    # Extract text from content blocks for easier LLM consumption
                    text_parts = []
                    for content in result.content:
                        if hasattr(content, "text"):
                            text_parts.append(content.text)
                        else:
                            text_parts.append(str(content))
                    
                    return "\n".join(text_parts)

                # Register in global registry
                # Note: We don't have the pydantic model for args here directly from MCP list_tools 
                # but we can pass the raw schema
                tool_registry._tools[scoped_name] = ToolDefinition(
                    name=scoped_name,
                    description=tool.description or "",
                    parameters=tool.inputSchema or {}
                )
                tool_registry._handlers[scoped_name] = mcp_handler
                
                logger.info("MCP tool registered", scoped_name=scoped_name)
                
        except Exception as e:
            logger.error("Failed to sync tools from MCP server", name=server_name, error=str(e))

    async def initialize_from_config(self, config_json: str):
        """
        Initialize multiple MCP servers from a JSON configuration string.
        Format: {"server_name": {"command": "...", "args": ["..."], "env": {...}}}
        """
        import json
        try:
            config_dict = json.loads(config_json)
            connection_tasks = []
            for name, params in config_dict.items():
                command = params.get("command")
                args = params.get("args", [])
                env = params.get("env")
                
                if command:
                    connection_tasks.append(self.connect_stdio(name, command, args, env))
            
            if connection_tasks:
                await asyncio.gather(*connection_tasks)
                
        except Exception as e:
            logger.error("Failed to initialize MCP servers from config", error=str(e))

    async def disconnect_all(self):
        """Close all active MCP sessions."""
        for name, stop_event in self._exit_stacks.items():
            stop_event.set()
        self._sessions.clear()
        self._exit_stacks.clear()

mcp_manager = MCPManager()
