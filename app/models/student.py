from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_password_set = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    department = Column(String(50), nullable=True)
    class_ = Column('class', String(50), nullable=True)
    gender = Column(String(10), nullable=True)

    # 关系
    schedules = relationship("Schedule", back_populates="student")
    work_records = relationship("WorkRecord", back_populates="student")
