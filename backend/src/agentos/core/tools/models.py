"""
Tool Models for AgentOS.

Defines the structure of tools and their execution results.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ToolDefinition(BaseModel):
    """Metadata for a tool."""
    name: str = Field(..., description="Unique name of the tool")
    description: str = Field(..., description="What the tool does and when to use it")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema of parameters")

class ToolInvokeRequest(BaseModel):
    """Request to invoke a tool."""
    tool_name: str
    arguments: Dict[str, Any]

class ToolInvokeResponse(BaseModel):
    """The result of a tool invocation."""
    tool_name: str
    output: Any
    error: Optional[str] = None
    success: bool = True
