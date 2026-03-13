
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from agentos.core.memory.vector import vector_memory

router = APIRouter(prefix="/memory", tags=["Memory"])

class MemoryUpsertRequest(BaseModel):
    text: str = Field(..., description="The information to store")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")

class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="The search query")
    top_k: int = Field(default=3, description="Number of results to return")

class MemoryPoint(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None

@router.post("/upsert")
async def upsert_memory(request: MemoryUpsertRequest):
    """Directly insert knowledge into the long-term memory."""
    point_id = vector_memory.upsert(request.text, request.metadata)
    if not point_id:
        raise HTTPException(status_code=500, detail="Failed to store knowledge")
    return {"message": "Memory stored successfully", "point_id": point_id}

@router.post("/search", response_model=List[MemoryPoint])
async def search_memory(request: MemorySearchRequest):
    """Search the long-term knowledge base."""
    results = vector_memory.search(request.query, top_k=request.top_k)
    return [
        MemoryPoint(
            id="unknown", # Qdrant search results hit doesn't expose ID easily in our wrapper yet
            content=res["content"],
            metadata=res["metadata"],
            score=res["score"]
        ) for res in results
    ]

@router.get("/points")
async def list_points():
    """List recent memory entries (diagnostics)."""
    points = vector_memory.list_all_points()
    return [
        {
            "id": p.id,
            "content": p.payload.get("content"),
            "metadata": p.payload.get("metadata")
        } for p in points
    ]
