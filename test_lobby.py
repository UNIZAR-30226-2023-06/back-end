from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Color, Cards
from logica_juego.mano import Mano


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
    
    #north vertex
    testBoard(0x76, 0x76, 0x87, 1)
    testBoard(0x76, 0x65, 0x65, 2)

    #north-east vertex
    testBoard(0x65, 0x65, 0x76, 3)
    testBoard(0x65, 0x64, 0x74, 4)

    #north-west vertex
    testBoard(0x87, 0x76, 0x76, 5)
    testBoard(0x87, 0x86, 0x96, 6)

    #south vertex
    testBoard(0x85, 0x74, 0x74, 7)
    testBoard(0x85, 0x85, 0x96, 8)

    #south-west vertex
    testBoard(0x74, 0x64, 0x65, 9)
    testBoard(0x74, 0x74, 0x85, 10)

    #south-east vertex
    testBoard(0x96, 0x85, 0x85, 11)
    testBoard(0x96, 0x86, 0x87, 12)
    
    print("Total errors: ", totalErrors)

if __name__ == "__main__":
    main()
