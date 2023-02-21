from utils import *

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # https://fastapi.tiangolo.com/tutorial/cors/

from routes.auth import router as auth_router

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