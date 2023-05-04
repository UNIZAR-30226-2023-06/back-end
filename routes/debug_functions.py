import os, sys

import jwt
import random

from fastapi import APIRouter, Depends, HTTPException
from logica_juego.board import Board
from models.user import User
from local_settings import  JWT_SECRET

from routes.auth import oauth2_scheme
from routes.auth import session

from models.user import User, Befriends

# Add parent directory to path to be able to import from "logica_juego"
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Building, Color, Cards, Resource, TurnPhase
from logica_juego.mano import Mano

from logica_juego.matchmaking import jugadores_buscando_partida, Lobbies, buscar_partida

router = APIRouter()

@router.post("/initial-buildings-true", tags=["Game"])
async def initial_buildings_true(Lobyb_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # TOKEN MANAGING

    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    user_id = decoded_token["id"]
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # OBTAINING LOBBY

    lob: Lobby = None
    for l in Lobbies:
        if l.id == Lobyb_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    # DOING CHANGES

    lob.game.initial_buildings_done = True

    # RETURNING

    return {"detail": "Initial building done"}