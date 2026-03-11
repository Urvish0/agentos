"""
AgentOS Core Runtime — LangGraph-based Agent Execution Engine.

This module implements the core reasoning loop that powers all AgentOS agents.
It uses LangGraph to define a stateful workflow: reason → respond → END.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from agentos.core.runtime.llm import get_llm

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
    messages: list[Any]

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
    "You are an AI agent running on AgentOS, an open-source infrastructure "
    "platform for autonomous AI agents. You are helpful, accurate, and concise. "
    "Think step by step before answering."
)


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

class AgentRuntime:
    """
    Core Runtime for executing AgentOS agents using LangGraph.

    Usage:
        runtime = AgentRuntime(model="llama-3.3-70b-versatile")
        result = await runtime.run("What is AgentOS?")
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float = 0.7,
        system_prompt: str | None = None,
    ):
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.llm = get_llm(model=model, temperature=temperature)
        self.graph = self._build_graph()

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self):
        """Build the LangGraph state machine."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("reason", self._reason_node)
        workflow.add_node("respond", self._respond_node)

        # Define edges
        workflow.set_entry_point("reason")
        workflow.add_edge("reason", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile()

    # ------------------------------------------------------------------
    # Graph nodes
    # ------------------------------------------------------------------

    async def _reason_node(self, state: AgentState) -> dict:
        """
        Core reasoning node — calls the LLM with the current context.
        """
        run_id = state["run_id"]
        logger.info("Reasoning started", run_id=run_id)

        messages = [
            SystemMessage(content=state["system_prompt"]),
            HumanMessage(content=state["input"]),
        ]

        try:
            response = await self.llm.ainvoke(messages)

            # Track token usage if available
            tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = response.usage_metadata.get("total_tokens", 0)

            reasoning_step = {
                "step": "reason",
                "input": state["input"],
                "output": response.content,
                "tokens": tokens,
            }

            logger.info(
                "Reasoning complete",
                run_id=run_id,
                tokens=tokens,
                output_length=len(response.content),
            )

            return {
                "messages": [*state.get("messages", []), response],
                "reasoning_steps": [
                    *state.get("reasoning_steps", []),
                    reasoning_step,
                ],
                "total_tokens": state.get("total_tokens", 0) + tokens,
            }

        except Exception as e:
            logger.error("Reasoning failed", run_id=run_id, error=str(e))
            return {"error": str(e)}

    async def _respond_node(self, state: AgentState) -> dict:
        """
        Formats the final response from the reasoning output.
        """
        if state.get("error"):
            return {"output": f"Error: {state['error']}"}

        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            return {"output": last_message.content}

        return {"output": "No response generated."}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(
        self,
        input_text: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute the agent reasoning loop.

        Args:
            input_text: The user's input/goal
            system_prompt: Optional override for the system prompt

        Returns:
            dict with keys: run_id, output, reasoning_steps, model,
                            total_tokens, execution_time_ms, error
        """
        run_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info("Agent execution started", run_id=run_id, input=input_text)

        initial_state: AgentState = {
            "run_id": run_id,
            "input": input_text,
            "system_prompt": system_prompt if system_prompt else self.system_prompt,
            "reasoning_steps": [],
            "messages": [],
            "output": "",
            "error": None,
            "model": self.model or "default",
            "total_tokens": 0,
            "execution_time_ms": 0.0,
        }

        # Execute the graph
        result = await self.graph.ainvoke(initial_state)

        execution_time_ms = (time.time() - start_time) * 1000

        logger.info(
            "Agent execution complete",
            run_id=run_id,
            execution_time_ms=round(execution_time_ms, 2),
            total_tokens=result.get("total_tokens", 0),
        )

        return {
            "run_id": run_id,
            "output": result.get("output", ""),
            "reasoning_steps": result.get("reasoning_steps", []),
            "model": result.get("model", ""),
            "total_tokens": result.get("total_tokens", 0),
            "execution_time_ms": round(execution_time_ms, 2),
            "error": result.get("error"),
        }
