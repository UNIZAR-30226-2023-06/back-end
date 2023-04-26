from enum import Enum, auto

class Color(Enum): # Antes estaba en board.py
    RED = auto()
    BLUE = auto()
    YELLOW = auto()
    GREEN = auto()

class Building(Enum): # Antes estaba en board.py
    VILLAGE = auto()
    CITY = auto()
    ROAD = auto()
    DEV_CARD = auto() # Development card

class Resource(Enum): # Antes estaba en board.py
    WOOD = auto()
    CLAY = auto()
    SHEEP = auto()
    STONE = auto()
    WHEAT = auto()
    DESERT = auto()

class Errors(Enum): # Antes estaba en errores.py
    NO_ERROR = auto()
    GAME_STARTED = auto()
    GAME_FULL = auto()

class Cards(Enum): # Antes estaba en cartas.py
    KNIGHT = 0
    INVENTION_PROGRESS = 1
    ROAD_PROGRESS = 2
    MONOPOLY_PROGRESS = 3

    TOWN_HALL = 4
    LIBRARY = 5
    MARKET = 6
    CHURCH = 7
    UNIVERSITY = 8
    
    TOTAL_CARDS = {
        KNIGHT, KNIGHT, KNIGHT, KNIGHT, KNIGHT, KNIGHT, KNIGHT, 
        KNIGHT, KNIGHT, KNIGHT, KNIGHT, KNIGHT, KNIGHT, KNIGHT,

        ROAD_PROGRESS, ROAD_PROGRESS,

        INVENTION_PROGRESS, INVENTION_PROGRESS,

        MONOPOLY_PROGRESS, MONOPOLY_PROGRESS,

        TOWN_HALL, LIBRARY, MARKET, CHURCH, UNIVERSITY
    }

    def pick_random_card():
        import random
        return random.choice(list(Cards.TOTAL_CARDS))
    
class TurnPhase(Enum):
    RESOURCE_PRODUCTION = 0 # Roll 2 dice, if dice sum is 7 move thief and steal resources from a player and if a player has >=7 cards discard half -- else give resources to players
    TRADING = 1 # Player can trade with other players or with the bank
    BUILDING = 2 # Player can build a village, city, road or development card
