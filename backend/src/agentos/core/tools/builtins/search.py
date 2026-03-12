
import httpx
import structlog
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from agentos.core.runtime.config import config

logger = structlog.get_logger()

class SearchArgs(BaseModel):
    query: str = Field(..., description="The search query to find information about.")
    search_depth: str = Field(default="basic", description="Search depth: basic or advanced")
    max_results: int = Field(default=5, description="Maximum number of results to return")

async def search(
    query: str, 
    search_depth: str = "basic", 
    max_results: int = 5
) -> str:
    """
    Search the web for information using Tavily.
    Returns a summary of relevant information with URLs.
    """
    api_key = config.tavily_api_key
    if not api_key:
        return "Error: TAVILY_API_KEY is not configured. Please add it to your .env file."

    logger.info("Performing web search", query=query, depth=search_depth)
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "include_answer": True,
        "max_results": max_results
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract common elements
            results = data.get("results", [])
            answer = data.get("answer")
            
            output = []
            if answer:
                output.append(f"Direct Answer: {answer}\n")
            
            output.append("Search Results:")
            for idx, res in enumerate(results, 1):
                output.append(f"{idx}. {res.get('title')} ({res.get('url')})")
                output.append(f"   {res.get('content')}\n")
                
            return "\n".join(output)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Tavily API Key."
            return f"Error: Search failed with status {e.response.status_code}"
        except Exception as e:
            logger.error("Search request failed", query=query, error=str(e))
            return f"Error: Search failed - {str(e)}"
