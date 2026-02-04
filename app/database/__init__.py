from app.database.database import Base, engine
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.work_record import WorkRecord

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)

__all__ = ["init_db", "Base", "engine"]
