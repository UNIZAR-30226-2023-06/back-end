import re
import jwt
import multiprocessing
import threading
from sqlalchemy import inspect
from db import get_engine_from_settings
from models.user import User

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # https://fastapi.tiangolo.com/tutorial/cors/

from routes.auth import router as auth_router, engine
from routes.friends import router as friends_router
from routes.game_board import router as game_board_router
from routes.user_settings import router as user_settings_router
from routes.game_lobby import router as game_lobby_router
from routes.game_phases import router as game_phases_router
from routes.debug_functions import router as debug_functions_router
from routes.game_chat import router as game_chat_router
from local_settings import JWT_SECRET
from sqlalchemy.orm import sessionmaker

from logica_juego.matchmaking import init_buscador
from logica_juego.matchmaking import jugadores_buscando_partida
app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_credentials=True,
  allow_origins=["*","http://localhost:3000"],
  allow_methods=["*"],
  allow_headers=["*"],
)

from models.user import Base as UserBase
from models.tablero import Base as BoardBase
from insert_users import poblarTodo

if not inspect(engine).has_table('users') and not inspect(engine).has_table('profile_pictures'):
  print("Database not created, creating...")
  UserBase.metadata.create_all(bind=engine)
  BoardBase.metadata.create_all(bind=engine)
  print("Database created successfully")
  # ask for the user if he wants to insert some users
  opt = input("Do you want to insert some users? (y/n): ")
  if opt == 'y':
    poblarTodo()
    print("Users inserted successfully")
  else:
    print("No users inserted")

app.include_router(auth_router)
app.include_router(game_board_router)
app.include_router(user_settings_router)
app.include_router(friends_router)
app.include_router(game_lobby_router)
app.include_router(game_phases_router)
app.include_router(debug_functions_router)
app.include_router(game_chat_router)

thread = threading.Thread(target=init_buscador)
thread.start()
