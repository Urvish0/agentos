from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import structlog
import json

from agentos.core.runtime.config import config

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AgentRunRequest(BaseModel):
    """Request body for running an agent."""
    input: str = Field(..., description="The user's input or goal for the agent")
    model: str | None = Field(None, description="Override the default LLM model")
    system_prompt: str | None = Field(None, description="Override the system prompt")
    provider: str | None = Field(None, description="LLM provider: groq, openai, anthropic")


class AgentRunResponse(BaseModel):
    """Response from an agent run."""
    run_id: str
    output: str
    model: str
    total_tokens: int
    execution_time_ms: float
    reasoning_steps: list[dict] = []
    error: str | None = None


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """
    Factory to create the AgentOS FastAPI application.
    """
    app = FastAPI(
        title="AgentOS API",
        description="Infrastructure platform for deploying and orchestrating AI agents.",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Database initialization on startup
    # ------------------------------------------------------------------
    @app.on_event("startup")
    async def on_startup():
        from agentos.core.manager.database import create_db_and_tables
        # Import models so SQLModel.metadata knows about all tables
        from agentos.core.orchestrator.models import Task  # noqa: F401
        create_db_and_tables()

        # Initialize MCP Servers
        from agentos.core.tools.mcp_manager import mcp_manager
        if config.mcp_servers_config:
            await mcp_manager.initialize_from_config(config.mcp_servers_config)

    # ------------------------------------------------------------------
    # Include routers
    # ------------------------------------------------------------------
    from agentos.api.routes.agents import router as agents_router
    from agentos.api.routes.tasks import router as tasks_router
    app.include_router(agents_router)
    app.include_router(tasks_router)

    # ------------------------------------------------------------------
    # Health & Info
    # ------------------------------------------------------------------

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "0.1.0",
            "llm_provider": config.llm_provider,
            "default_model": config.default_model,
            "groq_configured": bool(config.groq_api_key),
        }

    @app.get("/")
    async def root():
        return {"message": "Welcome to AgentOS API"}

    # ------------------------------------------------------------------
    # Agent Runtime — Standard (full response)
    # ------------------------------------------------------------------

    @app.post("/agent/run", response_model=AgentRunResponse)
    async def run_agent(request: AgentRunRequest):
        """
        Execute an agent with the given input.
        Returns the complete response after the agent finishes reasoning.
        """
        try:
            from agentos.core.runtime.runtime import AgentRuntime

            logger.info(
                "Agent run requested",
                input=request.input,
                model=request.model,
                provider=request.provider,
            )

            runtime = AgentRuntime(
                model=request.model,
                system_prompt=request.system_prompt,
                provider=request.provider,
            )
            result = await runtime.run(
                input_text=request.input,
                system_prompt=request.system_prompt,
            )

            return AgentRunResponse(**result)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error("Agent run failed", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------------
    # Agent Runtime — Streaming (token-by-token)
    # ------------------------------------------------------------------

    @app.post("/agent/run/stream")
    async def run_agent_stream(request: AgentRunRequest):
        """
        Execute an agent with streaming output.
        Returns Server-Sent Events (SSE) with tokens as they arrive.
        """
        from agentos.core.runtime.runtime import AgentRuntime

        logger.info(
            "Agent stream requested",
            input=request.input,
            model=request.model,
            provider=request.provider,
        )

        runtime = AgentRuntime(
            model=request.model,
            system_prompt=request.system_prompt,
            provider=request.provider,
        )

        async def event_stream():
            try:
                async for chunk in runtime.run_stream(
                    input_text=request.input,
                    system_prompt=request.system_prompt,
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
        )

    return app

app = create_app()
