import datetime
import random
from logica_juego.constants import TurnPhase

from logica_juego.partida import Partida

from .jugador import Color, Jugador
from .board import Board
from .mano import Mano, nueva_mano
from logica_juego.chat import Chat, Message

class Lobby:
    id = None
    game = Partida(4,0,0,[],60,0,0,Board(),True)
    game_has_started = False
    is_full = False
    max_Players = None 
    current_Players = 0
    board_dist = None

    # Partes de configuracion
    hay_ladron = True
    # max_tiempo_turno = 30 # en segundos
    max_tiempo_turno = 5 # en segundos

    def __init__(self, max_Players : int = 4):
        #id = random 4 digit number
        self.id = random.randint(1000, 9999) #TODO: check if id already exists
        self.is_full = False
        self.game_has_started = False
        self.max_Players = max_Players
        self.current_Players = len(self.game.jugadores)
        self.game.jugadores = []
        self.game: Partida = Partida(4, 0, 0, [], 60, 0, 0, Board(), True)
        
        self.hay_ladron = True
        self.max_tiempo_turno = 5
        self.board_dist = None
        self.last_time_modified = datetime.datetime.now()

    def add_Player(self, player : Jugador):
        if len(self.game.jugadores) < self.max_Players:
            self.game.jugadores.append(player)
            #recalculate elo (average of all players in lobby)
            self.elo = sum([player.elo for player in self.game.jugadores]) / len(self.game.jugadores)
            self.current_Players = len(self.game.jugadores)
            if len(self.game.jugadores) == self.max_Players:
                self.is_full = True
                return 1 # Player added successfully and lobby is full now
            return 0 # Player added successfully
        else:
            self.is_full = True
            return -1 # Lobby is full, player not added

    def remove_Player(self, player_id : int):
        for player in self.game.jugadores:
            if player.id == player_id:
                self.game.jugadores.remove(player)
                #recalculate elo (average of all players in lobby)
                try:
                    self.elo = sum([player.elo for player in self.game.jugadores]) / len(self.game.jugadores)
                except ZeroDivisionError:
                    self.elo = 0
                self.current_Players = len(self.game.jugadores)
                return 0
        return -1 # Player not found

    def get_Players(self):
        return self.game.jugadores  

    #it is assumed that the lobby is full and all players are ready
    def start_Game(self):
        color = { Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW }
        #initialize all the player's hands, victory points, etc
        for player in self.game.jugadores:
            player.mano = nueva_mano()
            player.puntos_victoria = 0
            player.color = color.pop()
            player.caballeros_usados = 0
            player.tiene_bono_carreteras = False
            player.tiene_bono_caballeros = False

        #initialize the board
        self.game.board = Board(to_assign=self.board_dist, thief=self.hay_ladron)
        self.game_has_started = True
        self.is_full = True
        self.game.turno = 0
        self.game.fase_turno = TurnPhase.INITIAL_TURN1
        print(self.game.initial_turns)
        
        return 0
