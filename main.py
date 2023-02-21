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

# session = get_session()

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