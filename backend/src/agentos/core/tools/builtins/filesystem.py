
import os
from pathlib import Path
from typing import List, Optional
import structlog
from pydantic import BaseModel, Field

from agentos.core.runtime.config import config

logger = structlog.get_logger()

# Helper to resolve and validate path
def _resolve_path(relative_path: str) -> Path:
    base_path = Path(config.agent_sandbox_path).absolute()
    # Ensure base path exists
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Resolve relative path
    target_path = (base_path / relative_path).resolve()
    
    # Security check: Ensure target is inside base_path
    if not str(target_path).startswith(str(base_path)):
        raise PermissionError(f"Access denied: Path {relative_path} is outside the sandbox.")
    
    return target_path

# --- tool: list_directory ---
class ListDirArgs(BaseModel):
    path: str = Field(default=".", description="Relative path to list files for")

def list_directory(path: str = ".") -> List[str]:
    """List files and directories in the sandboxed filesystem."""
    try:
        target = _resolve_path(path)
        if not target.exists():
            return [f"Error: Path {path} does not exist."]
        return os.listdir(target)
    except Exception as e:
        return [f"Error listing directory: {str(e)}"]

# --- tool: write_file ---
class WriteFileArgs(BaseModel):
    path: str = Field(..., description="Relative path to write the file to")
    content: str = Field(..., description="Text content to write")

def write_file(path: str, content: str) -> str:
    """Write text content to a file in the sandboxed filesystem."""
    try:
        target = _resolve_path(path)
        # Ensure parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info("File written to sandbox", path=path)
        return f"Successfully wrote to {path}"
    except Exception as e:
        logger.error("Failed to write file", path=path, error=str(e))
        return f"Error writing file: {str(e)}"

# --- tool: read_file ---
class ReadFileArgs(BaseModel):
    path: str = Field(..., description="Relative path to read the file from")

def read_file(path: str) -> str:
    """Read text content from a file in the sandboxed filesystem."""
    try:
        target = _resolve_path(path)
        if not target.is_file():
            return f"Error: {path} is not a file or does not exist."
            
        with open(target, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
