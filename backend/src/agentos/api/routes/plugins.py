from fastapi import APIRouter
from typing import List, Dict, Any
from agentos.core.plugins.manager import plugin_manager

router = APIRouter(prefix="/plugins", tags=["Plugins"])

@router.get("/")
def list_plugins() -> List[Dict[str, Any]]:
    """Get a list of all loaded plugins."""
    result = []
    for ptype, plugins in plugin_manager.plugins.items():
        for p in plugins:
            result.append({
                "name": p.name,
                "version": p.version,
                "type": ptype.value
            })
    return result
