from typing import Any, Union
import httpx

class Resource:
    """Base class for all SDK resources."""
    
    def __init__(self, client: Union[httpx.Client, httpx.AsyncClient], async_mode: bool):
        self._client = client
        self._async_mode = async_mode

    def _request(self, method: str, path: str, **kwargs) -> Any:
        """Internal helper for sync/async requests."""
        if self._async_mode:
            return self._async_request(method, path, **kwargs)
        
        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _async_request(self, method: str, path: str, **kwargs) -> Any:
        """Internal helper for async requests."""
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()
