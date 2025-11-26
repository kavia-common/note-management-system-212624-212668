from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Shared fields for Note models."""
    title: str = Field(..., description="Title of the note", min_length=1)
    content: str = Field(..., description="Content/body of the note")
    pinned: bool = Field(False, description="Whether the note is pinned to the top")


# PUBLIC_INTERFACE
class NoteIn(NoteBase):
    """Payload for creating a new note."""
    pass


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Payload for updating an existing note (all fields optional)."""
    title: Optional[str] = Field(None, description="New title of the note", min_length=1)
    content: Optional[str] = Field(None, description="New content/body of the note")
    pinned: Optional[bool] = Field(None, description="Whether the note is pinned to the top")


# PUBLIC_INTERFACE
class NoteOut(NoteBase):
    """Representation of a note returned by the API."""
    id: int = Field(..., description="Unique identifier of the note")
    created_at: datetime = Field(..., description="ISO timestamp when note was created")
    updated_at: datetime = Field(..., description="ISO timestamp when note was last updated")
