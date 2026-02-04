from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    time_slot = Column(String(20), nullable=False)  # 例如：上午、下午、晚上
    location = Column(String(50), nullable=True)
    notes = Column(String(200), nullable=True)

    # 关系
    student = relationship("Student", back_populates="schedules")
