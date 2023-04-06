import random

from .jugador import Color, Jugador
from .board import Board
from .mano import Mano

class Lobby:
    id = None
    players = [] # list of players in the lobby
    game = Board()
    is_full = False
    max_Players = None 
    current_Players = 0

    def __init__(self, max_Players : int = 4):
        #id = random 4 digit number
        self.id = random.randint(1000, 9999)
        self.is_full = False
        self.max_Players = max_Players
        self.current_Players = len(self.players)

    def add_Player(self, player : Jugador):
        if len(self.players) < self.max_Players:
            self.players.append(player)
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
                self.current_Players = len(self.players)
                return 0
        return -1 # Player not found

    def get_Players(self):
        return self.players
    
    def is_Full(self):
        return self.is_full
