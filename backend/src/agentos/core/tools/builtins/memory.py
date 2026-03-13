
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from agentos.core.memory.vector import vector_memory

class SaveToKnowledgeBaseArgs(BaseModel):
    text: str = Field(..., description="The information to remember")

class QueryKnowledgeBaseArgs(BaseModel):
    query: str = Field(..., description="The search term or question")
    top_k: int = Field(default=3, description="Number of relevant results to return")

async def save_to_knowledge_base(text: str) -> str:
    """
    Stores text in the vector database.
    
    Args:
        text (str): The information to remember.
    """
    point_id = vector_memory.upsert(text)
    if point_id:
        return f"Successfully saved to knowledge base. Point ID: {point_id}"
    return "Failed to save to knowledge base."

async def query_knowledge_base(query: str, top_k: int = 3) -> str:
    """
    Searches the vector database for relevant snippets.
    
    Args:
        query (str): The search term or question.
        top_k (int): Number of relevant results to return.
    """
    results = vector_memory.search(query, top_k=top_k)
    if not results:
        return "No relevant information found in the knowledge base."
    
    formatted_results = []
    for i, res in enumerate(results):
        formatted_results.append(f"Result {i+1} (Score: {res['score']:.2f}):\n{res['content']}")
    
    return "\n\n".join(formatted_results)
