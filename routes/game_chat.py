import os, sys

import jwt
import random

from fastapi import APIRouter, Depends, HTTPException
from logica_juego.board import Board, Hexgrid
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
import hexgrid
from hexgrid import *
router = APIRouter()


#route for sending a chat message
@router.post("/send_chat_message", tags=["Chat"])
async def send_chat_message(message: str, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        if session.query(User).filter(User.id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
       
        #search the lobby the user is in
        lob: Lobby = None
        for lobby in Lobbies:
            for player in lobby.game.jugadores:
                if player.id == user_id:
                    lob = lobby
                    break
        if lob is None:
            raise HTTPException(status_code=404, detail="Lobby not found")
        
        #add the message to the chat
        lob.game.send_message(user_id, message)
        return {"detail": "Message sent"}
    
#route for getting all the chat messages
@router.get("/get_chat_messages", tags=["Chat"])
async def get_chat_messages(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the user exists in the database
        if session.query(User).filter(User.id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
       
        #search the lobby the user is in
        lob: Lobby = None
        for lobby in Lobbies:
            for player in lobby.game.jugadores:
                if player.id == user_id:
                    lob = lobby
                    break
        if lob is None:
            raise HTTPException(status_code=404, detail="Lobby not found")
        
        #get the chat messages
        messages = lob.game.get_messages()
        return {"messages": messages}