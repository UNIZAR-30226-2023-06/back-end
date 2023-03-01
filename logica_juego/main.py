import partida
import configuracion
import jugador

# Inicializo la configuración de la partida los valores de la configuración los
# obtengo de la interfaz
configuracion = configuracion.nueva_configuracion(4, True, 30)

# Inicializo los jugadores en la partida, la información requerida de los
# jugadores, como sus ids, la obtengo de la interfaz
jugadores = {
    jugador.nuevo_jugador(0),
    jugador.nuevo_jugador(1),
    jugador.nuevo_jugador(2),
    jugador.nuevo_jugador(3)
}

partida = partida.nueva_partida(configuracion, jugadores)