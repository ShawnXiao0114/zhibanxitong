from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.student import Student
from app.schemas.auth import Token, TokenData
from app.utils.auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    student = db.query(Student).filter(Student.username == username).first()
    if student is None:
        raise credentials_exception
    return student

async def get_current_admin(current_user: Student = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.username == form_data.username).first()
    if not student or not verify_password(form_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 更新登录状态
    student.is_active = True
    student.last_login = datetime.now()
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": student.username, "student_id": student.id, "is_admin": student.is_admin},
        expires_delta=access_token_expires
    )
    
    # 检查是否需要强制更改密码
    require_password_change = not student.is_admin and not student.is_password_set
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "require_password_change": require_password_change
    }
