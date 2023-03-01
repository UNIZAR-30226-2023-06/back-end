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
# a la partida con codigo=codigo_partida
def unirse_a_partida(id_jugador, codigo_partida):
    # Devuelvo la partida si el jugador se ha podido unir a ella con éxito, o
    # None si la partida ya está llena.
    if partidas_en_curso[codigo_partida].anadir_jugador(id_jugador):
        return partidas_en_curso[codigo_partida]
    else:
        return None

# Código para hacer pruebas
nueva_partida(16990141)
