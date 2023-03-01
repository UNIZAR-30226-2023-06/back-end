class Configuracion:
    def __init__(self, num_jugadores, hay_ladron, tiempo_turno):
        self.num_jugadores = num_jugadores
        self.hay_ladron = hay_ladron
        self.tiempo_turno = tiempo_turno # en segundos

def nueva_configuracion(num_jugadores, hay_ladron, tiempo_turno):
    configuracion = Configuracion(num_jugadores, hay_ladron, tiempo_turno)
    return configuracion

