import jwt
from utils import *

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # https://fastapi.tiangolo.com/tutorial/cors/
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import sessionmaker
from db import get_engine_from_settings, get_session

from schemas.user import UserCreate
from models.user import User

from routes.auth import router as auth_router

from werkzeug.security import generate_password_hash, check_password_hash
from local_settings import JWT_SECRET



app = FastAPI()

origins = [
  "https://localhost:3000" # reacts'
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

session = get_session()

# @app.post("/login")
# def login(form_data: OAuth2EmailPasswordRequestForm = Depends()):
#     user = session.query(User).filter_by(email=form_data.email).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect email")
#     if not check_password_hash(user.password, form_data.password):
#         raise HTTPException(status_code=400, detail="Incorrect password")
    
#     user_dict = {"id": user.id, "username": user.username, "email": user.email}

#     token = jwt.encode(user_dict, JWT_SECRET)

#     return {"access_token": token, "token_type": "bearer"}

# from schemas.user import UserCreate
# @app.post("/register")
# def register(user: str = Depends(UserCreate)):
# # def register(token: str = Depends(oauth2_scheme), user: str, email: str, password: str):
#     hashed_password = generate_password_hash(user.password, method='sha256')
#     new_user = User(username=user.name, email=user.email, password=hashed_password)
#     session.add(new_user)
#     session.commit()
#     user_dict = {"id": user.id, "username": user.name, "email": user.email}
#     token = jwt.encode(user_dict, JWT_SECRET)
#     return {"access_token": token, "token_type": "bearer"}

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


app.include_router(auth_router)