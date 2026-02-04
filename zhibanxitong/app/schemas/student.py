from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentBase(BaseModel):
    name: str
    username: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    class_name: Optional[str] = None
    gender: Optional[str] = None

class StudentCreate(StudentBase):
    password: str
    is_admin: Optional[bool] = False

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    class_name: Optional[str] = None
    gender: Optional[str] = None
    is_admin: Optional[bool] = None
    is_password_set: Optional[bool] = None

class StudentAdminUpdate(BaseModel):
    is_admin: bool

class StudentPasswordReset(BaseModel):
    new_password: str

class StudentResponse(StudentBase):
    id: int
    is_admin: bool
    is_password_set: bool
    is_active: bool

    class Config:
        from_attributes = True
