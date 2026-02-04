from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high)$")
    status: Optional[str] = Field(default="pending", pattern="^(pending|in_progress|completed)$")
    assigned_to: Optional[int] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    assigned_to: Optional[int] = None
    is_completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: int
    created_by: int
    is_completed: bool
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True
