import mano
import cartas

class Jugador:
    def __init__(self, id, puntos_victoria, color, mano, caballeros_usados,
                 tiene_bono_carreteras, tiene_bono_caballeros, esta_preparado):
        # identificador del jugador
        self.id = id

        self.puntos_victoria = puntos_victoria
        self.color = color

        self.mano = mano

        self.caballeros_usados = caballeros_usados

        self.tiene_bono_carreteras = tiene_bono_carreteras
        self.tiene_bono_caballeros = tiene_bono_caballeros

        self.esta_preparado = esta_preparado

    def get_id(self):
        return self.id

    def get_puntos_victoria(self):
        return self.puntos_victoria
    
    def bono_carreteras(self):
        return self.tiene_bono_carreteras
    
    def bono_caballeros(self):
        return self.tiene_bono_caballeros
    
    def otorgar_bono_carreteras(self):
        self.tiene_bono_carreteras = True
        self.add_puntos_victoria(2)
    
    def otorgar_bono_caballeros(self):
        self.tiene_bono_caballeros = True
        self.add_puntos_victoria(2)
    
    def quitar_bono_carreteras(self):
        self.tiene_bono_carreteras = False
        self.add_puntos_victoria(-2)
    
    def quitar_bono_caballeros(self):
        self.tiene_bono_caballeros = False
        self.add_puntos_victoria(-2)
    
    def robar_recurso(self):
        return self.mano.extraer_recurso_aleatorio()
    
    def sumar_recursos(self, recursos):
        self.mano.add_recurso(cartas.ARCILLA, recursos[0])
        self.mano.add_recurso(cartas.MADERA, recursos[1])
        self.mano.add_recurso(cartas.OVEJA, recursos[2])
        self.mano.add_recurso(cartas.PIEDRA, recursos[3])
        self.mano.add_recurso(cartas.TRIGO, recursos[4])
    
    def restar_recursos(self, recursos):
        self.mano.sub_recurso(cartas.ARCILLA, recursos[0])
        self.mano.sub_recurso(cartas.MADERA, recursos[1])
        self.mano.sub_recurso(cartas.OVEJA, recursos[2])
        self.mano.sub_recurso(cartas.PIEDRA, recursos[3])
        self.mano.sub_recurso(cartas.TRIGO, recursos[4])
    
    def add_caballero(self):
        self.caballeros_usados += 1
    
    def get_caballeros_usados(self):
        return self.caballeros_usados
    
    def add_puntos_victoria(self, cantidad=1):
        self.puntos_victoria += cantidad
    
    def add_carta_desarrollo(self, tipo_carta):
        self.mano.add_carta_desarrollo(tipo_carta)
    
    def sub_carta_desarrollo(self, tipo_carta):
        self.mano.sub_carta_desarrollo(tipo_carta)
    
    def robar_monopolio(self, recurso):
        cantidad_robada = self.mano.get_recurso(recurso)
        self.mano.sub_recurso(recurso, cantidad_robada)
        return cantidad_robada
    
    def set_preparado(self):
        self.esta_preparado = True

    def get_preparado(self):
        return self.esta_preparado

def nuevo_jugador(id):
    mano_inicial = mano.nueva_mano()

    jugador = Jugador(id, 0, Color.NO_ASIGNADO, mano_inicial, 0, False, False,
                      False)
    return jugador

class Color:
    NO_ASIGNADO = 0
    ROJO = 1
    AMARILLO = 2
    BLANCO = 3
    AZUL = 4

