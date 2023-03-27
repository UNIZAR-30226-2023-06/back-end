from pydantic import BaseModel, EmailStr, SecretStr


class UserBase(BaseModel):
    name: str | None
    email: EmailStr | None
    password: SecretStr | None
    coins: int | None
    selected_grid_skin: str | None
    selected_piece_skin: str | None
    saved_music: str | None
    elo: int | None
    profile_picture: str | None


class UserCreate(UserBase):
    name: str
    email: EmailStr
    password: SecretStr
    coins: int = 0
    selected_grid_skin: str = 'default'
    selected_piece_skin: str = 'default'
    saved_music: str = 'default'
    elo: int = 500
    profile_picture: str = 'default'

class UserLogin(BaseModel):
    email: EmailStr
    password: str