import time
import asyncio
from typing import Any, Dict, List, Optional
from .base import Resource

class Tasks(Resource):
    """Resource for managing AgentOS Tasks."""

    def create(self, agent_id: str, input_text: str) -> Dict[str, Any]:
        """Create a new task for an agent."""
        return self._request("POST", "/tasks/create", json={"agent_id": agent_id, "input": input_text})

    def get(self, task_id: str) -> Dict[str, Any]:
        """Get details/status of a specific task."""
        return self._request("GET", f"/tasks/{task_id}")

    def list(self, skip: int = 0, limit: int = 100, status: str = None, agent_id: str = None) -> List[Dict[str, Any]]:
        """List tasks with optional filters."""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        if agent_id:
            params["agent_id"] = agent_id
        return self._request("GET", "/tasks/", params=params)

    def cancel(self, task_id: str) -> Dict[str, Any]:
        """Cancel a running task."""
        return self._request("POST", f"/tasks/{task_id}/cancel")

    def trace(self, task_id: str) -> Dict[str, Any]:
        """Get the OpenTelemetry trace link for a task."""
        return self._request("GET", f"/tasks/{task_id}/trace")

    def run_and_wait(self, agent_id: str, input_text: str, poll_interval: float = 1.0) -> Any:
        """
        High-level helper: Create a task and poll until it completes.
        Returns a Dict[str, Any] in sync mode, and a Coroutine in async mode.
        """
        if self._async_mode:
            return self._async_run_and_wait(agent_id, input_text, poll_interval)
        
        task = self.create(agent_id, input_text)
        task_id = task["id"]
        
        while True:
            task_data = self.get(task_id)
            if task_data["status"] in ["completed", "failed", "cancelled"]:
                return task_data
            time.sleep(poll_interval)

    async def _async_run_and_wait(self, agent_id: str, input_text: str, poll_interval: float = 1.0) -> Dict[str, Any]:
        """Async version of run_and_wait."""
        task = await self.create(agent_id, input_text)
        task_id = task["id"]
        
        while True:
            task_data = await self.get(task_id)
            if task_data["status"] in ["completed", "failed", "cancelled"]:
                return task_data
            await asyncio.sleep(poll_interval)
