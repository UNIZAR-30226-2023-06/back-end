import random

from logica_juego.partida import Partida

from .jugador import Color, Jugador
from .board import Board
from .mano import Mano, nueva_mano

class Lobby:
    id = None
    players = [] # list of players in the lobby
    game = Partida(4,0,0,None,60,0,0,Board(),True)
    game_has_started = False
    is_full = False
    max_Players = None 
    current_Players = 0

    # Partes de configuracion
    hay_ladron = True
    max_tiempo_turno = 30 # en segundos

    def __init__(self, max_Players : int = 4):
        #id = random 4 digit number
        self.id = random.randint(1000, 9999) #TODO: check if id already exists
        self.is_full = False
        self.max_Players = max_Players
        self.current_Players = len(self.players)
        self.players = []
        self.game= Partida(4,0,0,None,60,0,0,Board(),True)
        
        self.hay_ladron = True
        self.max_tiempo_turno = 30

    def add_Player(self, player : Jugador):
        if len(self.players) < self.max_Players:
            self.players.append(player)
            #recalculate elo (average of all players in lobby)
            self.elo = sum([player.elo for player in self.players]) / len(self.players)
            self.current_Players = len(self.players)
            if len(self.players) == self.max_Players:
                self.is_Full = True
                return 1 # Player added successfully and lobby is full now
            return 0 # Player added successfully
        else:
            self.is_Full = True
            return -1 # Lobby is full, player not added

    def remove_Player(self, player_id : int):
        for player in self.players:
            if player.id == player_id:
                self.players.remove(player)
                #recalculate elo (average of all players in lobby)
                self.elo = sum([player.elo for player in self.players]) / len(self.players)
                self.current_Players = len(self.players)
                return 0
        return -1 # Player not found

    def get_Players(self):
        return self.players
    
    def is_Full(self):
        return self.is_full
    

    #it is assumed that the lobby is full and all players are ready
    def start_Game(self):
        color = { Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW }
        #initialize all the player's hands, victory points, etc
        # for player in self.players:
        #     player.mano = nueva_mano()
        #     player.puntos_victoria = 0
        #     player.color = color.pop()
        #     player.caballeros_usados = 0
        #     player.tiene_bono_carreteras = False
        #     player.tiene_bono_caballeros = False

        #initialize the board
        self.game = Board()
        self.game_has_started = True
        self.is_full = True
        
        return 0
