import jwt

from werkzeug.security import generate_password_hash
from fastapi import APIRouter, Depends, HTTPException
from models.tablero import Board_Skins
from models.user import Has_Board_Skin, Has_Pieces_Skin, User
from local_settings import  JWT_SECRET

from routes.auth import oauth2_scheme
from routes.auth import session

from models.user import User, Befriends
from routes.auth import session
from schemas.board import CreateBoardSkin

router = APIRouter()

@router.post("/add_board_skin", tags=["board"])
def add_board_skin(board_skin : str = Depends(CreateBoardSkin)):
    new_skin = Board_Skins(name=board_skin.name, image=board_skin.image, description=board_skin.description, price=board_skin.price)
    session.add(new_skin)
    session.commit()
    return {"message": "Board skin created successfully"}