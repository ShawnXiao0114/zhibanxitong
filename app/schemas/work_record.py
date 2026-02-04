from pydantic import BaseModel
from datetime import date
from typing import Optional

class WorkRecordBase(BaseModel):
    date: date
    time_slot: Optional[str] = None
    student_id: int
    content: str
    handover_notes: Optional[str] = None

class WorkRecordCreate(WorkRecordBase):
    pass

class WorkRecordUpdate(BaseModel):
    time_slot: Optional[str] = None
    content: Optional[str] = None
    handover_notes: Optional[str] = None
    status: Optional[str] = None

class WorkRecordResponse(WorkRecordBase):
    id: int
    status: str
    student_name: Optional[str] = None

    class Config:
        from_attributes = True

class WorkRecordHandover(BaseModel):
    handover_notes: str
    next_student_id: int
