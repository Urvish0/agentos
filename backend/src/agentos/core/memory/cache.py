
import redis
import hashlib
import json
import structlog
from typing import Optional, Any
from agentos.core.runtime.config import config

logger = structlog.get_logger()

class RedisCache:
    """
    Handles LLM response caching and idempotency checks using Redis.
    """
    def __init__(self):
        self.redis_client = redis.from_url(config.redis_url, decode_responses=True)
        self.cache_prefix = "llm_cache:"
        self.idempotency_prefix = "idempotency:"
        self.default_ttl = 3600 * 12  # 12 hours

    def _get_cache_key(self, prompt: str, model: str) -> str:
        # Create a unique hash for the prompt+model combination
        content = f"{model}:{prompt}".encode('utf-8')
        p_hash = hashlib.sha256(content).hexdigest()
        return f"{self.cache_prefix}{p_hash}"

    def get_cached_response(self, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached LLM response if it exists."""
        key = self._get_cache_key(prompt, model)
        data = self.redis_client.get(key)
        if data:
            logger.info("Cache hit for LLM response", model=model)
            return json.loads(data)
        return None

    def set_cached_response(self, prompt: str, model: str, response: Dict[str, Any], ttl: Optional[int] = None):
        """Cache an LLM response."""
        key = self._get_cache_key(prompt, model)
        self.redis_client.set(key, json.dumps(response), ex=ttl or self.default_ttl)
        logger.info("Saved response to cache", key=key)

    def is_duplicate(self, request_id: str, ttl: int = 300) -> bool:
        """
        Check if a request with this ID has been seen recently.
        Returns True if duplicate, False if unique.
        """
        key = f"{self.idempotency_prefix}{request_id}"
        # setnx (SET if Not eXists) returns 1 if it set the key, 0 otherwise
        is_new = self.redis_client.set(key, "processing", nx=True, ex=ttl)
        if not is_new:
            logger.warning("Duplicate request detected", request_id=request_id)
            return True
        return False

    def mark_completed(self, request_id: str, result: str, ttl: int = 3600):
        """Mark an idempotent request as completed and store the result."""
        key = f"{self.idempotency_prefix}{request_id}"
        self.redis_client.set(key, result, ex=ttl)

# Global cache instance
cache = RedisCache()
