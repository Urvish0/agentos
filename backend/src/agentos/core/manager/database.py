"""
Database connection module for AgentOS.

Uses SQLModel (SQLAlchemy + Pydantic) with PostgreSQL.
Provides session management and table creation utilities.
"""

import os
from sqlmodel import SQLModel, Session, create_engine
import structlog

logger = structlog.get_logger()

# Read the DATABASE_URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://agentos:agentos_password@localhost:5432/agentos_db"
)

# Create the SQLAlchemy engine
# echo=True logs all SQL statements (useful for debugging, disable in production)
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """
    Create all tables defined by SQLModel models.
    Called once at application startup.
    """
    logger.info("Creating database tables", database_url=DATABASE_URL.split("@")[-1])
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
