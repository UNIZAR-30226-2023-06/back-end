import multiprocessing
import time

import partida

# Diccionario que guarda qué partidas hay en curso actualmente con una relación
# de código (entero) - partida (clase partida).
partidas_en_curso = {

}

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

# Código para hacer pruebas
nueva_partida(16990141)
