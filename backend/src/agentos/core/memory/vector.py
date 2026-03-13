
import structlog
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding

from agentos.core.runtime.config import config

logger = structlog.get_logger()

class VectorMemory:
    """
    Handles long-term vector-based memory using Qdrant and FastEmbed.
    """
    def __init__(self, collection_name: str = "agent_memory"):
        self.client = QdrantClient(url=config.qdrant_url)
        self.collection_name = collection_name
        self.embedding_model = TextEmbedding()  # Uses default 'BAAI/bge-small-en-v1.5'
        self._ensure_collection()

    def _ensure_collection(self):
        """Create the collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                logger.info("Creating Qdrant collection", name=self.collection_name)
                # Small BGE model has 384 dimensions
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384, 
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error("Failed to ensure Qdrant collection", error=str(e))

    def upsert(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Embed text and store in Qdrant."""
        try:
            # Generate embeddings (returns a generator)
            embeddings = list(self.embedding_model.embed([text]))
            vector = embeddings[0].tolist()
            logger.info("Generated embedding", dimensions=len(vector))

            import uuid
            point_id = str(uuid.uuid4())

            result = self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "content": text,
                            "metadata": metadata or {}
                        }
                    )
                ]
            )
            logger.info("Knowledge saved to vector memory", status=result.status, id=point_id)
            return point_id
        except Exception as e:
            logger.error("Failed to upsert to Qdrant", error=str(e))
            return None

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant context in Qdrant."""
        try:
            embeddings = list(self.embedding_model.embed([query]))
            vector = embeddings[0].tolist()

            results = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=top_k
            ).points
            
            return [
                {
                    "content": hit.payload["content"],
                    "metadata": hit.payload.get("metadata", {}),
                    "score": hit.score
                }
                for hit in results
            ]
        except Exception as e:
            logger.error("Failed to search Qdrant", error=str(e))
            return []

    def list_all_points(self):
        """Debug helper to see what's in the collection."""
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                limit=10,
                with_payload=True,
                with_vectors=False
            )
            return results[0]  # Return the list of points
        except Exception as e:
            logger.error("Failed to scroll Qdrant", error=str(e))
            return []

# Global vector memory instance
vector_memory = VectorMemory()
