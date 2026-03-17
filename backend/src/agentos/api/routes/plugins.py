from fastapi import APIRouter
from typing import List, Dict, Any
from agentos.core.plugins.manager import plugin_manager

router = APIRouter(prefix="/plugins", tags=["Plugins"])

@router.get("/")
async def list_plugins():
    # Return all plugins with their enabled status
    processed_names = set()
    all_plugins = []
    
    # Registered plugins (active)
    for name, plugin in plugin_manager.plugins.items():
        all_plugins.append({
            "name": plugin.name,
            "version": plugin.version,
            "type": plugin.plugin_type,
            "enabled": True
        })
        processed_names.add(name)
    
    # Add ones from registry (especially disabled ones or enabled-but-not-loaded)
    for name, enabled in plugin_manager._registry_data.items():
        if name not in processed_names:
            all_plugins.append({
                "name": name,
                "version": "unknown",
                "type": "unknown",
                "enabled": enabled,
                "status": "pending_restart" if enabled else "disabled"
            })
            
    return all_plugins

@router.patch("/{name}")
async def update_plugin_state(name: str, enabled: bool):
    if enabled:
        plugin_manager.enable_plugin(name)
    else:
        plugin_manager.disable_plugin(name)
    return {"status": "success", "name": name, "enabled": enabled}

@router.post("/install")
async def install_plugin(path: str):
    try:
        dest = plugin_manager.install_plugin_file(path)
        return {"status": "success", "destination": dest}
    except Exception as e:
        return {"status": "error", "message": str(e)}
