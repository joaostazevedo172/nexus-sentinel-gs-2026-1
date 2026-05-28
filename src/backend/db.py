"""SQLModel database setup.

Local dev:    SQLite (./nexus.db) — DATABASE_URL not set
Production:   Postgres            — DATABASE_URL set by Render/Neon/Supabase

The schema is the same in both cases; SQLModel/SQLAlchemy handles the
dialect differences automatically.
"""
import os
from datetime import datetime
from typing import Generator, Optional

from sqlmodel import Field, Session, SQLModel, create_engine


class TransactionDB(SQLModel, table=True):
    """Persisted blockchain transaction. Maps to ``models.Transaction``."""
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    hash: str = Field(index=True)
    region: str = Field(index=True)
    action: str
    reward: int
    time: str
    fed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


# Local SQLite or remote Postgres (via DATABASE_URL)
# Render injects DATABASE_URL automatically when you add a Postgres add-on.
# Neon/Supabase: copy the connection string from their dashboard.
_DB_URL = os.getenv("DATABASE_URL", "sqlite:///./nexus.db")

# Render/Heroku give us postgres:// but SQLAlchemy needs postgresql://
if _DB_URL.startswith("postgres://"):
    _DB_URL = _DB_URL.replace("postgres://", "postgresql://", 1)

_is_sqlite = _DB_URL.startswith("sqlite")
engine = create_engine(
    _DB_URL,
    echo=False,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,   # health-check connections in Postgres
)


def init_db() -> None:
    """Create tables if they don't exist. Called at FastAPI startup."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
