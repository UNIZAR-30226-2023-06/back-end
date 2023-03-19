import re
import jwt
from db import get_engine_from_settings
from models.user import User
from utils import *

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # https://fastapi.tiangolo.com/tutorial/cors/

from routes.auth import router as auth_router
from routes.friends import router as friends_router
from routes.user_settings import router as user_settings_router
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


app.include_router(auth_router)
app.include_router(friends_router)
app.include_router(user_settings_router)