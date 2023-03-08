import multiprocessing
import time

from enum import Enum

import partida

# Diccionario que guarda qué partidas hay en curso actualmente con una relación
# de código (entero) - partida (clase partida).
partidas_en_curso = {

}

################ GESTIÓN DE PARTIDAS (EMPEZARLAS Y TERMINARLAS) ################

# Función a la que se llama cuando el jugador con id=id_jugador crea una nueva
# sala de juego. Devuelve el código de la partida.
def nueva_partida(id_jugador):
    # Creo una nueva instancia de partida y añado el jugador que ha creado la
    # sala.
    partida, codigo_partida = partida.nueva_partida()
    partida.anadir_jugador(id_jugador)

    # Añado la partida al registro de partidas en curso
    partidas_en_curso[codigo_partida] = partida

    # Devuelvo el código de la partida
    return codigo_partida

# Función a la que se llama cuando el jugador con id=id_jugador quiere unirse
# a la partida con código=codigo_partida.
def unirse_a_partida(id_jugador, codigo_partida):
    # Devuelvo la partida si el jugador se ha podido unir a ella con éxito, o
    # None si la partida ya está llena.
    if partidas_en_curso[codigo_partida].anadir_jugador(id_jugador):
        return partidas_en_curso[codigo_partida]
    else:
        return None

# Función a la aque se llama cuando el jugador con id=id_jugador quiere
# abandonar la partida con código=codigo_partida.
def salirse_de_partida(id_jugador, codigo_partida):
    # Solo hacemos algo si el jugador que se va es el único que queda en
    # la partida, haciendo que la partida se quede vacía.
    if partidas_en_curso[codigo_partida].get_num_jugadores_activos() <= 1:

        # Si la partida no se ha empezado aún, se borra y ya está.
        if not partidas_en_curso[codigo_partida].get_num_jugadores_activos():
            del partidas_en_curso[codigo_partida]
        
        # Si la partida sí que está en curso, se espera 10 minutos a que por lo
        # menos un jugador vuelva, si eso no ha ocurrido, se borra la partida y
        # el código de la sala queda libre para otro jugadores.
        else:
            # Lanzo el limpiador en paralelo
            thread = multiprocessing.Pool()
            thread.apply_async(limpiador, [codigo_partida])
    else:
        partidas_en_curso[codigo_partida].restar_jugador(id_jugador)

# El limpiador checkea si una partida en concreto ha sido abandonada y la
# borra si es el caso. Espera 10 minutos antes de hacer el checkeo.
def limpiador(codigo_partida):
    time.sleep(10*60)
    if partidas_en_curso[codigo_partida].get_num_jugadores_activos() <= 0:
        del partidas_en_curso[codigo_partida]

######################## GESTIÓN DE BÚSQUEDA DE PARTIDA ########################

jugadores_buscando_partida = {

}

# Función a la que se llama cuando el jugador con id=id_jugador quiere buscar
# partida.
def buscar_partida(id_jugador):
    # Si el jugador ya está buscando partida, no hacemos nada.
    if id_jugador in jugadores_buscando_partida:
        return

    # Si no, añadimos el jugador a la lista de jugadores buscando partida.
    # TODO: el valor que se le debe asignar a cada jugador es su ELO
    jugadores_buscando_partida[id_jugador] = 1000

# Cada 5 segundos el buscador revisa si hay jugadores buscando partida y si los
# hay, los empareja según su ELO.
def init_buscador():
    # El sentido en el que se van a buscar los jugadores va a alternar entre
    # ascendente y descendente según su ELO.
    class Sentido(Enum):
        ASCENDENTE = 1
        DESCENDENTE = 2
    
    sentido = Sentido.ASCENDENTE

    while(True):
        # Alternamos el sentido de búsqueda en cada iteración.
        if sentido == Sentido.ASCENDENTE:
            sentido = Sentido.DESCENDENTE
        else:
            sentido = Sentido.ASCENDENTE

        # Obtengo todos los jugadores buscando partida y los ordeno de menor a mayor
        # según su ELO.
        jugadores = list(jugadores_buscando_partida.items())
        jugadores.sort(key=lambda x: x[1])

        # Si hay menos de 4 jugadores buscando partida, esperamos 5 segundos y
        # volvemos a comprobar.
        if len(jugadores) < 4:
            time.sleep(5)
            continue

        # Si hay 4 o más jugadores buscando partida, los emparejamos según el
        # sentido de búsqueda que toca.
        if sentido == Sentido.ASCENDENTE:
            # Emparejamos los jugadores de menor a mayor ELO.
            for i in range(0, len(jugadores - (len(jugadores)%4)), 4):
                # Creamos una nueva partida con el primer jugador de la pareja
                # y le añadimos el resto de jugadores.
                codigo_partida = nueva_partida(jugadores[i][0])
                unirse_a_partida(jugadores[i+1][0], codigo_partida)
                unirse_a_partida(jugadores[i+2][0], codigo_partida)
                unirse_a_partida(jugadores[i+3][0], codigo_partida)

                # Eliminamos los jugadores de la lista de jugadores buscando
                # partida.
                del jugadores_buscando_partida[jugadores[i][0]]
                del jugadores_buscando_partida[jugadores[i+1][0]]
                del jugadores_buscando_partida[jugadores[i+2][0]]
                del jugadores_buscando_partida[jugadores[i+3][0]]
        else:
            # Emparejamos los jugadores de mayor a menor ELO.
            for i in range(len(jugadores) - 1, 3, -4):
                # Creamos una nueva partida con el primer jugador de la pareja
                # y le añadimos el resto de jugadores.
                codigo_partida = nueva_partida(jugadores[i][0])
                unirse_a_partida(jugadores[i-1][0], codigo_partida)
                unirse_a_partida(jugadores[i-2][0], codigo_partida)
                unirse_a_partida(jugadores[i-3][0], codigo_partida)

                # Eliminamos los jugadores de la lista de jugadores buscando
                # partida.
                del jugadores_buscando_partida[jugadores[i][0]]
                del jugadores_buscando_partida[jugadores[i-1][0]]
                del jugadores_buscando_partida[jugadores[i-2][0]]
                del jugadores_buscando_partida[jugadores[i-3][0]]
        time.sleep(5)

######################### GESTIÓN DE INICIO DE PARTIDA #########################

# Función a la que se llama cuando el jugador con id=id_jugador quiere empezar
# la partida con código=codigo_partida.
def empezar_partida(id_jugador, codigo_partida):
    # Indico en la partida que el jugador con id "id_jugador" quiere empezar
    # la partida.
    todos_listos = partidas_en_curso[codigo_partida].jugador_listo(id_jugador)

    # Si todos los jugadores están listos, se avisa a todos los jugadores de
    # la partida de que la partida va a empezar.
    if todos_listos:
        for jugador in partidas_en_curso[codigo_partida].get_jugadores():
            # TODO: avisar a los jugadores de que la partida va a empezar
            return True
    
    return False

##################################### MAIN #####################################

init_buscador()
