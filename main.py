from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.routes import auth, students, schedules, work_records, todos
from app.database.database import engine, Base
from app.models import student, schedule, work_record, todo

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="值班管理系统",
    description="值班管理系统后端API",
    version="1.0.0"
)

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth, prefix="/auth", tags=["认证"])
app.include_router(students, prefix="/students", tags=["学生管理"])
app.include_router(schedules, prefix="/schedules", tags=["排班管理"])
app.include_router(work_records, prefix="/work-records", tags=["工作记录"])
app.include_router(todos, prefix="/todos", tags=["待办事项"])

@app.get("/")
def read_root():
    # 重定向到登录页面
    return RedirectResponse(url="/static/login.html")

@app.get("/login")
def login_page():
    # 登录页面路由
    return RedirectResponse(url="/static/login.html")
