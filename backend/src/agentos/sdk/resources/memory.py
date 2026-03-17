from typing import Any, Dict, List, Optional
from .base import Resource

class Memory(Resource):
    """Resource for managing AgentOS Long-term Memory (Vector DB)."""

    def upsert(self, text: str, metadata: Dict[str, Any] = None, collection: str = "agent_knowledge") -> Dict[str, Any]:
        """Store information in the long-term memory."""
        data = {"text": text, "metadata": metadata or {}, "collection": collection}
        return self._request("POST", "/memory/upsert", json=data)

    def search(self, query: str, limit: int = 5, collection: str = "agent_knowledge") -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant items."""
        params = {"query": query, "limit": limit, "collection": collection}
        return self._request("GET", "/memory/search", params=params)

    def list_points(self, collection: str = "agent_knowledge", limit: int = 100) -> List[Dict[str, Any]]:
        """List all memory points in a collection."""
        params = {"collection": collection, "limit": limit}
        return self._request("GET", "/memory/points", params=params)
