from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database.database import get_db
from app.models.todo import Todo
from app.models.student import Student
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.routes.auth import get_current_user, get_current_admin

router = APIRouter()

@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    # 检查被分配人是否存在
    if todo_data.assigned_to:
        assignee = db.query(Student).filter(Student.id == todo_data.assigned_to).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned student not found"
            )
    # 创建新待办事项
    new_todo = Todo(
        **todo_data.model_dump(),
        created_by=current_user.id
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    # 构建响应
    response = TodoResponse.model_validate(new_todo)
    if new_todo.assignee:
        response.assignee_name = new_todo.assignee.name
    response.creator_name = current_user.name
    return response

@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned student"),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    query = db.query(Todo)
    # 普通用户只能看到分配给自己的或自己创建的
    if not current_user.is_admin:
        query = query.filter(
            (Todo.assigned_to == current_user.id) | (Todo.created_by == current_user.id)
        )
    # 应用过滤
    if status:
        query = query.filter(Todo.status == status)
    if priority:
        query = query.filter(Todo.priority == priority)
    if assigned_to:
        query = query.filter(Todo.assigned_to == assigned_to)
    todos = query.all()
    # 构建响应
    response = []
    for todo in todos:
        todo_response = TodoResponse.model_validate(todo)
        if todo.assignee:
            todo_response.assignee_name = todo.assignee.name
        if todo.creator:
            todo_response.creator_name = todo.creator.name
        response.append(todo_response)
    return response

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    # 检查权限
    if not current_user.is_admin and todo.assigned_to != current_user.id and todo.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 构建响应
    response = TodoResponse.model_validate(todo)
    if todo.assignee:
        response.assignee_name = todo.assignee.name
    if todo.creator:
        response.creator_name = todo.creator.name
    return response

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    # 检查权限
    if not current_user.is_admin and todo.assigned_to != current_user.id and todo.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 检查被分配人是否存在
    if todo_data.assigned_to:
        assignee = db.query(Student).filter(Student.id == todo_data.assigned_to).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned student not found"
            )
    # 更新待办事项
    update_data = todo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    # 同步状态和完成状态
    if todo.status == "completed":
        todo.is_completed = True
    elif todo.status in ["pending", "in_progress"]:
        todo.is_completed = False
    db.commit()
    db.refresh(todo)
    # 构建响应
    response = TodoResponse.model_validate(todo)
    if todo.assignee:
        response.assignee_name = todo.assignee.name
    if todo.creator:
        response.creator_name = todo.creator.name
    return response

@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    # 检查权限
    if not current_user.is_admin and todo.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@router.post("/{todo_id}/complete")
async def complete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    # 检查权限
    if not current_user.is_admin and todo.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 标记为完成
    todo.status = "completed"
    todo.is_completed = True
    db.commit()
    return {"message": "Todo marked as completed"}
