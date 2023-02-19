from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # https://fastapi.tiangolo.com/tutorial/cors/
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker
from db import get_engine_from_settings, get_session

from schemas.user import UserCreate
from models.user import User

from werkzeug.security import generate_password_hash, check_password_hash

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
session = get_session()

# TODO : mirar como se hace el login y sesiones con Oauth2
@app.post("/token")
async def login(user_email : str, password : str):
    user_dict = session.query(User).filter_by(email=user_email).first()
    return user_dict
    # if not user_dict:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    # user = UserInDB(**user_dict)
    # hashed_password = generate_password_hash(form_data.password, "sha256")
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    # return {"access_token": user.username, "token_type": "bearer"}


