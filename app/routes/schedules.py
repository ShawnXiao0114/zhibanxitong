from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.database.database import get_db
from app.models.schedule import Schedule
from app.models.student import Student
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, CalendarView
from app.routes.auth import get_current_user, get_current_admin

router = APIRouter()

@router.post("/", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    # 检查学生是否存在
    student = db.query(Student).filter(Student.id == schedule_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 创建新排班
    new_schedule = Schedule(**schedule_data.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    # 添加学生姓名
    response = ScheduleResponse.model_validate(new_schedule)
    response.student_name = student.name
    return response

@router.get("/", response_model=List[ScheduleResponse])
async def get_schedules(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    student_id: Optional[int] = Query(None, description="Filter by student ID"),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    query = db.query(Schedule)
    if start_date:
        query = query.filter(Schedule.date >= start_date)
    if end_date:
        query = query.filter(Schedule.date <= end_date)
    if student_id:
        query = query.filter(Schedule.student_id == student_id)
    schedules = query.all()
    # 添加学生姓名
    response = []
    for schedule in schedules:
        schedule_response = ScheduleResponse.model_validate(schedule)
        student = db.query(Student).filter(Student.id == schedule.student_id).first()
        if student:
            schedule_response.student_name = student.name
        response.append(schedule_response)
    return response

@router.get("/calendar/{year}/{month}", response_model=List[CalendarView])
async def get_calendar_view(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    # 计算月份的开始和结束日期
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    # 获取该月的所有排班
    schedules = db.query(Schedule).filter(
        Schedule.date >= start_date,
        Schedule.date <= end_date
    ).all()
    # 按日期分组
    date_schedules = {}
    for schedule in schedules:
        if schedule.date not in date_schedules:
            date_schedules[schedule.date] = []
        schedule_response = ScheduleResponse.model_validate(schedule)
        student = db.query(Student).filter(Student.id == schedule.student_id).first()
        if student:
            schedule_response.student_name = student.name
        date_schedules[schedule.date].append(schedule_response)
    # 生成日历视图
    calendar = []
    current_day = start_date
    while current_day <= end_date:
        calendar.append(CalendarView(
            date=current_day,
            schedules=date_schedules.get(current_day, [])
        ))
        current_day += timedelta(days=1)
    return calendar

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    # 更新排班信息
    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    db.commit()
    db.refresh(schedule)
    # 添加学生姓名
    response = ScheduleResponse.model_validate(schedule)
    student = db.query(Student).filter(Student.id == schedule.student_id).first()
    if student:
        response.student_name = student.name
    return response

@router.delete("/batch-delete")
async def batch_delete_schedules(
    start_date: date = Query(..., description="Start date for batch deletion"),
    end_date: date = Query(..., description="End date for batch deletion"),
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    schedules = db.query(Schedule).filter(
        Schedule.date >= start_date,
        Schedule.date <= end_date
    ).all()
    
    if not schedules:
        return {"message": "No schedules found in the specified date range"}
    
    deleted_count = len(schedules)
    for schedule in schedules:
        db.delete(schedule)
    db.commit()
    
    return {"message": f"Successfully deleted {deleted_count} schedules"}

@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}
