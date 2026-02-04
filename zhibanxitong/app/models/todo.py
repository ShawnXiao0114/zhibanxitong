from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database.database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    assigned_to = Column(Integer, ForeignKey("students.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("students.id"), nullable=False)
    is_completed = Column(Boolean, default=False)

    # 关系
    assignee = relationship("Student", foreign_keys=[assigned_to], backref="assigned_todos")
    creator = relationship("Student", foreign_keys=[created_by], backref="created_todos")
