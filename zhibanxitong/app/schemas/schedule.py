from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class ScheduleBase(BaseModel):
    date: date
    student_id: int
    time_slot: str
    location: Optional[str] = None
    notes: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    student_id: Optional[int] = None
    time_slot: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    id: int
    student_name: Optional[str] = None

    class Config:
        from_attributes = True

class CalendarView(BaseModel):
    date: date
    schedules: List[ScheduleResponse]
