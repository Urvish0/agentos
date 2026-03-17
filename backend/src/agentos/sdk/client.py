"""
Base client for AgentOS Python SDK.
"""
import os
import httpx
from typing import Optional

from .resources.agents import Agents
from .resources.tasks import Tasks
from .resources.memory import Memory


class AgentOS:
    """
    The main entry point for the AgentOS SDK.
    
    Usage:
        client = AgentOS()
        agents = client.agents.list()
    """

    def __init__(
        self, 
        base_url: str = None, 
        timeout: float = 30.0,
        async_mode: bool = False
    ):
        self.base_url = base_url or os.getenv("AGENTOS_API_URL", "http://localhost:8000")
        self.timeout = timeout
        self.async_mode = async_mode
        
        # Initialize HTTP clients
        if async_mode:
            self._http_client = httpx.AsyncClient(
                base_url=self.base_url, 
                timeout=self.timeout,
                follow_redirects=True
            )
        else:
            self._http_client = httpx.Client(
                base_url=self.base_url, 
                timeout=self.timeout,
                follow_redirects=True
            )

        # Initialize Resources
        self.agents = Agents(self._http_client, async_mode)
        self.tasks = Tasks(self._http_client, async_mode)
        self.memory = Memory(self._http_client, async_mode)

    def __enter__(self):
        if self.async_mode:
            raise TypeError("Use 'async with' for async mode")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._http_client.close()

    async def __aenter__(self):
        if not self.async_mode:
            raise TypeError("Use 'with' for sync mode")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._http_client.aclose()
