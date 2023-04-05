from .jugador import Color, Jugador
from .board import Board
from .mano import Mano

class Lobby:
    players = [] # list of players in the lobby
    game = Board()
    is_Full = False
    max_Players = None 

    def __init__(self, max_Players : int = 4):
        is_Full = False
        self.max_Players = max_Players

    def add_Player(self, player : Jugador):
        if len(self.players) < self.max_Players:
            self.players.append(player)
            if len(self.players) == self.max_Players:
                self.is_Full = True
                return 1 # Player added successfully and lobby is full now
            return 0 # Player added successfully
        else:
            self.is_Full = True
            return -1 # Lobby is full, player not added

    def remove_Player(self, player : Jugador):
        if player in self.players:
            self.players.remove(player)
            return 0 # Player removed successfully
        else:
            return -1 # Player not found

    def getPlayers(self):
        return self.players
    
    def is_Full(self):
        return self.is_Full
