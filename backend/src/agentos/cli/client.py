"""
API Client for AgentOS CLI.
Handles all HTTP communication with the backend.
"""
import os
import httpx
from typing import Any, Dict, List, Optional


class AgentOSClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("AGENTOS_API_URL", "http://localhost:8000")
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0, follow_redirects=True)

    def list_agents(self) -> List[Dict[str, Any]]:
        response = self.client.get("/agents/")
        response.raise_for_status()
        return response.json()

    def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.post("/agents/register", json=agent_data)
        response.raise_for_status()
        return response.json()

    def create_task(self, agent_id: str, input_text: str) -> Dict[str, Any]:
        response = self.client.post("/tasks/create", json={"agent_id": agent_id, "input": input_text})
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        response = self.client.post(f"/tasks/{task_id}/cancel")
        response.raise_for_status()
        return response.json()

    def get_trace_url(self, task_id: str) -> str:
        # This endpoint returns the URL to the trace (e.g., Jaeger)
        response = self.client.get(f"/tasks/{task_id}/trace")
        response.raise_for_status()
        return response.json().get("trace_url", "No trace URL available")

    def list_plugins(self) -> List[Dict[str, Any]]:
        response = self.client.get("/plugins/")
        response.raise_for_status()
        return response.json()
