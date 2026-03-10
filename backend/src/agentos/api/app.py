from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

logger = structlog.get_logger()

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

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "0.1.0"}

    @app.get("/")
    async def root():
        return {"message": "Welcome to AgentOS API"}

    return app

app = create_app()
