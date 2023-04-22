from logica_juego.board import Hexgrid
from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Color, Cards
from logica_juego.mano import Mano
from hexgrid import *
from logica_juego.board import NodeDirection, EdgeDirection


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
    lob.game.board.place_town(Color.BLUE, 0x76)
    lob.game.board.place_road(Color.BLUE, 0x65)
    lob.game.board.place_road(Color.BLUE, 0x64)
    lob.game.board.place_road(Color.BLUE, 0x63)
    lob.game.board.place_road(Color.BLUE, 0x74)
    lob.game.board.place_road(Color.BLUE, 0x84)
    lob.game.board.place_road(Color.BLUE, 0x83)
    lob.game.board.place_road(Color.BLUE, 0x72)

    # adj = lob.game.board.get_adjacent_nodes_by_node_id(0xad)

    # adj = [node for node in adj if node in legal_node_coords()]

    # print("Adjacent nodes to 0xad :", [f"{node:x}" for node in adj])

    # adj_edges = lob.game.board.get_adjacent_edges_by_node_id(0x58)

    # adj_edges = [edge for edge in adj_edges if edge in legal_edge_coords()]

    # print("Adjacent edges to 0x58 :", [f"{edge:x}" for edge in adj_edges])

    # lob.game.board.place_road(Color.BLUE, 0x83)


    legal_building_nodes = lob.game.board.legal_building_nodes(Color.RED)

    print(f"Legal building nodes for {Color.BLUE.name} : {[f'{node:x}' for node in legal_building_nodes]}")

    lob.game.board.svg("test.svg")

    # longest_path = lob.game.board.longest_path(Color.BLUE)
    # print("Longest Path ----> ", longest_path)
    
    # print("Total errors: ", totalErrors)

if __name__ == "__main__":
    main()
