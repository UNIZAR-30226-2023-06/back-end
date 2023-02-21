from pydantic import BaseModel, EmailStr, SecretStr


class UserBase(BaseModel):
    name: str | None
    email: EmailStr | None
    password: SecretStr | None


class UserCreate(UserBase):
    name: str
    email: EmailStr
    password: SecretStr


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
