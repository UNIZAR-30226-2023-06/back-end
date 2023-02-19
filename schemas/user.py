from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None


class UserCreate(UserBase):
    email: str
    hashed_password: str


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
