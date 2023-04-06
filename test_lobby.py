from logica_juego.lobby import Lobby
from logica_juego.jugador import Jugador
from logica_juego.constants import Color, Cards
from logica_juego.mano import Mano

if __name__ == "__main__":
    lobby = Lobby()
    mano = Mano(None, 0, 0, 0, 0, 0)
    player = []
    player.append(Jugador(0, 0, Color.BLUE, mano, 0, False, False, False))
    player.append(Jugador(1, 0, Color.GREEN, mano, 0, False, False, False))
    player.append(Jugador(2, 0, Color.RED, mano, 0, False, False, False))
    player.append(Jugador(3, 0, Color.YELLOW, mano, 0, False, False, False))

    for p in player:
        lobby.add_Player(p)

    for p in lobby.players:
        print(p.id, p.color)

