from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserCreate(UserBase):
    name: str
    email: EmailStr
    password: str


# class UserRead(UserBase):
#     id: int
#     email: str

#     class Config:
#         orm_mode = True


# class UserUpdate(UserBase):
#     name: Optional[str] = None
#     email: Optional[str] = None
#     hashed_password: Optional[str] = None


# class UserDelete(BaseModel):
#     id: int
