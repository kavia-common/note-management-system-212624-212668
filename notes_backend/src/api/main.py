from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import NoteIn, NoteOut, NoteUpdate
from .repository import create_note, delete_note, get_note, list_notes, update_note

app = FastAPI(
    title="Notes Backend API",
    description="REST API for managing notes (create, read, update, delete) backed by SQLite.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Service health endpoints"},
        {"name": "notes", "description": "CRUD operations for notes"},
    ],
)

# Keep permissive CORS for development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set specific origins via env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Return a simple health message to confirm the service is running."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/notes",
    response_model=List[NoteOut],
    tags=["notes"],
    summary="List notes",
    description="List all notes optionally filtered by a search string in the title or content. Sorted by pinned (desc) then updated_at (desc).",
)
def list_notes_endpoint(search: Optional[str] = Query(None, description="Search string to filter by title or content")):
    """List notes with optional search."""
    return list_notes(search=search)


# PUBLIC_INTERFACE
@app.get(
    "/notes/{note_id}",
    response_model=NoteOut,
    tags=["notes"],
    summary="Get a note",
    description="Retrieve a single note by its ID.",
)
def get_note_endpoint(note_id: int = Path(..., description="ID of the note to retrieve")):
    """Get a note by ID."""
    note = get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=NoteOut,
    status_code=201,
    tags=["notes"],
    summary="Create a note",
    description="Create a new note with title, content, and optional pinned flag.",
)
def create_note_endpoint(payload: NoteIn):
    """Create a new note."""
    return create_note(payload)


# PUBLIC_INTERFACE
@app.put(
    "/notes/{note_id}",
    response_model=NoteOut,
    tags=["notes"],
    summary="Update a note",
    description="Update fields of an existing note. Automatically updates updated_at.",
)
def update_note_endpoint(
    payload: NoteUpdate,
    note_id: int = Path(..., description="ID of the note to update"),
):
    """Update an existing note by ID."""
    updated = update_note(note_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated


# PUBLIC_INTERFACE
@app.delete(
    "/notes/{note_id}",
    status_code=204,
    tags=["notes"],
    summary="Delete a note",
    description="Delete a note by its ID.",
)
def delete_note_endpoint(note_id: int = Path(..., description="ID of the note to delete")):
    """Delete a note by ID."""
    deleted = delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
