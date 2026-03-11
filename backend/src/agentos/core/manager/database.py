"""
Database connection module for AgentOS.

Uses SQLModel (SQLAlchemy + Pydantic) with PostgreSQL.
Provides session management and table creation utilities.
"""

from sqlmodel import SQLModel, Session, create_engine
import structlog

from agentos.core.runtime.config import config

logger = structlog.get_logger()

# Create the SQLAlchemy engine from centralized config
engine = create_engine(config.database_url, echo=False)


def create_db_and_tables():
    """
    Create all tables defined by SQLModel models.
    Called once at application startup.
    """
    logger.info("Creating database tables", database_url=config.database_url.split("@")[-1])
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def get_session():
    """
    Dependency that provides a database session.
    Used with FastAPI's Depends() for automatic session management.

    Usage in a route:
        @app.get("/agents")
        def list_agents(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
