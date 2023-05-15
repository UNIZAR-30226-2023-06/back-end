import datetime
import multiprocessing
import threading
import time
from logica_juego.jugador import Jugador
from logica_juego.lobby import Lobby
from models.user import User

from routes.auth import session

from enum import Enum


# Diccionario que guarda qué partidas hay en curso actualmente con una relación
# de código (entero) - partida (clase partida).
# partidas_en_curso = {}
Lobbies : Lobby = []
################ GESTIÓN DE PARTIDAS (EMPEZARLAS Y TERMINARLAS) ################

# Función a la que se llama cuando el jugador con id=id_jugador crea una nueva
# sala de juego. Devuelve el código de la partida.
def nueva_partida(id_jugador):
    # Creo una nueva instancia de partida y añado el jugador que ha creado la
    # sala.
    # partida, codigo_partida = partida.nueva_partida()
    user = session.query(User).filter(User.id == id_jugador).first()
    if user is None:
        return -1 # User not found
    lobby = Lobby()
    player = Jugador(id_jugador, user.elo, 0, None, None, 0, False, False, False, True)
    res = lobby.add_Player(player)
    if res == -1:
        return -2 # Lobby is full

    # Añado la partida al registro de partidas en curso
    # partidas_en_curso[codigo_partida] = partida
    Lobbies.append(lobby)

    # Devuelvo el código de la partida
    return lobby.id

# Función a la que se llama cuando el jugador con id=id_jugador quiere unirse
# a la partida con código=codigo_partida.
def unirse_a_partida(id_jugador, codigo_partida):
    # Devuelvo la partida si el jugador se ha podido unir a ella con éxito, o
    # None si la partida ya está llena.

    # if partidas_en_curso[codigo_partida].anadir_jugador(id_jugador):
    #     return partidas_en_curso[codigo_partida]
    # else:
    #     return None

    for lobby in Lobbies:
        user = session.query(User).filter(User.id == id_jugador).first()
        if user is None:
            return None
        if lobby.id == codigo_partida:
            if len(lobby.game.jugadores) >= 4:
                return None
            player = Jugador(id_jugador, user.elo, 0, None, None, 0, False, False, False, True)
            lobby.add_Player(player)
            return lobby

# El limpiador checkea si una partida en concreto ha sido abandonada y la
# borra si es el caso. Espera 10 minutos antes de hacer el checkeo.
def limpiador():
    print("Limpiador iniciado")
    lob: Lobby = None
    global Lobbies
    while(True):
        print("lobbies:", Lobbies)
        print("Limpiador checkeando")
        for lobby in Lobbies:
                print
                now = datetime.datetime.now()
                lob = lobby
                print("last ",lob.last_time_modified)
                print("now ",now)
                print("dif ",now - lob.last_time_modified)
                if now - lob.last_time_modified > datetime.timedelta(minutes=10):
                    # si la partida lleva 10 minutos sin modificarse, se borra
                    print("Partida borrada con id: ", lob.id)
                    Lobbies.remove(lob)
        time.sleep(60)

######################## GESTIÓN DE BÚSQUEDA DE PARTIDA ########################

jugadores_buscando_partida : Jugador = []

# Función a la que se llama cuando el jugador con id=id_jugador quiere buscar
# partida.
def buscar_partida(jugador : Jugador):

    user = session.query(User).filter(User.id == jugador.id).first()
    if user is None:
        return -1
    
    # Si el jugador ya está buscando partida, no hacemos nada.
    if jugador in jugadores_buscando_partida:
        return -2

    for jugador_buscando_partida in jugadores_buscando_partida:
        if jugador_buscando_partida.id == jugador.id:
            return -2

    # Si no, añadimos el jugador a la lista de jugadores buscando partida.
    # TODO: el valor que se le debe asignar a cada jugador es su ELO
    jugadores_buscando_partida.append(Jugador(user.id, user.elo, 0, None, None, 0, False, False, False, True))
    print(jugadores_buscando_partida)
    return 0

# Cada 5 segundos el buscador revisa si hay jugadores buscando partida y si los
# hay, los empareja según su ELO.
def init_buscador():
    # El sentido en el que se van a buscar los jugadores va a alternar entre
    # ascendente y descendente según su ELO.

    global jugadores_buscando_partida
    global Lobbies

    class Sentido(Enum):
        ASCENDENTE = 1
        DESCENDENTE = 2
    
    sentido = Sentido.ASCENDENTE

    while(True):
        #print("Estoy vivo\n")
        # Alternamos el sentido de búsqueda en cada iteración.
        if sentido == Sentido.ASCENDENTE:
            sentido = Sentido.DESCENDENTE
        else:
            sentido = Sentido.ASCENDENTE

        # Obtengo todos los jugadores buscando partida y los ordeno de menor a mayor
        # según su ELO.
        #print(jugadores_buscando_partida)
        jugadores = jugadores_buscando_partida
        jugadores.sort(key=lambda x: x.elo)

        # Si hay menos de 4 jugadores buscando partida, esperamos 5 segundos y
        # volvemos a comprobar.
        if len(jugadores) < 4:
            #print("No hay suficientes jugadores buscando partida\n")
            time.sleep(2)
            continue

        # Si hay 4 o más jugadores buscando partida, los emparejamos según el
        # sentido de búsqueda que toca.
        if sentido == Sentido.ASCENDENTE:
            # Emparejamos los jugadores de menor a mayor ELO.
            for i in range(0, (len(jugadores) - (len(jugadores)%4)), 4):
                # Creamos una nueva partida con el primer jugador de la pareja
                # y le añadimos el resto de jugadores.
                codigo_partida = nueva_partida(jugadores[i].id)
                unirse_a_partida(jugadores[i+1].id, codigo_partida)
                unirse_a_partida(jugadores[i+2].id, codigo_partida)
                unirse_a_partida(jugadores[i+3].id, codigo_partida)

                # Eliminamos los jugadores de la lista de jugadores buscando
                # partida.
                jugadores_buscando_partida.remove(jugadores[i+3])
                jugadores_buscando_partida.remove(jugadores[i+2])
                jugadores_buscando_partida.remove(jugadores[i+1])
                jugadores_buscando_partida.remove(jugadores[i])   
        else:
            # Emparejamos los jugadores de mayor a menor ELO.
            for i in range(len(jugadores) - 1, 3, -4):
                # Creamos una nueva partida con el primer jugador de la pareja
                # y le añadimos el resto de jugadores.
                codigo_partida = nueva_partida(jugadores[i][0])
                unirse_a_partida(jugadores[i-1].id, codigo_partida)
                unirse_a_partida(jugadores[i-2].id, codigo_partida)
                unirse_a_partida(jugadores[i-3].id, codigo_partida)

                # Eliminamos los jugadores de la lista de jugadores buscando
                # partida.
                jugadores_buscando_partida.remove(jugadores[i])
                jugadores_buscando_partida.remove(jugadores[i-1])
                jugadores_buscando_partida.remove(jugadores[i-2])
                jugadores_buscando_partida.remove(jugadores[i-3])
            
        time.sleep(2)

######################### GESTIÓN DE INICIO DE PARTIDA #########################

# Función a la que se llama cuando el jugador con id=id_jugador quiere empezar
# la partida con código=codigo_partida.
def empezar_partida(codigo_partida):
    # Indico en la partida que el jugador con id "id_jugador" quiere empezar
    # la partida.
    lobby : Lobby = None
    for l in Lobbies:
        if l.id == codigo_partida:
            lobby = l
    todos_listos = True
    for player in lobby.game.jugadores:
        if player.esta_Preparado == False:
            todos_listos = False
            break

    # Si todos los jugadores están listos, se avisa a todos los jugadores de
    # la partida de que la partida va a empezar.
    if todos_listos:
        for jugador in lobby.game.jugadores:
            # TODO: avisar a los jugadores de que la partida va a empezar
            return True
    
    return False

##################################### MAIN #####################################

# init_buscador()
