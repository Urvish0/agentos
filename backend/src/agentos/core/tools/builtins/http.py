
import httpx
import structlog
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = structlog.get_logger()

class HttpRequestArgs(BaseModel):
    url: str = Field(..., description="The URL to send the request to.")
    method: str = Field(default="GET", description="HTTP method: GET, POST, PUT, DELETE")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters for GET requests")
    data: Optional[Dict[str, Any]] = Field(None, description="JSON body for POST/PUT requests")
    headers: Optional[Dict[str, Any]] = Field(None, description="Optional request headers")

async def http_request(
    url: str, 
    method: str = "GET", 
    params: Dict[str, Any] = None, 
    data: Dict[str, Any] = None,
    headers: Dict[str, Any] = None
) -> str:
    """
    Make an HTTP request to an external URL. 
    Returns the response status and body as string.
    """
    logger.info("Making HTTP request", method=method, url=url)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=30.0
            )
            
            return f"Status: {response.status_code}\nContent: {response.text[:2000]}"
            
        except Exception as e:
            logger.error("HTTP request failed", url=url, error=str(e))
            return f"Error: Request failed - {str(e)}"
