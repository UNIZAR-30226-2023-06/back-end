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
    if session.query(Board_Skins).filter_by(name=board_skin.name).first():
        raise HTTPException(status_code=400, detail="Board skin already exists")
    new_skin = Board_Skins(name=board_skin.name, image=board_skin.image, description=board_skin.description, price=board_skin.price)
    session.add(new_skin)
    session.commit()
    return {"detail": "Board skin created successfully"}

@router.post("/buy_board_skin", tags=["board"])
def buy_board_skin(board_skin_name : str , token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="authenticated")
    elif not session.query(Board_Skins).filter_by(name=board_skin_name).first():
        raise HTTPException(status_code=400, detail="Board skin doesn't exist")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        user = session.query(User).filter(User.id == user_id).first()
        board_skin = session.query(Board_Skins).filter(Board_Skins.name == board_skin_name).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        #check whether the user already has the board skin
        if session.query(Has_Board_Skin).filter(Has_Board_Skin.user_id == user_id, Has_Board_Skin.board_skin_id == board_skin.id).first():
            raise HTTPException(status_code=400, detail="User already has this board skin")
        
        #check whether the user has enough money
        if user.coins < board_skin.price:
            raise HTTPException(status_code=400, detail="Not enough money")
        
        #add the board skin to the user and subtract the price from the user's coins
        user.coins -= board_skin.price
        has_board_skin = Has_Board_Skin(user_id=user_id, board_skin_id=board_skin.id)
        session.add(has_board_skin)
        session.query(User).filter(User.id == user_id).update({User.coins: user.coins})
        session.commit()
        return {"detail": "Board skin bought successfully"}

        

        