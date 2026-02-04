from app.routes.auth import router as auth_router
from app.routes.students import router as students_router
from app.routes.schedules import router as schedules_router
from app.routes.work_records import router as work_records_router
from app.routes.todos import router as todos_router

# 导出路由模块，方便main.py导入
auth = auth_router
students = students_router
schedules = schedules_router
work_records = work_records_router
todos = todos_router

__all__ = ["auth", "students", "schedules", "work_records", "todos"]
