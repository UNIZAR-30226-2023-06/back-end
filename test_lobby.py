
from logica_juego.board import Board, Hexgrid
from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Color, Cards, Resource, Building
from logica_juego.mano import Mano
from hexgrid import *
from logica_juego.board import NodeDirection, EdgeDirection
from logica_juego.mano import nueva_mano


totalErrors = 0

def testBoard(townCoord, roadCoord, expectedResult, i):
    global totalErrors
    lobby = Lobby()
    lobby.game.board.place_town(Color.BLUE, townCoord)
    lobby.game.board.place_road(Color.BLUE, roadCoord)
    res = lobby.game.board.longest_path(Color.BLUE)
    if res == expectedResult:
        pass
        # print("*************** TEST ", i,  " OK***************")

        # print("**********************************")
    else:
        print("*************** TEST ", i, " FAIL ***************")
        print("Expected", f"{expectedResult:x}")
        print("Got", f"{res:x}")
        print("***********************************")
        totalErrors += 1



def main():
    
    test_params = {(0x76, 0x76, 0x87, 1),
                   (0x76, 0x65, 0x65, 2),
                   (0x65, 0x65, 0x76, 3),
                   (0x65, 0x64, 0x74, 4),
                   (0x87, 0x76, 0x76, 5), #!
                   (0x87, 0x86, 0x96, 6),
                   (0x85, 0x74, 0x74, 7), #!
                   (0x85, 0x85, 0x96, 8),
                   (0x74, 0x64, 0x65, 9), #!
                   (0x74, 0x74, 0x85, 10), 
                   (0x96, 0x85, 0x85, 11),
                   (0x96, 0x86, 0x87, 12)
                   } #!
    
    #sort test_params by the fourth element of each tuple
    test_params = sorted(test_params, key=lambda x: x[3])

    # for params in test_params:
    #     testBoard(params[0], params[1], params[2], params[3])


    lob = Lobby()
    DEFAULT_RES_DISTRIB = (
    [Resource.DESERT, ] + [Resource.WOOD, ] * 4 + [Resource.WHEAT, ] * 4 +
    [Resource.SHEEP, ] * 4 + [Resource.STONE, ] * 3 + [Resource.CLAY, ] * 3
    )

    CENTER_DESERT_DISTRIB = ( [Resource.CLAY, ]  + 
                             [Resource.WOOD, ] + [Resource.WOOD, ] + [Resource.WOOD, ] + [Resource.WOOD, ] +
                             [Resource.WHEAT, ] + [Resource.WHEAT, ]+ [Resource.WHEAT, ]+ [Resource.WHEAT, ]+
                             [Resource.SHEEP, ] + [Resource.SHEEP, ] + [Resource.SHEEP, ] + [Resource.SHEEP, ] + 
                             [Resource.STONE, ] + [Resource.STONE, ] + [Resource.STONE, ]  + 
                             [Resource.DESERT, ] + [Resource.CLAY, ] + [Resource.CLAY, ])

    lob.game.board = Board(to_assign=CENTER_DESERT_DISTRIB, thief=True)

    lob.game.board.set_node_building_by_coord(0x76, Building.CITY)
    lob.game.board.set_node_color_by_coord(0x76, Color.BLUE)
    lob.game.board.set_node_building_by_coord(0x65, Building.CITY)
    lob.game.board.set_node_color_by_coord(0x65, Color.BLUE)

    lob.game.board.set_edge_by_coord(Color.BLUE, 0x65)
    lob.game.board.set_edge_by_coord(Color.BLUE, 0x76)
    lob.game.board.set_edge_by_coord(Color.BLUE, 0x64)

    lob.game.board.svg("test.svg")

    longest_path = lob.game.board.longest_path(Color.BLUE)
    print("Longest Path ----> ", longest_path)
    
    # print("Total errors: ", totalErrors)

if __name__ == "__main__":
    lob = Lobby()
    # lob.game.board.set_node_building_by_coord(0x52, Building.VILLAGE)
    # lob.game.board.set_node_color_by_coord(0x52, Color.RED)
    aaa = lob.game.board.place_townV2(color=Color.RED, position=0x52)
    lob.game.board.place_townV2(color=Color.BLUE, position=0x54)
    print("aaa ",aaa)
    lob.game.board.place_road(color=Color.RED, position=0x52)


    player1 = Jugador(2880, 500, 0, Color.RED, nueva_mano(), 0, False, False, True, True)
    player2 = Jugador(7365, 500, 0, Color.BLUE, nueva_mano(), 0, False, False, True, True)
    player3 = Jugador(7771, 500, 0, Color.GREEN, nueva_mano(), 0, False, False, True, True)
    player4 = Jugador(7543, 500, 0, Color.YELLOW, nueva_mano(), 0, False, False, True, True)

    lob.game.jugadores.append(player1)
    lob.game.jugadores.append(player2)
    lob.game.jugadores.append(player3)
    lob.game.jugadores.append(player4)

    print("NODES AROUND TILE", lob.game.board.nodes_around_tile(0x53))

    lob.game.board.svg("diavoliko.svg")
