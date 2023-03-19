import re
import jwt
from db import get_engine_from_settings
from models.user import User
from utils import *

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # https://fastapi.tiangolo.com/tutorial/cors/

from routes.auth import router as auth_router
from routes.friends import router as friends_router
from local_settings import JWT_SECRET
from sqlalchemy.orm import sessionmaker

app = FastAPI()

origins = [
  "*" # reacts'
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


from routes.auth import oauth2_scheme
@app.post("/")
def index(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        #TODO: return something when not authenticated
    else:
        #TODO: return something when authenticated
        #returns the token
        return {"token": token}


from routes.auth import session
#gets a user from the database given the user id
@app.get("/get-user-from-id/{user_id}")
def get_user(user_id: int):
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
      return user
    
#gets a user from the database given the user email
@app.get("/get-user-from-email/{email}")
def get_user_by_email(email: str):
    #if the email is not a valid email, return an error
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
  
    user = session.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
      return user

is_valid_email = lambda email: re.match(r"[^@]+@[^@]+\.[^@]+", email)

app.include_router(auth_router)
app.include_router(friends_router)