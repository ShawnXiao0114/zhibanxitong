from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base

class WorkRecord(Base):
    __tablename__ = "work_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    time_slot = Column(String(50), nullable=True)  # 时段，例如：上午、下午、晚上
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    content = Column(Text, nullable=False)
    handover_notes = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, completed

    # 关系
    student = relationship("Student", back_populates="work_records")
