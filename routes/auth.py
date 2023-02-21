import jwt

from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from local_settings import  JWT_SECRET
from utils import OAuth2EmailPasswordRequestForm

from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.security import OAuth2PasswordBearer

from db import get_engine_from_settings
from sqlalchemy.orm import sessionmaker


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

engine = get_engine_from_settings()
Session = sessionmaker(bind=engine)
session = Session()

@router.post("/login", tags=["auth"])
def login(form_data: OAuth2EmailPasswordRequestForm = Depends()):
    user = session.query(User).filter_by(email=form_data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email")
    if not check_password_hash(user.password, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    user_dict = {"id": user.id, "username": user.username, "email": user.email}

    token = jwt.encode(user_dict, JWT_SECRET)

    return {"access_token": token, "token_type": "bearer"}

from schemas.user import UserCreate
@router.post("/register", tags=["auth"])
def register(user: str = Depends(UserCreate)):
# def register(token: str = Depends(oauth2_scheme), user: str, email: str, password: str):
    if session.query(User).filter_by(email=user.email).first() is None:
        hashed_password = generate_password_hash(user.password.get_secret_value(), method='sha256')
        new_user = User(username=user.name, email=user.email, password=hashed_password)
        session.add(new_user)
        session.commit()
        user_dict = {"id": new_user.id, "username": user.name, "email": user.email}
        token = jwt.encode(user_dict, JWT_SECRET)
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Email already exists")