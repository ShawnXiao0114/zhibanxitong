from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models.student import Student
from app.models.work_record import WorkRecord
from app.models.todo import Todo
from app.models.schedule import Schedule
from app.schemas.student import StudentCreate, StudentUpdate, StudentAdminUpdate, StudentPasswordReset, StudentResponse
from app.utils.auth import get_password_hash
from app.routes.auth import get_current_user, get_current_admin

router = APIRouter()

@router.post("/", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    # 检查用户名是否已存在
    existing_student = db.query(Student).filter(Student.username == student_data.username).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # 创建新学生
    hashed_password = get_password_hash(student_data.password)
    new_student = Student(
        name=student_data.name,
        username=student_data.username,
        password_hash=hashed_password,
        phone=student_data.phone,
        email=student_data.email,
        department=student_data.department,
        class_=student_data.class_name,
        gender=student_data.gender,
        is_admin=student_data.is_admin,
        is_password_set=False
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@router.get("/", response_model=List[StudentResponse])
async def get_students(
    search: Optional[str] = Query(None, description="Search by student ID or name"),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    query = db.query(Student)
    if search:
        query = query.filter(
            (Student.username == search) | (Student.name.contains(search))
        )
    # 按学号从小到大排序
    query = query.order_by(Student.username.asc())
    return query.all()

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 只有管理员或学生本人可以访问
    if not current_user.is_admin and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 只有管理员或学生本人可以修改
    if not current_user.is_admin and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 更新学生信息
    update_data = student_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student

@router.put("/{student_id}/reset-password")
async def reset_password(
    student_id: int,
    password_data: StudentPasswordReset,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 重置密码
    hashed_password = get_password_hash(password_data.new_password)
    student.password_hash = hashed_password
    student.is_password_set = False
    db.commit()
    return {"message": "Password reset successfully"}

@router.put("/{student_id}/admin", response_model=StudentResponse)
async def set_admin(
    student_id: int,
    admin_data: StudentAdminUpdate,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 设置管理员权限
    student.is_admin = admin_data.is_admin
    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 不能删除管理员
    if student.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin user"
        )
    
    # 删除相关的工作记录
    db.query(WorkRecord).filter(WorkRecord.student_id == student_id).delete()
    
    # 删除相关的待办事项（作为分配人）
    db.query(Todo).filter(Todo.assigned_to == student_id).delete()
    
    # 删除相关的待办事项（作为创建人）
    db.query(Todo).filter(Todo.created_by == student_id).delete()
    
    # 删除相关的值班安排
    db.query(Schedule).filter(Schedule.student_id == student_id).delete()
    
    # 删除学生
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

@router.post("/change-password")
async def change_password(
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    if not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be empty"
        )
    
    # 更新密码哈希
    current_user.password_hash = get_password_hash(new_password)
    current_user.is_password_set = True
    db.commit()
    
    return {"message": "Password changed successfully"}
