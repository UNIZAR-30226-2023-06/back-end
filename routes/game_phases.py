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
from logica_juego.constants import Color, Cards, Resource, TurnPhase
from logica_juego.mano import Mano

from logica_juego.matchmaking import jugadores_buscando_partida, Lobbies, buscar_partida

router = APIRouter()

def resource_str_to_Resource(res: str) -> Resource:
    if res == "WOOD":
        return Resource.WOOD
    elif res == "CLAY":
        return Resource.CLAY
    elif res == "SHEEP":
        return Resource.SHEEP
    elif res == "WHEAT":
        return Resource.WHEAT
    elif res == "STONE":
        return Resource.STONE
    else:
        raise Exception("Invalid resource")

@router.get("/game_phases/advance_phase", tags=["game_phases"])
def advance_phase(lobby_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    lob.game.avanzar_fase()

    current_phase: TurnPhase = lob.game.fase_actual
    output = ""
    if current_phase == TurnPhase.RESOURCE_PRODUCTION:
        output = "RESOURCE PRODUCTION"
    elif current_phase == TurnPhase.TRADING:
        output = "TRADING"
    elif current_phase == TurnPhase.BUILDING:
        output = "BUILDING"

    return {"current_phase": output, "detail": "Phase advanced successfully"}
    

################################# RESOURCE PRODUCTION #################################

@router.get("/game_phases/resource_production", tags=["game_phases: resource_production"],
             description="Funcion que tira dados y actualiza los recursos de los jugadores")
def resource_production(lobby_id: int):
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    try:
        die1, die2 = lob.game.asignacion_recursos()
        return {"die1": die1, "die2": die2}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#move the robber
@router.get("/game_phases/move_thief", tags=["game_phases: resource_production"],
            description="Funcion que mueve el ladrón si ha salido un 7 en resource_production \
            y roba un recurso a un jugador ( new_thief_position_tile_coord es la coordenada \
            del hexágono, NO el ID del hexágono )")
def move_thief(lobby_id: int, stolen_player_id: int, new_thief_position_tile_coord: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    try:
        lob.game.mover_ladron(new_thief_position_tile_coord, user.id, stolen_player_id)
        return {"message": "Thief moved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
####################################################################################### 




####################################### TRADING #######################################
@router.get("/game_phases/trade_with_player", tags=["game_phases: trading"],
            description="Funcion que permite al jugador hacer un intercambio con otro jugador \n \
                ( player2_id es el ID del jugador con el que se quiere hacer el intercambio )\n \
                los parametros wood_amount_p1, clay_amount_p1, sheep_amount_p1, wheat_amount_p1, stone_amount_p1 \
                son los recursos que el jugador 1 quiere dar al jugador 2\n \
                los parametros wood_amount_p2, clay_amount_p2, sheep_amount_p2, wheat_amount_p2, stone_amount_p2 \
                son los recursos que el jugador 2 quiere dar al jugador 1")
def trade_with_player(lobby_id: int, player2_id: int, wood_amount_p1: int, clay_amount_p1: int, 
                      sheep_amount_p1: int, wheat_amount_p1: int, stone_amount_p1: int,
                      wood_amount_p2: int, clay_amount_p2: int, sheep_amount_p2: int,
                      wheat_amount_p2: int, stone_amount_p2: int,
                      token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    player2 : Jugador = None
    for j in lob.game.jugadores:
        if j.id == player2_id:
            player2 = j
            break
    if player2 is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    try:
        #recursos_1 = {0,0,0,0,0}
        #recursos_1 = {CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
        
        recursos_p1 = [clay_amount_p1, wood_amount_p1, sheep_amount_p1, stone_amount_p1, wheat_amount_p1]
        recursos_p2 = [clay_amount_p2, wood_amount_p2, sheep_amount_p2, stone_amount_p2, wheat_amount_p2]
        lob.game.intercambiar_recursos(user.id, recursos_p1, player2_id, recursos_p2)
        return {"message": "Trade with player successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# trade with bank
@router.get("/game_phases/trade_with_bank", tags=["game_phases: trading"],
            description="Funcion que permite al jugador hacer un intercambio con el banco \
                (resource_type es el tipo de recurso que se quiere, amount es la cantidad de \
                recursos que se quiere, requested_type es el tipo de recurso que se quiere \
                a cambio) [el tipo de recurso es: 'WOOD', 'CLAY', 'SHEEP', 'STONE', 'WHEAT']")
def trade_with_bank(lobby_id: int, resource_type: str, amount: int, requested_type: str, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    try:
        resource = resource_str_to_Resource(resource_type)
        resource_requested = resource_str_to_Resource(requested_type)
        lob.game.intercambiar_banca(user.id, resource, amount, resource_requested)
        return {"message": "Trade with bank successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

####################################################################################### 


####################################### BUILDING ######################################

####################################################################################### 
