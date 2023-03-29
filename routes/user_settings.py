import re
import jwt

from werkzeug.security import generate_password_hash
from fastapi import APIRouter, Depends, HTTPException
from models.user import Has_Board_Skin, Has_Pieces_Skin, User
from local_settings import  JWT_SECRET

from routes.auth import oauth2_scheme
from routes.auth import session

from models.user import User, Befriends

router = APIRouter()

is_valid_email = lambda email: re.match(r"[^@]+@[^@]+\.[^@]+", email) #checks if the email is valid

from routes.auth import session
#gets a user from the database given the user id
@router.get("/get-user-from-id/{user_id}", tags=["user_settings"])
def get_user(user_id: int):
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
      return user
    
#gets a user from the database given the user email
@router.get("/get-user-from-email/{email}", tags=["user_settings"])
def get_user_by_email(email: str):
    #if the email is not a valid email, return an error
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
  
    user = session.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
      return user


#route for changing a user's username
@router.post("/change-username", tags=["user_settings"])
def change_username(new_username: str, token: str = Depends(oauth2_scheme)):
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
            #update the username in the database
            session.query(User).filter(User.id == user_id).update({User.username: new_username})
            session.commit()
            new_user = session.query(User).filter(User.id == user_id).first()
            user_dict = {"id": new_user.id, "username": new_user.username, "email": new_user.email}          
            token = jwt.encode(user_dict, JWT_SECRET)
            return {"access_token": token, "token_type": "bearer", "detail": "Username changed successfully"}
        
#route for changing a user's email
@router.post("/change-email", tags=["user_settings"])
def change_email(new_email: str, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    elif not is_valid_email(new_email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        if session.query(User).filter(User.id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            #update the email in the database
            session.query(User).filter(User.id == user_id).update({User.email: new_email})
            session.commit()
            new_user = session.query(User).filter(User.id == user_id).first()
            user_dict = {"id": new_user.id, "username": new_user.username, "email": new_user.email}          
            token = jwt.encode(user_dict, JWT_SECRET)
            return {"access_token": token, "token_type": "bearer", "detail": "Email changed successfully"}
        
#route for changing a user's password
@router.post("/change-password", tags=["user_settings"])
def change_password(new_password: str, token: str = Depends(oauth2_scheme)):
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
            #update the password in the database
            hashed_new_password = generate_password_hash(new_password, method='sha256')
            session.query(User).filter(User.id == user_id).update({User.password: hashed_new_password})
            session.commit()
            new_user = session.query(User).filter(User.id == user_id).first()
            user_dict = {"id": new_user.id, "username": new_user.username, "email": new_user.email}
            token = jwt.encode(user_dict, JWT_SECRET)
            return {"access_token": token, "token_type": "bearer", "detail": "Password changed successfully"}
        
#delete a user from the database
@router.delete("/delete-user", tags=["user_settings"])
def delete_user(token: str = Depends(oauth2_scheme)):
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
            #delete the user from the database
            #first, delete all the user appearances in the befriends table
            session.query(Befriends).filter(Befriends.user_id == user_id).delete()
            session.query(Befriends).filter(Befriends.friend_id == user_id).delete()
            #then, delete all the user appearances in has_board_skin table
            session.query(Has_Board_Skin).filter(Has_Board_Skin.user_id == user_id).delete()
            #then, delete all the user appearancdes in the has_piece_skin table
            session.query(Has_Pieces_Skin).filter(Has_Pieces_Skin.user_id == user_id).delete()
            #finally, delete the user from the user table
            session.query(User).filter(User.id == user_id).delete()
            session.commit()
            return {"detail": "User deleted successfully"}

#!##################################################
#! A partir de aquí las funciones están sin probar #
#!##################################################

#add an amount of coins to a user's balance
@router.post("/add-coins", tags=["user_settings"])
def add_coins(amount: int, token: str = Depends(oauth2_scheme)):
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
            #add the coins to the user's balance
            user = session.query(User).filter(User.id == user_id).first()
            user.coins += amount
            session.commit()
            new_amount = user.coins
            return {"coins": new_amount, "detail": "Coins added successfully"}
        
#remove an amount of coins from a user's balance
@router.post("/remove-coins", tags=["user_settings"])
def remove_coins(amount: int, token: str = Depends(oauth2_scheme)):
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
            #remove the coins from the user's balance
            user = session.query(User).filter(User.id == user_id).first()
            if user.coins < amount:
                raise HTTPException(status_code=400, detail="Not enough coins")
            user.coins -= amount
            new_amount = user.coins
            session.commit()
            return {"coins": new_amount, "detail": "Coins removed successfully"}

#route for modifying a user's selected grid skin
@router.post("/change-grid-skin", tags=["user_settings"])
def change_grid_skin(new_grid_skin: str, token: str = Depends(oauth2_scheme)):
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
            #update the grid skin in the database
            session.query(User).filter(User.id == user_id).update({User.selected_grid_skin: new_grid_skin})
            session.commit()
            return {"detail": "Grid skin changed successfully to " + new_grid_skin}
        
#route for modifying a user's selected pieces skin
@router.post("/change-pieces-skin", tags=["user_settings"])
def change_pieces_skin(new_pieces_skin: str, token: str = Depends(oauth2_scheme)):
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
            #update the pieces skin in the database
            session.query(User).filter(User.id == user_id).update({User.selected_pieces_skin: new_pieces_skin})
            session.commit()
            return {"detail": "Pieces skin changed successfully to " + new_pieces_skin}
        
    #route for changing a user's profile picture
@router.post("/change-profile-picture", tags=["user_settings"])
def change_profile_picture(new_profile_picture: str, token: str = Depends(oauth2_scheme)):
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
            #update the profile picture in the database
            session.query(User).filter(User.id == user_id).update({User.profile_picture: new_profile_picture})
            session.commit()
            return {"detail": "Profile picture changed successfully to " + new_profile_picture}