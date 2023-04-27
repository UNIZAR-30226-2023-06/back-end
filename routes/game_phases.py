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
    
def game_phase_to_str(gamePhase: TurnPhase) -> str:
    if gamePhase == TurnPhase.RESOURCE_PRODUCTION:
        return "RESOURCE_PRODUCTION"
    elif gamePhase == TurnPhase.TRADING:
        return "TRADING"
    elif gamePhase == TurnPhase.BUILDING:
        return "BUILDING"
    else:
        raise Exception("Invalid game phase")

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

#use a knight card
@router.get("/game_phases/use_knight_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de caballero \
            Args: id_stolen_player es el id del jugador al que se le quiere robar \
                  coord es la coordenada de la casilla a la que se quiere mover el ladron \
                  token -> token de autenticacion \
                  lobby_id -> id del lobby en el que se esta jugando")
def use_knight_card(lobby_id: int, stolen_player_id: int, new_thief_position_tile_coord: str, token: str = Depends(oauth2_scheme)): 
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
        lob.game.usar_carta_caballero(user.id, stolen_player_id, new_thief_position_tile_coord)
        return {"detail": "Knight card used successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#use an invention progress card
@router.get("/game_phases/use_invention_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de invencion \
            Args: token -> token de autenticacion \
                  lobby_id -> id del lobby en el que se esta jugando \
                  recurso1 -> primer recurso que se quiere \
                  recurso2 -> segundo recurso que se quiere")
def use_invention_card(lobby_id: int, resource1:str, resource2:str, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        res1 = resource_str_to_Resource(resource1)
        res2 = resource_str_to_Resource(resource2)
        lob.game.usar_carta_invention_progress(user.id, res1, res2)
        return {"detail": "Invention card used successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#use road progress card
@router.get("/game_phases/use_road_progress_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de camino \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenada de casilla en la que construir la carretera")
def use_road_card(lobby_id: int, coord: str, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.usar_carta_road_progress(user.id, coord)
        return {"detail": "Road built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
                    

#use monopoly progress card
@router.get("/game_phases/use_monopoly_progress_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de monopolio \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    resource -> recurso que se quiere")
def use_monopoly_card(lobby_id: int, resource: str, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        res = resource_str_to_Resource(resource)
        lob.game.usar_carta_monopoly_progress(user.id, res)
        return {"detail": "Monopoly card used successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#use victory point progress card
@router.get("/game_phases/use_victory_point_progress_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de punto de victoria \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando")
def use_victory_point_card(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.usar_carta_victory_progress(user.id)
        return {"detail": "Victory point card used successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#buy development card
@router.get("/game_phases/buy_development_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar una carta de desarrollo \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando")
def buy_development_card(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.DEV_CARD, None)
        return {"detail": "Development card bought successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#buy and build road
@router.get("/game_phases/buy_and_build_road", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar y construir una carretera \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenadas de la carretera")
def buy_and_build_road(lobby_id: int, coord: str, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.ROAD, coord)
        return {"detail": "Road bought and built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#buy and build village
@router.get("/game_phases/buy_and_build_village", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar y construir un pueblo \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenadas del pueblo")
def buy_and_build_village(lobby_id: int, coord: str, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.VILLAGE, coord)
        return {"detail": "Village bought and built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#buy and build city
@router.get("/game_phases/buy_and_build_city", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar y construir una ciudad \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenadas de la ciudad")
def buy_and_build_city(lobby_id: int, coord: str, token: str = Depends(oauth2_scheme)):
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
    
    player = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.CITY, coord)
        return {"detail": "City bought and built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
####################################################################################### 

# get a player state
@router.get("/game_phases/get_player_state", tags=["game_phases: get_state"],
            description="Funcion que permite al jugador obtener su estado \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando")
def get_player_state(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
    
    player: Jugador = None
    #check whether the player is in a lobby
    for p in lob.players:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    player_development_cards = {"knight" : player.mano.cartas_desarrollo[Cards.KNIGHT.value],
                                "invention_progress" : player.mano.cartas_desarrollo[Cards.INVENTION_PROGRESS.value],
                                "road_progress" : player.mano.cartas_desarrollo[Cards.ROAD_PROGRESS.value],
                                "monopoly_progress" : player.mano.cartas_desarrollo[Cards.MONOPOLY_PROGRESS.value],
                                "town_hall" : player.mano.cartas_desarrollo[Cards.TOWN_HALL.value],
                                "library" : player.mano.cartas_desarrollo[Cards.LIBRARY.value],
                                "market" : player.mano.cartas_desarrollo[Cards.MARKET.value],
                                "university" : player.mano.cartas_desarrollo[Cards.UNIVERSITY.value],
                                "church" : player.mano.cartas_desarrollo[Cards.CHURCH.value],}

    player_hand = { "wheat" : player.mano.trigo,
                    "wood" : player.mano.madera,
                    "sheep" : player.mano.oveja,
                    "brick" : player.mano.arcilla,
                    "rock" : player.mano.piedra,
                    "dev_cards" : player_development_cards,}

    player_state = {"id" : player.id, 
                    "victory_points" : player.puntos_victoria,
                    "color" : player.color,
                    "used_knights" : player.caballeros_usados,
                    "has_knights_bonus": player.tiene_bono_caballeros,
                    "has_longest_road_bonus": player.tiene_bono_carreteras,
                    "is_ready": player.esta_preparado,
                    "elo" : player.elo,
                    "is_active" : player.activo,
                    "hand" : player_hand,}

    return player_state

#get the state of the game
@router.get("/game_phases/get_game_state", tags=["game_phases: get_state"],
            description="Funcion que permite al jugador obtener el estado del juego \
            Args: lobby_id -> id del lobby en el que se esta jugando")
def get_game_state(lobby_id: int):
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    print(lob.game)

    game_state = {
        "player_0" : {"id" : lob.game.jugadores[0].id, "color" : lob.game.jugadores[0].color, "is_active" : lob.game.jugadores[0].activo},
        "player_1" : {"id" : lob.game.jugadores[1].id, "color" : lob.game.jugadores[1].color, "is_active" : lob.game.jugadores[1].activo},
        "player_2" : {"id" : lob.game.jugadores[2].id, "color" : lob.game.jugadores[2].color, "is_active" : lob.game.jugadores[2].activo},
        "player_3" : {"id" : lob.game.jugadores[3].id, "color" : lob.game.jugadores[3].color, "is_active" : lob.game.jugadores[3].activo},

        "turn_phase" : game_phase_to_str(lob.game.fase_turno),
        "player_turn" : lob.game.turno,
        "turn_time" : lob.game.tiempo_turno,

        "thief_enabled" : lob.game.hay_ladron,
        "board" : lob.game.board
    }

    return game_state
