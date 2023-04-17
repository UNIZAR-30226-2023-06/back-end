from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Color, Cards
from logica_juego.mano import Mano



def main():
    lobby = Lobby()
    # mano = Mano(None, 0, 0, 0, 0, 0)
    # player = []
    # player.append(Jugador(0, 0, None, mano, 0, False, False, False, False))
    # player.append(Jugador(1, 0, None, mano, 0, False, False, False, False))
    # player.append(Jugador(2, 0, None, mano, 0, False, False, False, False))
    # player.append(Jugador(3, 0, None, mano, 0, False, False, False, False))

    # for player in lobby.players:
    #     player.esta_preparado = True


    # for p in player:
    #     lobby.add_Player(p)

    lobby.start_Game()

    lobby.game.place_town(Color.BLUE, 0x76)
    lobby.game.upgrade_town(0x76)


    res = lobby.game.place_road(Color.BLUE, 0x65)
    print(res)
    lobby.game.svg("cosa.svg")
    


if __name__ == "__main__":
    main()
