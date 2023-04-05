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
    KNIGHT = auto()
    INVENTION_PROGRESS = auto()
    ROAD_PROGRESS = auto()
    MONOPOLY_PROGRESS = auto()
    TOWN_HALL = auto()
    LIBRARY = auto()
    MARKET = auto()
    CHURCH = auto()
    UNIVERSITY = auto()
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