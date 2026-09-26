"""
Database Engine and Session Lifecycle Management for SQLite.
Configures foreign key enforcement and connection isolation.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from student42.core.config import get_paths
from student42.database.models import Base


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record) -> None: # type: ignore
    """Ensure SQLite enforces foreign key constraints on every connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


class DatabaseManager:
    """Controls connection pooling, schema initialization, and sessions."""

    def __init__(self, db_path_override: str | None = None) -> None:
        if db_path_override:
            self.db_url = f"sqlite:///{db_path_override}"
        else:
            paths = get_paths()
            self.db_url = f"sqlite:///{paths.database_file}"

        self.engine = create_engine(
            self.db_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def init_db(self) -> None:
        """Create all tables if they do not exist."""
        Base.metadata.create_all(bind=self.engine)

    def reset_db(self) -> None:
        """Drop and recreate all tables (use with caution in tests)."""
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Context manager providing transactional session handling."""
        session: Session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Singleton Instance
_db_manager: DatabaseManager | None = None


def get_db_manager(override_path: str | None = None) -> DatabaseManager:
    """Retrieves or creates the database manager singleton."""
    global _db_manager
    if _db_manager is None or override_path is not None:
        _db_manager = DatabaseManager(db_path_override=override_path)
        _db_manager.init_db()
    return _db_manager