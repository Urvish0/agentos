"""
AgentOS Core Runtime — LangGraph-based Agent Execution Engine.

This module implements the core reasoning loop that powers all AgentOS agents.
It uses LangGraph to define a stateful workflow: reason → respond → END.
"""

import time
import uuid
import operator
from typing import Any, TypedDict, Annotated

import structlog
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.utils.function_calling import convert_to_openai_tool

from agentos.core.runtime.llm import get_llm
from agentos.core.tools.registry import registry as tool_registry

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    """
    Represents the state flowing through the LangGraph execution.
    """
    # Inputs
    run_id: str
    input: str
    system_prompt: str

    # Execution tracking
    reasoning_steps: list[dict[str, Any]]
    messages: Annotated[list[Any], operator.add]
    
    # Tool tracking
    tools_available: list[str]
    last_tool_call: dict[str, Any] | None

    # Output
    output: str
    error: str | None

    # Metadata
    model: str
    total_tokens: int
    execution_time_ms: float


# ---------------------------------------------------------------------------
# Default system prompt
# ---------------------------------------------------------------------------

DEFAULT_SYSTEM_PROMPT = (
    "You are an AI agent running on AgentOS. You are helpful, accurate, and concise. "
    "Think step by step. If a tool is available and relevant, use it."
)


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

class AgentRuntime:
    """
    Core Runtime with Tool Support.
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float = 0.7,
        system_prompt: str | None = None,
        provider: str | None = None,
        tools: list[str] | None = None,
    ):
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.provider = provider
        self.tools = tools or []
        
        # Get base LLM
        self.llm = get_llm(model=model, temperature=temperature, provider=provider)
        
        # Bind tools if provided
        if self.tools:
            tool_definitions = []
            for t_name in self.tools:
                t_def = tool_registry.get_tool_definition(t_name)
                if t_def:
                    # Convert our model to LangChain/OpenAI format
                    tool_definitions.append({
                        "type": "function",
                        "function": {
                            "name": t_def.name,
                            "description": t_def.description,
                            "parameters": t_def.parameters,
                        }
                    })
            
            if tool_definitions:
                self.llm = self.llm.bind_tools(tool_definitions)
        
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state machine with tool support."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("reason", self._reason_node)
        workflow.add_node("action", self._action_node)

        # Define edges
        workflow.set_entry_point("reason")
        
        # Conditional edge: decide whether to act or end
        workflow.add_conditional_edges(
            "reason",
            self._should_continue,
            {
                "continue": "action",
                "end": END
            }
        )
        
        # Action always goes back to reason
        workflow.add_edge("action", "reason")

        return workflow.compile()

    def _should_continue(self, state: AgentState):
        """Logic to decide if we should call a tool or finish."""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"

    async def _reason_node(self, state: AgentState) -> dict:
        """Call the LLM and track reasoning."""
        run_id = state["run_id"]
        
        # Build message history: System prompt + all messages in state
        messages = [SystemMessage(content=state["system_prompt"])]
        messages.extend(state.get("messages", []))

        try:
            response = await self.llm.ainvoke(messages)
            
            # Update token usage
            tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = response.usage_metadata.get("total_tokens", 0)

            return {
                "messages": [response],
                "total_tokens": state.get("total_tokens", 0) + tokens,
                "output": response.content if not response.tool_calls else ""
            }

        except Exception as e:
            logger.error("Reasoning failed", run_id=run_id, error=str(e))
            return {"error": str(e)}

    async def _action_node(self, state: AgentState) -> dict:
        """Execute tool calls requested by the LLM."""
        last_message = state["messages"][-1]
        tool_results = []
        
        for tool_call in last_message.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            call_id = tool_call["id"]
            
            logger.info("Executing tool call", name=name, args=args, run_id=state["run_id"])
            
            response = await tool_registry.invoke(name, **args)
            
            # Format as ToolMessage for LangChain
            tool_msg = ToolMessage(
                content=str(response.output) if response.success else f"Error: {response.error}",
                tool_call_id=call_id
            )
            tool_results.append(tool_msg)
            
        return {"messages": tool_results}

    async def run(
        self,
        input_text: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Execute the agent reasoning loop."""
        run_id = str(uuid.uuid4())
        start_time = time.time()

        initial_state: AgentState = {
            "run_id": run_id,
            "input": input_text,
            "system_prompt": system_prompt if system_prompt else self.system_prompt,
            "reasoning_steps": [],
            "messages": [HumanMessage(content=input_text)],
            "tools_available": self.tools,
            "last_tool_call": None,
            "output": "",
            "error": None,
            "model": self.model or "default",
            "total_tokens": 0,
            "execution_time_ms": 0.0,
        }

        # Execute the graph
        # Note: In LangGraph 0.2+, state updates are additive for lists
        result = await self.graph.ainvoke(initial_state)

        execution_time_ms = (time.time() - start_time) * 1000

        return {
            "run_id": run_id,
            "output": result.get("output", ""),
            "messages_count": len(result.get("messages", [])),
            "model": self.model or "default",
            "total_tokens": result.get("total_tokens", 0),
            "execution_time_ms": round(execution_time_ms, 2),
            "error": result.get("error"),
        }

    async def run_stream(self, *args, **kwargs):
        """Streaming is temporarily disabled during tool refactor."""
        yield {"type": "error", "content": "Streaming not yet supported for tool-calling agents."}
