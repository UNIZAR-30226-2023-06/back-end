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

last_die1: int = 0
last_die2: int = 0

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
    
def color_to_string(color: Color) -> str:
    if color == Color.BLUE:
        return "BLUE"
    elif color == Color.RED:
        return "RED"
    elif color == Color.GREEN:
        return "GREEN"
    elif color == Color.YELLOW:
        return "YELLOW"
    else:
        raise Exception("Invalid color")
    
def game_phase_to_str(gamePhase: TurnPhase) -> str:
    if gamePhase == TurnPhase.RESOURCE_PRODUCTION:
        return "RESOURCE_PRODUCTION"
    elif gamePhase == TurnPhase.TRADING:
        return "TRADING"
    elif gamePhase == TurnPhase.BUILDING:
        return "BUILDING"
    elif gamePhase == TurnPhase.INITIAL_TURN1:
        return "INITIAL_TURN1"
    elif gamePhase == TurnPhase.INITIAL_TURN2:
        return "INITIAL_TURN2"
    else:
        raise Exception("Invalid game phase")
    
def get_player_as_json(player: Jugador, user: User, lobby: Lobby):
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
                    "clay" : player.mano.arcilla,
                    "rock" : player.mano.piedra,
                    "dev_cards" : player_development_cards,}

    villages = [coord for coord, (c, b) in lobby.game.board.nodes.items() if b == Building.VILLAGE and c == player.color]
    cities = [coord for coord, (c, b) in lobby.game.board.nodes.items() if b == Building.CITY and c == player.color]
    roads = [coord for coord, c in lobby.game.board.edges.items() if c == player.color]

    player_state = {"id" : player.id,
                    "profile_pic" : user.profile_picture,
                    "name" : user.username,
                    "selected_pieces_skin" : user.selected_pieces_skin,
                    "selected_grid_skin" : user.selected_grid_skin,
                    "victory_points" : player.puntos_victoria,
                    "color" : color_to_string(player.color),
                    "used_knights" : player.caballeros_usados,
                    "has_knights_bonus": player.tiene_bono_caballeros,
                    "has_longest_road_bonus": player.tiene_bono_carreteras,
                    "is_ready": player.esta_preparado,
                    "elo" : player.elo,
                    "is_active" : player.activo,
                    "num_villages" : len(villages),
                    "num_cities" : len(cities),
                    "num_roads" : len(roads),
                    "hand" : player_hand,}
    return player_state


@router.get("/game_phases/advance_phase", tags=["game_phases"])
async def advance_phase(lobby_id: int, token: str = Depends(oauth2_scheme)):
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

    current_phase: TurnPhase = lob.game.fase_turno
    output = game_phase_to_str(current_phase)
    

    return {"current_phase": output, "detail": "Phase advanced successfully", "turn": lob.game.jugadores[lob.game.turno].id}
    

################################# RESOURCE PRODUCTION #################################

@router.get("/game_phases/resource_production", tags=["game_phases: resource_production"],
             description="Funcion que tira dados y actualiza los recursos de los jugadores")
async def resource_production(lobby_id: int):
    global last_die1, last_die2
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    try:
        die1, die2 = lob.game.asignacion_recursos()
        last_die1 = die1
        last_die2 = die2
        return {"die1": die1, "die2": die2}
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))

#move the robber
@router.get("/game_phases/move_thief", tags=["game_phases: resource_production"],
            description="Funcion que mueve el ladrón si ha salido un 7 en resource_production \
            y roba un recurso a un jugador ( new_thief_position_tile_coord es la coordenada \
            del hexágono, NO el ID del hexágono )")
async def move_thief(lobby_id: int, stolen_player_id: int, new_thief_position_tile_coord: int, token: str = Depends(oauth2_scheme)):
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
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))
    

    #steal half of the resources of a player
@router.get("/game_phases/steal_half_of_player_resources", tags=["game_phases: resource_production"],
            description="Funcion que roba la mitad de los recursos de un jugador")
async def steal_resources(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
        player_resources = lob.game.jugadores[lob.game.turno].mano.num_total_recursos()
        player_num_resources = sum(player_resources)

        stolen_resources = [0,0,0,0,0]
        for i in range(player_num_resources//2):
            aux = lob.game.jugadores[lob.game.i_jugador(user_id)].robar_recurso()
            for j in range(len(aux)):
                stolen_resources[j] += aux[j]
        return {"stolen_clay": stolen_resources[0],
                "stolen_wood": stolen_resources[1],
                "stolen_sheep": stolen_resources[2],
                "stolen_stone": stolen_resources[3],
                "stolen_wheat": stolen_resources[4],
                "detail": "Resources stolen successfully"}

    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))
####################################################################################### 




####################################### TRADING #######################################

#propose trade to another player
@router.post("/game_phases/propose_trade", tags=["game_phases: trading"])
async def propose_trade(lobby_id: int, player2_id: int, wood_amount_p1: int, clay_amount_p1: int, 
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
    
    resource1 = [clay_amount_p1, wood_amount_p1, sheep_amount_p1, stone_amount_p1, wheat_amount_p1]
    resource2 = [clay_amount_p2, wood_amount_p2, sheep_amount_p2, stone_amount_p2, wheat_amount_p2]

    lob.game.propose_trade(user_id, player2.id, resource1, resource2)

    return {"detail": "trade proposed successfully"}

#accept trade
@router.get("/game_phases/accept_trade", tags=["game_phases: trading"])
async def accept_trade(lobby_id: int, player2_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id: int = decoded_token['id']
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

    if lob.game.accept_trade(user_id, player2_id):
        return {"detail": "trade accepted successfully"}
    else:
        raise HTTPException(status_code=403, detail="Trade not found")
    
#reject trade
@router.get("/game_phases/reject_trade", tags=["game_phases: trading"])
async def reject_trade(lobby_id: int, player2_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id: int = decoded_token['id']
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

    if lob.game.reject_trade(user_id, player2_id):
        return {"detail": "trade rejected successfully"}
    else:
        raise HTTPException(status_code=403, detail="Trade not found")


@router.get("/game_phases/trade_with_player", tags=["Debug"],
            description="Funcion que permite al jugador hacer un intercambio con otro jugador \n \
                ( player2_id es el ID del jugador con el que se quiere hacer el intercambio )\n \
                los parametros wood_amount_p1, clay_amount_p1, sheep_amount_p1, wheat_amount_p1, stone_amount_p1 \
                son los recursos que el jugador 1 quiere dar al jugador 2\n \
                los parametros wood_amount_p2, clay_amount_p2, sheep_amount_p2, wheat_amount_p2, stone_amount_p2 \
                son los recursos que el jugador 2 quiere dar al jugador 1")
async def trade_with_player(lobby_id: int, player2_id: int, wood_amount_p1: int, clay_amount_p1: int, 
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
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))

# trade with bank
@router.get("/game_phases/trade_with_bank", tags=["game_phases: trading"],
            description="Funcion que permite al jugador hacer un intercambio con el banco \
                (resource_type es el tipo de recurso que se quiere, amount es la cantidad de \
                recursos que se quiere, requested_type es el tipo de recurso que se quiere \
                a cambio) [el tipo de recurso es: 'WOOD', 'CLAY', 'SHEEP', 'STONE', 'WHEAT']")
async def trade_with_bank(lobby_id: int, resource_type: str, amount: int, requested_type: str, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    print("TOKEN: ", token)
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    print("DECODED TOKEN: ", decoded_token)
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
        print("RESOURCE: ", resource)
        resource_requested = resource_str_to_Resource(requested_type)
        print("RESOURCE REQUESTED: ", resource_requested)
        lob.game.intercambiar_banca(user.id, resource, amount, resource_requested)
        print("TRADE WITH BANK SUCCESSFUL")
        return {"message": "Trade with bank successful"}
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))    

####################################################################################### 





####################################### BUILDING ######################################

#use a knight card
@router.get("/game_phases/use_knight_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de caballero \
            Args: id_stolen_player es el id del jugador al que se le quiere robar \
                  coord es la coordenada de la casilla a la que se quiere mover el ladron \
                  token -> token de autenticacion \
                  lobby_id -> id del lobby en el que se esta jugando")
async def use_knight_card(lobby_id: int, stolen_player_id: int, new_thief_position_tile_coord: int, token: str = Depends(oauth2_scheme)): 
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
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))
    
@router.get("/game_phases/substract_knight_card", tags=["game_phases: building"])
async def substract_knight_card(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
        lob.game.jugadores[lob.game.turno].sub_carta_desarrollo(Cards.KNIGHT)
        lob.game.jugadores[lob.game.turno].caballeros_usados += 1
        lob.game.check_bono_caballeros(lob.game.jugadores[lob.game.turno])
        return {"detail": "Knight card substracted successfully"}
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))

#use an invention progress card
@router.get("/game_phases/use_invention_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de invencion \
            Args: token -> token de autenticacion \
                  lobby_id -> id del lobby en el que se esta jugando \
                  recurso1 -> primer recurso que se quiere \
                  recurso2 -> segundo recurso que se quiere")
async def use_invention_card(lobby_id: int, resource1:str, resource2:str, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
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
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))

#substract road progress card
@router.get("/game_phases/substract_road_progress_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de camino \
            Args: token -> token de autenticacion \
                  lobby_id -> id del lobby en el que se esta jugando \
                    DESPUÉS DE ESTA FUNCIÓN ES TRABAJO DEL FRONT END CONSTRUIR LA CARRETERA CON \
                    LA FUNCIÓN DE BUILD ROAD, NO BUY AND BUILD ROAD!")
async def substract_road_card(lobby_id: int, coord: int, token: str = Depends(oauth2_scheme)):
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
        lob.game.jugadores[lob.game.turno].sub_carta_desarrollo(Cards.ROAD_PROGRESS)
        return {"detail": "Road built successfully"}
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))

#use road progress card
@router.get("/game_phases/use_road_progress_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de camino \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenada de casilla en la que construir la carretera")
async def use_road_card(lobby_id: int, coord: int, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.usar_carta_road_progress(user.id, coord)
        return {"detail": "Road built successfully"}
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))
                    

#use monopoly progress card
@router.get("/game_phases/use_monopoly_progress_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de monopolio \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    resource -> recurso que se quiere")
async def use_monopoly_card(lobby_id: int, resource: str, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
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
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))
    
#use victory point progress card
@router.get("/game_phases/use_victory_point_progress_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador usar una carta de punto de victoria \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando")
async def use_victory_point_card(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.usar_carta_victory_progress(user.id)
        return {"detail": "Victory point card used successfully"}
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=403, detail=str(e))
    
#buy development card
@router.get("/game_phases/buy_development_card", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar una carta de desarrollo \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando")
async def buy_development_card(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.DEV_CARD, None)
        return {"detail": "Development card bought successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail=str(e))

#buy and build road
@router.get("/game_phases/buy_and_build_road", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar y construir una carretera \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenadas de la carretera")
async def buy_and_build_road(lobby_id: int, coord: int, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.ROAD, coord)
        return {"detail": "Road bought and built successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail=str(e))
    
#buy and build village
@router.get("/game_phases/buy_and_build_village", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar y construir un pueblo \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenadas del pueblo")
async def buy_and_build_village(lobby_id: int, coord: int, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.VILLAGE, coord)
        return {"detail": "Village bought and built successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail=str(e))
    
#buy and build city
@router.get("/game_phases/buy_and_build_city", tags=["game_phases: building"],
            description="Funcion que permite al jugador comprar y construir una ciudad \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando \
                    coord -> coordenadas de la ciudad")
async def buy_and_build_city(lobby_id: int, coord: int, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        lob.game.comprar_y_construir(user.id, Building.CITY, coord)
        return {"detail": "City bought and built successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail=str(e))
    
####################################################################################### 

# get a player state
@router.get("/game_phases/get_player_state", tags=["game_phases"],
            description="Funcion que permite al jugador obtener su estado \
            Args: token -> token de autenticacion \
                    lobby_id -> id del lobby en el que se esta jugando")
async def get_player_state(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
    for p in lob.game.jugadores:
        if p.id == user.id:
            player = p
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return get_player_as_json(player, user, lob)

#get the state of the game
@router.get("/game_phases/get_game_state", tags=["game_phases"],
            description="Funcion que permite al jugador obtener el estado del juego \
            Args: lobby_id -> id del lobby en el que se esta jugando")
async def get_game_state(lobby_id: int):
    global last_die1, last_die2
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    print(lob.game)

    user0 = session.query(User).filter(User.id == lob.game.jugadores[0].id).first() if lob.game.jugadores[0] is not None else None
    user1 = session.query(User).filter(User.id == lob.game.jugadores[1].id).first() if lob.game.jugadores[1] is not None else None
    user2 = session.query(User).filter(User.id == lob.game.jugadores[2].id).first() if lob.game.jugadores[2] is not None else None
    user3 = session.query(User).filter(User.id == lob.game.jugadores[3].id).first() if lob.game.jugadores[3] is not None else None


    player0 = get_player_as_json(lob.game.jugadores[0], user0, lob) if lob.game.jugadores[0] is not None else None
    player1 = get_player_as_json(lob.game.jugadores[1], user1, lob) if lob.game.jugadores[1] is not None else None
    player2 = get_player_as_json(lob.game.jugadores[2], user2, lob) if lob.game.jugadores[2] is not None else None
    player3 = get_player_as_json(lob.game.jugadores[3], user3, lob) if lob.game.jugadores[3] is not None else None

    game_state = {
        "player_0" : player0,
        "player_1" : player1,
        "player_2" : player2,
        "player_3" : player3,

        "chat" : lob.game.get_messages(),
        "trade_requests" : lob.game.get_trades(),

        "die_1" : last_die1,
        "die_2" : last_die2,

        "turn_phase" : game_phase_to_str(lob.game.fase_turno),
        "player_turn" : lob.game.jugadores[lob.game.turno].id,
        "player_turn_name": session.query(User).filter(User.id == lob.game.jugadores[lob.game.turno].id).first().username,
        "turn_time" : lob.game.tiempo_turno,

        "thief_enabled" : lob.game.hay_ladron,
        "thief_position" : lob.game.board.thief_coord,
        "board" : lob.game.board,
    }

    return game_state

# get the last die roll
@router.get("/game_phases/get_last_die_roll", tags=["game_phases"],
            description="Funcion que permite conocer el ultimo resultado de los dados \
            Args: lobby_id -> id del lobby en el que se esta jugando")
async def get_last_die_roll(lobby_id: int):
    global last_die1, last_die2
    lob: Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    return {"die_1" : last_die1, "die_2" : last_die2}


#######################################################################################

####################################### GAME RULES #########################################
#route for enabling the thief
@router.post("/enable-thief", tags=["Lobby"])
async def enable_thief(Lobyb_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token["id"]
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    lob: Lobby = None
    for l in Lobbies:
        if l.id == Lobyb_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lob.game.hay_ladron = True
    return {"detail": "Thief enabled"}

#route for disabling the thief
@router.post("/disable-thief", tags=["Lobby"])
async def disable_thief(Lobyb_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token["id"]
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    lob: Lobby = None
    for l in Lobbies:
        if l.id == Lobyb_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lob.game.hay_ladron = False
    return {"detail": "Thief disabled"}


#set the necessary points to win
@router.post("/set-points-to-win", tags=["Lobby"])
async def set_points_to_win(Lobyb_id: int, points: int):
    lob: Lobby = None
    for l in Lobbies:
        if l.id == Lobyb_id:
            lob = l
            break
    if lob is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    if lob.game_has_started:
        raise HTTPException(status_code=403, detail="Game has already started")
    
    lob.game.puntos_victoria_ganar = points

    return {"detail": "Points to win set successfully"}

#######################################################################################





#!###################################### DEBUG #########################################

#add resources to a player
@router.post("/add-resources", tags=["Debug"])
async def add_resources(player_id: int, wood: int, clay: int, sheep: int, stone: int, wheat: int):
    user = session.query(User).filter(User.id == player_id).first()
    #search the player in the lobbies
    resources = [clay, wood, sheep, stone, wheat]
    for l in Lobbies:
        for p in l.game.jugadores:
            if p.id == player_id:
                l.game.jugadores[l.game.turno].sumar_recursos(resources)
                return {"detail": "Resources added successfully"}
    return {"detail": "Player not found"}

#adds 99 resources of each to every player
@router.post("/add-resources-to-all", tags=["Debug"])
async def add_resources_to_all(lobby_id: int):
    lob : Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lob = l
            break
    if lob is None:
        return {"detail": "Lobby not found"}
    
    for p in lob.game.jugadores:
        p.sumar_recursos([99,99,99,99,99])
    return {"detail": "Resources added successfully"}