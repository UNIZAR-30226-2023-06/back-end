import os, sys

import jwt
import random

from fastapi import APIRouter, Depends, HTTPException
from logica_juego.board import Board
from logica_juego.partida import Partida
from models.user import User
from local_settings import  JWT_SECRET

from routes.auth import oauth2_scheme
from routes.auth import session

from models.user import User, Befriends

# Add parent directory to path to be able to import from "logica_juego"
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Color, Cards, TurnPhase
from logica_juego.mano import Mano

from logica_juego.matchmaking import jugadores_buscando_partida, Lobbies, buscar_partida

router = APIRouter()

# Lobbies : Lobby = []

# Create a new lobby
@router.post("/create-lobby", tags=["Lobby"])
async def create_Lobby():
    lobby = Lobby()
    Lobbies.append(lobby)
    return {"lobby_id": lobby.id, "detail": "Lobby created"}

#delete a lobby
@router.delete("/delete-lobby", tags=["Lobby"])
async def delete_Lobby(lobby_id: int):
    for lobby in Lobbies:
        if lobby.id == lobby_id:
            Lobbies.remove(lobby)
            return {"detail": "Lobby deleted"}
    return {"detail": "Lobby not found"}

@router.get("/get-all-lobbies", tags=["Lobby"])
async def get_Lobbies():
    return Lobbies

@router.get("/get-lobby-from-id", tags=["Lobby"])
async def get_Lobby_From_Id(lobby_id: int):
    for lobby in Lobbies:
        if lobby.id == lobby_id:
            return lobby
    return {"detail": "Lobby not found"}

# Join a lobby
@router.post("/join-lobby", tags=["Lobby"])
async def join_Lobby(lobby_id: int, token: str = Depends(oauth2_scheme)):
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
    for l in Lobbies:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                raise HTTPException(status_code=409, detail="User already in lobby")

    # Search for the lobby
    lobby : Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lobby = l
            break
    
    if lobby is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    # Add the user to the lobby
    player = Jugador(user.id, user.elo, 0, Color.BLUE, Mano([0,0,0,0,0,0,0,0,0], 0, 0 ,0 ,0, 0), 0, False, False, False, True)

    # Search whether the user is already in the lobby (some player has the same id)
    players = lobby.get_Players()
    for j in players:
        if j.id == player.id:
            raise HTTPException(status_code=409, detail="User already in lobby")


    response = lobby.add_Player(player)
    if response == -1:
        raise HTTPException(status_code=409, detail="Lobby is full")
    elif response == 0 or response == 1:
        return {"num_players":len(lobby.game.jugadores),  "detail": "Lobby joined"}

# Leave a lobby
@router.post("/leave-lobby", tags=["Lobby"])
async def leave_Lobby(token: str = Depends(oauth2_scheme)):
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
    for l in Lobbies:
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
        return {"num_players":len(lobby.game.jugadores),  "detail": "Lobby left"}

# Search for a lobby
@router.post("/search-lobby", tags=["Lobby"])
async def search_Lobby(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    for l in Lobbies:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                raise HTTPException(status_code=409, detail="User already in lobby")
            
    player = Jugador(user.id, user.elo ,0, None, None, 0, False, False, False, True)
    if buscar_partida(player) == -2:
        raise HTTPException(status_code=409, detail="User already searching for a lobby")

    return {"detail": "Searching for a lobby"}

# Stop searching for a lobby
@router.post("/stop-searching-lobby", tags=["Lobby"], description="Stop searching for a lobby")
async def stop_Searching_Lobby(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #decode the token
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    #get the user id from the token
    user_id = decoded_token['id']
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    from logica_juego.matchmaking import jugadores_buscando_partida

    for j in jugadores_buscando_partida:
        if j.id == user.id:
            jugadores_buscando_partida.remove(j)
            return {"detail": "Stopped searching for a lobby"}
    
    raise HTTPException(status_code=404, detail="User not searching for a lobby")
    
    
# Get the lobby a player is in
@router.get("/get-lobby-from-player", tags=["Lobby"])
async def get_Lobby_From_Player(token: str = Depends(oauth2_scheme)):
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
    for l in Lobbies:
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
        return lobby
    

#start the game
@router.post("/start-game", tags=["Lobby"])
async def start_Game(lobby_id: int):
    lobby : Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lobby = l
        
    if lobby is None:
        raise HTTPException(status_code=404, detail="Lobby not found")

    all_players_ready = True
    for player in lobby.game.jugadores:
        if player.esta_preparado == False:
            all_players_ready = False
            break
    if all_players_ready == False:
        raise HTTPException(status_code=409, detail="Not all players are ready")
    
    #start the game
    lobby.start_Game()

#return the legal building nodes for citys
@router.get("/get-legal-building-nodes", tags=["Game"])
async def get_Legal_Building_Nodes(lobby_id: int, color: str):
    lobby : Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lobby = l
        
    if lobby is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    if lobby.game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    col = None
    if color == "RED":
        col = Color.RED
    elif color == "BLUE":
        col = Color.BLUE
    elif color == "GREEN":
        col = Color.GREEN
    elif color == "YELLOW":
        col = Color.YELLOW
    else:
        raise HTTPException(status_code=400, detail="Invalid color")

    return lobby.game.board.legal_building_nodes(col)

@router.get("/get-legal-building-nodes-non-initial-phases", tags=["Game"])
async def get_Legal_Building_Nodes_Non_Initial_Phases(lobby_id: int, color: str):
    lobby : Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lobby = l
        
    if lobby is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    if lobby.game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    col = None
    if color == "RED":
        col = Color.RED
    elif color == "BLUE":
        col = Color.BLUE
    elif color == "GREEN":
        col = Color.GREEN
    elif color == "YELLOW":
        col = Color.YELLOW
    else:
        raise HTTPException(status_code=400, detail="Invalid color")

    return lobby.game.board.legal_building_nodes_second_phase(col)

#return the legal building edges for roads
@router.get("/get-legal-building-edges", tags=["Game"])
async def get_Legal_Building_Edges(lobby_id: int, color: str):
    lobby : Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lobby = l
        
    if lobby is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    if lobby.game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    col = None
    if color == "RED":
        col = Color.RED
    elif color == "BLUE":
        col = Color.BLUE
    elif color == "GREEN":
        col = Color.GREEN
    elif color == "YELLOW":
        col = Color.YELLOW
    else:
        raise HTTPException(status_code=400, detail="Invalid color")

    return lobby.game.board.legal_building_edges(col)


#set a player as ready
@router.post("/set-player-ready", tags=["Game"])
async def set_Player_Ready(token : str = Depends(oauth2_scheme)):
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
    for l in Lobbies:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                lobby = l
                break
        if lobby is not None:
            break
    if lobby is None:
        raise HTTPException(status_code=404, detail="Player not in any lobby")
    
    
    # Search for the player in the lobby
    player : Jugador = None
    for j in lobby.game.jugadores:
        if j.id == user.id:
            player = j
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not in the lobby")
    
    # Set the player as ready
    lobby.game.jugador_listo(player.id)

    lobby.game.actualizar_initial_turns()

    

    # Check if all players are ready
    all_players_ready = True
    for player in lobby.game.jugadores:
        if player.esta_preparado == False:
            all_players_ready = False
            break
    if all_players_ready == True:
        lobby.start_Game()
        return {"detail": "Player ready and Game started"}

    return {"detail": "Player ready"}

# build a village
@router.post("/build-village", tags=["Game"])
async def build_Village(node: int, token : str = Depends(oauth2_scheme)):
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
    for l in Lobbies:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                lobby = l
                break
        if lobby is not None:
            break
    if lobby is None:
        raise HTTPException(status_code=404, detail="Player not in any lobby")
    
    # Search for the player in the lobby
    player : Jugador = None
    for j in lobby.game.jugadores:
        if j.id == user.id:
            player = j
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not in the lobby")
    if not lobby.game_has_started:
        raise HTTPException(status_code=409, detail="Game has not started yet")
    
    # Build the Village
    if lobby.game.place_town(node_coord=node, id_jugador=player.id):
        if lobby.game.fase_turno == TurnPhase.INITIAL_TURN2:
            print("nodo puesto =====>>>>>", lobby.game.board.nodes[node])
            lobby.game.asignacion_recursos_a_jugador(lobby.game.jugadores[lobby.game.turno].id, node)
    else:
        raise HTTPException(status_code=409, detail="Invalid building position")
        
    return {"detail": "Village built"}

#build a road
@router.post("/build-road", tags=["Game"])
async def build_Road(edge: int, token : str = Depends(oauth2_scheme)):
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
    for l in Lobbies:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                lobby = l
                break
        if lobby is not None:
            break
    if lobby is None:
        raise HTTPException(status_code=404, detail="Player not in any lobby")
    if not lobby.game_has_started:
        raise HTTPException(status_code=409, detail="Game has not started yet")
    
    # Search for the player in the lobby
    player : Jugador = None
    for j in lobby.game.jugadores:
        if j.id == user.id:
            player = j
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not in the lobby")
    
    
    # Build the Road
    if not lobby.game.place_road(edge_coord=edge, id_jugador=player.id):
        raise HTTPException(status_code=409, detail="Invalid building position")
    
    return {"detail": "Road built"}

#upgrade a village to a city
@router.post("/upgrade-village-to-city", tags=["Game"])
async def upgrade_Village(node: int, token : str = Depends(oauth2_scheme)):
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
    for l in Lobbies:
        players = l.get_Players()
        for j in players:
            if j.id == user.id:
                lobby = l
                break
        if lobby is not None:
            break
    if lobby is None:
        raise HTTPException(status_code=404, detail="Player not in any lobby")
    if not lobby.game_has_started:
        raise HTTPException(status_code=409, detail="Game has not started yet")
    
    # Search for the player in the lobby
    player : Jugador = None
    for j in lobby.game.jugadores:
        if j.id == user.id:
            player = j
            break
    if player is None:
        raise HTTPException(status_code=404, detail="Player not in the lobby")
    
    # Upgrade the Village
    if not lobby.game.upgrade_town(node_coord=node, id_jugador=player.id):
        raise HTTPException(status_code=409, detail="Invalid building position")
    return {"detail": "Village upgraded"}

#create a test lobby
@router.post("/create-test-lobby", tags=["Debug"])
async def create_Test_Lobby():


    # Añado los jugadores
    # LobbyTest.add_Player(Jugador(1, 1000, 2, None, None, 0, False, False, True, True))
    # LobbyTest.add_Player(Jugador(2, 1000, 3, None, None, 0, True, False, True, True))
    # LobbyTest.add_Player(Jugador(3, 1000, 5, None, None, 0, False, False, True, True))
    # LobbyTest.add_Player(Jugador(4, 1000, 0, None, None, 0, False, True, True, True))

    # Añado aleatoriamente entre 2 y 4 jugadores
    num_players = 4
    LobbyTest : Lobby = Lobby(num_players)
    LobbyTest.game = Partida(num_players, 0, 0, [], 5, 4, 0, Board(), True)

    for i in range(num_players):

        # Elijo aleatoriamente algunos atributos del jugador
        id = random.randint(1, 1000)
        elo = random.randint(1000, 2000)
        puntos_victoria = random.randint(0, 9)
        caballeros_usados = random.randint(0, 4)
        tiene_bono_carreteras = random.choice([True, False])
        tiene_bono_caballeros = random.choice([True, False])

        # Añado el jugador
        LobbyTest.add_Player(Jugador(id, elo, puntos_victoria, None, None, caballeros_usados, tiene_bono_carreteras, tiene_bono_caballeros, True, True))
    
    #start the game
    LobbyTest.start_Game()
    Lobbies.append(LobbyTest)

    return LobbyTest


#get nodes around tile
@router.get("/get-nodes-around-tile", tags=["Game"])
async def get_Nodes_Around_Tile(lobby_id: int, tileCoord: int):
    lobby : Lobby = None
    for l in Lobbies:
        if l.id == lobby_id:
            lobby = l
        
    if lobby is None:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    if lobby.game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    return {"nodes": lobby.game.board.nodes_around_tile(tileCoord), "detail": "Nodes around tile returned",}