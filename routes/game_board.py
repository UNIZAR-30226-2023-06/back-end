import jwt

from werkzeug.security import generate_password_hash
from fastapi import APIRouter, Depends, HTTPException
from models.tablero import Board_Skins, Pieces_Skins, Profile_Pictures
from models.user import Has_Board_Skin, Has_Pieces_Skin, Has_Profile_Picture, User
from local_settings import  JWT_SECRET

from routes.auth import oauth2_scheme
from routes.auth import session

from models.user import User, Befriends
from routes.auth import session
from schemas.board import CreateBoardSkin, CreatePieceSkin, CreateProfilePicture

router = APIRouter()


############################################### BOARD SKINS #########################################################
@router.post("/add_board_skin", tags=["board"])
def add_board_skin(board_skin : str = Depends(CreateBoardSkin)):
    if session.query(Board_Skins).filter_by(name=board_skin.name).first():
        raise HTTPException(status_code=400, detail="Board skin already exists")
    new_skin = Board_Skins(name=board_skin.name, image=board_skin.image, description=board_skin.description, price=board_skin.price)
    session.add(new_skin)
    session.commit()
    return {"detail": "Board skin created successfully"}

# route for deleting a board skin from the database's Board_Skins table
@router.delete("/delete-board-skin", tags=["board"])
def delete_board_skin(board_skin_name : str):
    board_skin = session.query(Board_Skins).filter(Board_Skins.name == board_skin_name).first()
    if board_skin is None:
        raise HTTPException(status_code=404, detail="Board skin not found")
    else:
        session.delete(board_skin)
        session.commit()
        return {"detail": "Board skin deleted successfully"}

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
    
#route for listing a user's owned board skins
@router.get("/list-board-skins", tags=["board"])
def list_board_skins(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        if session.query(User).filter(User.id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            #get the user's owned board skins
            user = session.query(User).filter(User.id == user_id).first()
            board_skins_ids = session.query(Has_Board_Skin).filter(Has_Board_Skin.user_id == user.id).all()
            board_skins = []
            for board_skin_id in board_skins_ids:
                board_skin = session.query(Board_Skins).filter(Board_Skins.id == board_skin_id.board_skin_id).first()
                board_skins.append(board_skin.name)
            return {"board_skins": board_skins, "detail": "Board skins listed successfully"}

#route for listing all the board skins
@router.get("/list-all-board-skins", tags=["board"])
def list_all_board_skins():
    board_skins = session.query(Board_Skins).all()
    board_skins_list = []
    for board_skin in board_skins:
        board_skins_list.append(board_skin.name)
    return {"board_skins": board_skins_list, "detail": "Board skins listed successfully"}

#route for getting a board skin data
@router.get("/get-board-skin", tags=["board"])
def get_board_skin(board_skin_name : str):
    board_skin = session.query(Board_Skins).filter(Board_Skins.name == board_skin_name).first()
    if board_skin is None:
        raise HTTPException(status_code=404, detail="Board skin not found")
    else:
        return {"board_skin": board_skin.name, "image": board_skin.image, "description": board_skin.description, "price": board_skin.price, "detail": "Board skin data listed successfully"}
##########################################################################################################################



############################################### PROFILE PICTURES #########################################################

#create a piece skin
@router.post("/add_piece_skin", tags=["pieces"])
def add_piece_skin(piece_skin : str = Depends(CreatePieceSkin)):
    if session.query(Pieces_Skins).filter_by(name=piece_skin.name).first():
        raise HTTPException(status_code=400, detail="Piece skin already exists")
    new_skin = Pieces_Skins(name=piece_skin.name, image=piece_skin.image, description=piece_skin.description, price=piece_skin.price)
    session.add(new_skin)
    session.commit()
    return {"detail": "Piece skin created successfully"}

#route for deleting a piece skin from the database's Pieces_Skins table
@router.delete("/delete-piece-skin", tags=["pieces"])
def delete_piece_skin(piece_skin_name : str):
    piece_skin = session.query(Pieces_Skins).filter(Pieces_Skins.name == piece_skin_name).first()
    if piece_skin is None:
        raise HTTPException(status_code=404, detail="Piece skin not found")
    else:
        session.delete(piece_skin)
        session.commit()
        return {"detail": "Piece skin deleted successfully"}

#buy a piece skin
@router.post("/buy_piece_skin", tags=["pieces"])
def buy_piece_skin(piece_skin_name : str , token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="authenticated")
    elif not session.query(Pieces_Skins).filter_by(name=piece_skin_name).first():
        raise HTTPException(status_code=400, detail="Piece skin doesn't exist")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        user = session.query(User).filter(User.id == user_id).first()
        piece_skin = session.query(Pieces_Skins).filter(Pieces_Skins.name == piece_skin_name).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        #check whether the user already has the piece skin
        if session.query(Has_Pieces_Skin).filter(Has_Pieces_Skin.user_id == user_id, Has_Pieces_Skin.pieces_skin_id == piece_skin.id).first():
            raise HTTPException(status_code=400, detail="User already has this piece skin")
        
        #check whether the user has enough money
        if user.coins < piece_skin.price:
            raise HTTPException(status_code=400, detail="Not enough money")
        
        #add the piece skin to the user and subtract the price from the user's coins
        user.coins -= piece_skin.price
        has_piece_skin = Has_Pieces_Skin(user_id=user_id, pieces_skin_id=piece_skin.id)
        session.add(has_piece_skin)
        session.query(User).filter(User.id == user_id).update({User.coins: user.coins})
        session.commit()
        return {"detail": "Piece skin bought successfully"}     
    
#route for listing a user's owned piece skins
@router.get("/list-piece-skins", tags=["pieces"])
def list_piece_skins(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        if session.query(User).filter(User.id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            #get the user's owned piece skins
            user = session.query(User).filter(User.id == user_id).first()
            piece_skins_ids = session.query(Has_Pieces_Skin).filter(Has_Pieces_Skin.user_id == user.id).all()
            piece_skins = []
            for piece_skin_id in piece_skins_ids:
                piece_skin = session.query(Pieces_Skins).filter(Pieces_Skins.id == piece_skin_id.pieces_skin_id).first()
                piece_skins.append(piece_skin.name)
            return {"piece_skins": piece_skins, "detail": "Piece skins listed successfully"}
        

#route for listing all the piece skins
@router.get("/list-all-piece-skins", tags=["pieces"])
def list_all_piece_skins():
    piece_skins = session.query(Pieces_Skins).all()
    piece_skins_list = []
    for piece_skin in piece_skins:
        piece_skins_list.append(piece_skin.name)
    return {"piece_skins": piece_skins_list, "detail": "Piece skins listed successfully"}

#route for getting a piece skin's data
@router.get("/get-piece-skin", tags=["pieces"])
def get_piece_skin(piece_skin_name : str):
    piece_skin = session.query(Pieces_Skins).filter(Pieces_Skins.name == piece_skin_name).first()
    if piece_skin is None:
        raise HTTPException(status_code=404, detail="Piece skin not found")
    else:
        return {"id": piece_skin.id, "piece_skin": piece_skin.name, "image": piece_skin.image, "description": piece_skin.description, "price": piece_skin.price, "detail": "Piece skin data listed successfully"}

##########################################################################################################################


############################################### PROFILE PICTURES #########################################################

#route for adding a new profile picture
@router.post("/add_profile_picture", tags=["profile pictures"])
def add_profile_picture(profile_picture : str = Depends(CreateProfilePicture)):
    if session.query(Profile_Pictures).filter_by(name=profile_picture.name).first():
        raise HTTPException(status_code=400, detail="Profile picture already exists")
    new_picture = Profile_Pictures(name=profile_picture.name, image=profile_picture.image, description=profile_picture.description, price=profile_picture.price)
    session.add(new_picture)
    session.commit()
    return {"detail": "Profile picture created successfully"}

#route for deleting a profile picture from the database's Profile_Pictures table
@router.delete("/delete-profile-picture", tags=["profile pictures"])
def delete_profile_picture(profile_picture_name : str):
    profile_picture = session.query(Profile_Pictures).filter(Profile_Pictures.name == profile_picture_name).first()
    if profile_picture is None:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    else:
        session.delete(profile_picture)
        session.commit()
        return {"detail": "Profile picture deleted successfully"}

#route for buying a profile picture
@router.post("/buy_profile_picture", tags=["profile pictures"])
def buy_profile_picture(profile_picture_name : str , token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="authenticated")
    elif not session.query(Profile_Pictures).filter_by(name=profile_picture_name).first():
        raise HTTPException(status_code=400, detail="Profile picture doesn't exist")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        user = session.query(User).filter(User.id == user_id).first()
        profile_picture = session.query(Profile_Pictures).filter(Profile_Pictures.name == profile_picture_name).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        #check whether the user already has the profile picture
        if session.query(Has_Profile_Picture).filter(Has_Profile_Picture.user_id == user_id, Has_Profile_Picture.profile_picture_id == profile_picture.id).first():
            raise HTTPException(status_code=400, detail="User already has this profile picture")
        
        #check whether the user has enough money
        if user.coins < profile_picture.price:
            raise HTTPException(status_code=400, detail="Not enough money")
        
        #add the profile picture to the user and subtract the price from the user's coins
        user.coins -= profile_picture.price
        has_profile_picture = Has_Profile_Picture(user_id=user_id, profile_picture_id=profile_picture.id)
        session.add(has_profile_picture)
        session.query(User).filter(User.id == user_id).update({User.coins: user.coins})
        session.commit()
        return {"detail": "Profile picture bought successfully"}
    
#route for listing a user's owned profile pictures
@router.get("/list-profile-pictures", tags=["profile pictures"])
def list_profile_pictures(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        if session.query(User).filter(User.id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            #get the user's owned profile pictures
            user = session.query(User).filter(User.id == user_id).first()
            profile_pictures_ids = session.query(Has_Profile_Picture).filter(Has_Profile_Picture.user_id == user.id).all()
            profile_pictures = []
            for profile_picture_id in profile_pictures_ids:
                profile_picture = session.query(Profile_Pictures).filter(Profile_Pictures.id == profile_picture_id.profile_picture_id).first()
                profile_pictures.append(profile_picture.name)
            return {"profile_pictures": profile_pictures, "detail": "Profile pictures listed successfully"}
        
#route for listing all the profile pictures
@router.get("/list-all-profile-pictures", tags=["profile pictures"])
def list_all_profile_pictures():
    profile_pictures = session.query(Profile_Pictures).all()
    profile_pictures_list = []
    for profile_picture in profile_pictures:
        profile_pictures_list.append(profile_picture.name)
    return {"profile_pictures": profile_pictures_list, "detail": "Profile pictures listed successfully"}

#route for getting a profile picture's data
@router.get("/get-profile-picture", tags=["profile pictures"])
def get_profile_picture(profile_picture_name : str):
    profile_picture = session.query(Profile_Pictures).filter(Profile_Pictures.name == profile_picture_name).first()
    if profile_picture is None:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    else:
        return {"id": profile_picture.id, "profile_picture": profile_picture.name, "image": profile_picture.image, "description": profile_picture.description, "price": profile_picture.price, "detail": "Profile picture data listed successfully"}

##########################################################################################################################
