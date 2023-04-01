from pydantic import BaseModel, EmailStr, SecretStr


class BoardSkinBase(BaseModel):
    name: str | None
    description: str | None
    image: str | None
    price: int | None

class CreateBoardSkin(BoardSkinBase):
    name: str
    price: int 
    description: str = "No description"
    image: str = "default.png"


class PieceSkinBase(BaseModel):
    name: str | None
    description: str | None
    image: str | None
    price: int | None

class CreatePieceSkin(PieceSkinBase):
    name: str
    price: int 
    description: str = "No description"
    image: str = "default.png"

class ProfilePictureBase(BaseModel):
    name: str | None
    description: str | None
    image: str | None
    price: int | None

class CreateProfilePicture(ProfilePictureBase):
    name: str
    price: int 
    description: str = "No description"
    image: str = "default.png"