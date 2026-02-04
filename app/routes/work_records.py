from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database.database import get_db
from app.models.work_record import WorkRecord
from app.models.student import Student
from app.schemas.work_record import WorkRecordCreate, WorkRecordUpdate, WorkRecordResponse, WorkRecordHandover
from app.routes.auth import get_current_user, get_current_admin

router = APIRouter()

@router.post("/", response_model=WorkRecordResponse)
async def create_work_record(
    record_data: WorkRecordCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    # 检查学生是否存在
    student = db.query(Student).filter(Student.id == record_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 只有管理员或学生本人可以创建工作记录
    if not current_user.is_admin and current_user.id != record_data.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 创建新工作记录
    new_record = WorkRecord(**record_data.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    # 添加学生姓名
    response = WorkRecordResponse.model_validate(new_record)
    response.student_name = student.name
    return response

@router.get("/", response_model=List[WorkRecordResponse])
async def get_work_records(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    student_id: Optional[int] = Query(None, description="Filter by student ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    query = db.query(WorkRecord)
    if start_date:
        query = query.filter(WorkRecord.date >= start_date)
    if end_date:
        query = query.filter(WorkRecord.date <= end_date)
    if student_id:
        query = query.filter(WorkRecord.student_id == student_id)
    if status:
        query = query.filter(WorkRecord.status == status)
    records = query.all()
    # 添加学生姓名
    response = []
    for record in records:
        record_response = WorkRecordResponse.model_validate(record)
        student = db.query(Student).filter(Student.id == record.student_id).first()
        if student:
            record_response.student_name = student.name
        response.append(record_response)
    return response

@router.get("/{record_id}", response_model=WorkRecordResponse)
async def get_work_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    record = db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work record not found"
        )
    # 添加学生姓名
    response = WorkRecordResponse.model_validate(record)
    student = db.query(Student).filter(Student.id == record.student_id).first()
    if student:
        response.student_name = student.name
    return response

@router.put("/{record_id}", response_model=WorkRecordResponse)
async def update_work_record(
    record_id: int,
    record_data: WorkRecordUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    record = db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work record not found"
        )
    # 只有管理员或学生本人可以修改工作记录
    if not current_user.is_admin and current_user.id != record.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 更新工作记录
    update_data = record_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    # 添加学生姓名
    response = WorkRecordResponse.model_validate(record)
    student = db.query(Student).filter(Student.id == record.student_id).first()
    if student:
        response.student_name = student.name
    return response

@router.delete("/{record_id}")
async def delete_work_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    record = db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work record not found"
        )
    # 只有管理员或学生本人可以删除工作记录
    if not current_user.is_admin and current_user.id != record.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    db.delete(record)
    db.commit()
    return {"message": "Work record deleted successfully"}
