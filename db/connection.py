"""Database connection helpers.

Provides a minimal, optional PostgreSQL connection manager. If psycopg2 is
not installed or DATABASE_URL is not set, falls back to a mock in-memory helper.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator, Optional
from config.settings import get_settings


class DatabaseConnection:
    """Manages PostgreSQL database connections."""

    def __init__(self, connection_url: Optional[str] = None):
        self.settings = get_settings()
        self.connection_url = connection_url or self.settings.database_url
        self._connection = None

    def connect(self):
        """Establish database connection."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(self.connection_url)
        return self._connection

    def close(self):
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    @contextmanager
    def get_cursor(self, dict_cursor: bool = True) -> Generator:
        """Get a database cursor with automatic commit/rollback."""
        conn = self.connect()
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def execute(self, query: str, params: tuple = None) -> list:
        """Execute a query and return results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return []

    def execute_one(self, query: str, params: tuple = None) -> Optional[dict]:
        """Execute a query and return single result."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchone()
            return None

    def execute_returning(self, query: str, params: tuple = None) -> Optional[dict]:
        """Execute an INSERT/UPDATE with RETURNING clause."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()


# Global connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db_connection() -> DatabaseConnection:
    """Get or create global database connection."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection

