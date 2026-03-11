from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env — search upward from this file to find .env
def _find_and_load_dotenv():
    """Walk up from this file's directory to find .env"""
    current = Path(__file__).resolve().parent
    for _ in range(10):  # max 10 levels up
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=str(env_file))
            return str(env_file)
        current = current.parent
    return None

_env_path = _find_and_load_dotenv()

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AgentRunRequest(BaseModel):
    """Request body for running an agent."""
    input: str = Field(..., description="The user's input or goal for the agent")
    model: str | None = Field(None, description="Override the default LLM model")
    system_prompt: str | None = Field(None, description="Override the system prompt")


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
    # Health & Info
    # ------------------------------------------------------------------

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "0.1.0",
            "env_loaded": _env_path is not None,
            "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        }

    @app.get("/")
    async def root():
        return {"message": "Welcome to AgentOS API"}

    # ------------------------------------------------------------------
    # Agent Runtime
    # ------------------------------------------------------------------

    @app.post("/agent/run", response_model=AgentRunResponse)
    async def run_agent(request: AgentRunRequest):
        """
        Execute an agent with the given input.
        Uses the LangGraph runtime engine with Groq LLM.
        """
        try:
            from agentos.core.runtime.runtime import AgentRuntime

            logger.info("Agent run requested", input=request.input, model=request.model)

            runtime = AgentRuntime(
                model=request.model,
                system_prompt=request.system_prompt,
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

    return app

app = create_app()
