import re
import jwt

from werkzeug.security import generate_password_hash
from fastapi import APIRouter, Depends, HTTPException
from models.user import User
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
    
        
