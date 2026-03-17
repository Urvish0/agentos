from typing import Any, Dict, List
from .base import Resource

class Agents(Resource):
    """Resource for managing AgentOS Agents."""

    def list(self, skip: int = 0, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        """List all registered agents."""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        return self._request("GET", "/agents/", params=params)

    def get(self, agent_id: str) -> Dict[str, Any]:
        """Get details of a specific agent."""
        return self._request("GET", f"/agents/{agent_id}")

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent."""
        return self._request("POST", "/agents/register", json=data)

    def update(self, agent_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent."""
        return self._request("PUT", f"/agents/{agent_id}", json=data)

    def delete(self, agent_id: str) -> None:
        """Delete an agent."""
        self._request("DELETE", f"/agents/{agent_id}")
