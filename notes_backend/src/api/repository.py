from datetime import datetime, timezone
from typing import List, Optional

from .db import get_connection
from .models import NoteIn, NoteOut, NoteUpdate


def _row_to_note(row) -> NoteOut:
    """Convert sqlite Row to NoteOut."""
    return NoteOut(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        pinned=bool(row["pinned"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


# PUBLIC_INTERFACE
def list_notes(search: Optional[str] = None) -> List[NoteOut]:
    """List notes, optionally filtered by a search string in title or content.

    Sorted by pinned (desc) then updated_at (desc).
    """
    with get_connection(readonly=True) as conn:
        if search:
            like = f"%{search}%"
            rows = conn.execute(
                """
                SELECT * FROM notes
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY pinned DESC, datetime(updated_at) DESC
                """,
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM notes
                ORDER BY pinned DESC, datetime(updated_at) DESC
                """
            ).fetchall()
        return [_row_to_note(r) for r in rows]


# PUBLIC_INTERFACE
def get_note(note_id: int) -> Optional[NoteOut]:
    """Get a single note by ID. Returns None if not found."""
    with get_connection(readonly=True) as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if not row:
            return None
        return _row_to_note(row)


# PUBLIC_INTERFACE
def create_note(payload: NoteIn) -> NoteOut:
    """Create a new note and return it."""
    now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    with get_connection(readonly=False) as conn:
        cur = conn.execute(
            """
            INSERT INTO notes (title, content, pinned, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload.title, payload.content, 1 if payload.pinned else 0, now, now),
        )
        note_id = cur.lastrowid
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return _row_to_note(row)


# PUBLIC_INTERFACE
def update_note(note_id: int, updates: NoteUpdate) -> Optional[NoteOut]:
    """Update an existing note. Returns updated note or None if not found."""
    # Fetch existing to ensure it exists
    with get_connection(readonly=False) as conn:
        existing = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if not existing:
            return None

        # Build dynamic update set
        fields = []
        values = []
        if updates.title is not None:
            fields.append("title = ?")
            values.append(updates.title)
        if updates.content is not None:
            fields.append("content = ?")
            values.append(updates.content)
        if updates.pinned is not None:
            fields.append("pinned = ?")
            values.append(1 if updates.pinned else 0)

        # Always update updated_at
        fields.append("updated_at = ?")
        now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        values.append(now)

        if not fields:
            # No-op update, just return current row
            return _row_to_note(existing)

        values.append(note_id)
        conn.execute(f"UPDATE notes SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return _row_to_note(row)


# PUBLIC_INTERFACE
def delete_note(note_id: int) -> bool:
    """Delete a note by ID. Returns True if a row was deleted, False otherwise."""
    with get_connection(readonly=False) as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cur.rowcount > 0
