import os, sys

import jwt

from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from local_settings import  JWT_SECRET

from routes.auth import oauth2_scheme
from routes.auth import session

from models.user import User, Befriends

# Add parent directory to path to be able to import from "logica_juego"
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Color, Cards
from logica_juego.mano import Mano

router = APIRouter()

Lobbys : Lobby = []

# Create a new lobby
@router.post("/create-lobby", tags=["Lobby"])
def create_Lobby():
    lobby = Lobby()
    Lobbys.append(lobby)
    return {"lobby_id": lobby.id, "detail": "Lobby created"}

#delete a lobby
@router.delete("/delete-lobby", tags=["Lobby"])
def delete_Lobby(lobby_id: int):
    for lobby in Lobbys:
        if lobby.id == lobby_id:
            Lobbys.remove(lobby)
            return {"detail": "Lobby deleted"}
    return {"detail": "Lobby not found"}

@router.get("/get-lobbys", tags=["Lobby"])
def get_Lobbys():
    return Lobbys

# Join a lobby
@router.post("/join-lobby", tags=["Lobby"])
def join_Lobby(lobby_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # check whether the user is alredy in other lobby
    for l in Lobbys:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                raise HTTPException(status_code=409, detail="User already in lobby")

    # Search for the lobby
    lobby : Lobby = None
    for l in Lobbys:
        if l.id == lobby_id:
            lobby = l
            break
    
    if lobby is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    # Add the user to the lobby
    player = Jugador(user.id, 0, None, None, 0, False, False, False)

    # Search whether the user is already in the lobby (some player has the same id)
    players = lobby.get_Players()
    for j in players:
        if j.id == player.id:
            raise HTTPException(status_code=409, detail="User already in lobby")


    response = lobby.add_Player(player)
    if response == -1:
        raise HTTPException(status_code=409, detail="Lobby is full")
    elif response == 0 or response == 1:
        return {"num_players":len(lobby.players),  "detail": "Lobby joined"}

# Leave a lobby
@router.post("/leave-lobby", tags=["Lobby"])
def leave_Lobby(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Search for the lobby
    lobby : Lobby = None
    for l in Lobbys:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                lobby = l
                break
        if lobby is not None:
            break
    if lobby is None:
        raise HTTPException(status_code=404, detail="Player not in any lobby")
    else:
        lobby.remove_Player(user.id)
        return {"num_players":len(lobby.players),  "detail": "Lobby left"}
