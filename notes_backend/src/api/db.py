import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def _default_db_path() -> str:
    """Resolve the default database path to a sibling notes_database/myapp.db"""
    # notes_backend/src/api/db.py -> notes_backend
    backend_root = Path(__file__).resolve().parents[2]
    # sibling container root is assumed to be notes_database at same level as notes_backend
    sibling_db_dir = backend_root.parent / "notes_database"
    # Ensure directory exists (do not create file yet)
    sibling_db_dir.mkdir(parents=True, exist_ok=True)
    return str(sibling_db_dir / "myapp.db")


def get_db_path() -> str:
    """Get database path from env NOTES_DB_PATH or use default sibling path."""
    return os.environ.get("NOTES_DB_PATH", _default_db_path())


def initialize_db_schema(conn: sqlite3.Connection) -> None:
    """Create notes table if it does not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            pinned INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


# PUBLIC_INTERFACE
@contextmanager
def get_connection(readonly: Optional[bool] = False) -> Iterator[sqlite3.Connection]:
    """Context manager to get a sqlite3 connection.

    Set readonly=True to open in read-only mode when possible.
    Ensures foreign keys pragma and proper row factory for dict-like access.
    Also ensures database schema is initialized on first write connection.
    """
    db_path = get_db_path()
    # Build URI for potential readonly mode
    if readonly:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
    else:
        # Ensure directory exists before creating db
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        # Initialize schema for write connections
        initialize_db_schema(conn)

    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
    finally:
        conn.close()
