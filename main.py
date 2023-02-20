import jwt

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # https://fastapi.tiangolo.com/tutorial/cors/
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker
from db import get_engine_from_settings, get_session

from schemas.user import UserCreate
from models.user import User

from werkzeug.security import generate_password_hash, check_password_hash

app = FastAPI()

JWT_SECRET = "mysecret"

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
session = get_session()

# TODO : mirar como se hace el login y sesiones con Oauth2
@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = session.query(User).filter_by(email=form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email")
    if not check_password_hash(user.password, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    user_dict = {"id": user.id, "username": user.username, "email": user.email, "password": user.password}

    token = jwt.encode(user_dict, JWT_SECRET)

    return {"access_token": token, "token_type": "bearer"}

@app.post("/")
def index(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        #TODO: return something when not authenticated
    else:
        #returns the token
        return {"token": token}