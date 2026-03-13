
import redis
import json
import structlog
from typing import List, Dict, Any, Optional
from agentos.core.runtime.config import config

logger = structlog.get_logger()

class RedisMemory:
    """
    Handles short-term conversation persistence using Redis.
    Messages are stored as a JSON list under a thread_id key.
    """
    def __init__(self):
        self.redis_client = redis.from_url(config.redis_url, decode_responses=True)
        self.prefix = "agent_history:"
        self.default_ttl = 3600 * 24  # 24 hours

    def _get_key(self, thread_id: str) -> str:
        return f"{self.prefix}{thread_id}"

    def get_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a specific thread."""
        key = self._get_key(thread_id)
        data = self.redis_client.get(key)
        if not data:
            return []
        try:
            return json.loads(data)
        except Exception as e:
            logger.error("Failed to parse history from Redis", thread_id=thread_id, error=str(e))
            return []

    def add_messages(self, thread_id: str, messages: List[Dict[str, Any]], ttl: Optional[int] = None):
        """Append new messages to the thread history."""
        existing = self.get_history(thread_id)
        # Combine existing and new
        updated = existing + messages
        
        # Keep only last 50 messages to prevent context overflow (configurable later)
        if len(updated) > 50:
            updated = updated[-50:]
            
        key = self._get_key(thread_id)
        self.redis_client.set(key, json.dumps(updated), ex=ttl or self.default_ttl)
        logger.info("History updated in Redis", thread_id=thread_id, new_count=len(messages))

    def clear_history(self, thread_id: str):
        """Delete history for a thread."""
        key = self._get_key(thread_id)
        self.redis_client.delete(key)
        logger.info("History cleared", thread_id=thread_id)

# Global memory instance
memory = RedisMemory()
