from .mano import Mano, nueva_mano
#import cartas

from .board import Color
from .constants import Resource
# class Color:
#     NO_ASIGNADO = 0
#     ROJO = 1
#     AMARILLO = 2
#     BLANCO = 3
#     AZUL = 4


class Jugador:
    def __init__(self, id : int, elo:int, puntos_victoria : int, color : Color, mano : Mano, caballeros_usados : int,
                 tiene_bono_carreteras : bool, tiene_bono_caballeros : bool, esta_preparado : bool, activo : bool):
        # identificador del jugador
        self.id = id

        self.puntos_victoria = puntos_victoria
        self.color = color

        self.mano = mano

        self.caballeros_usados = caballeros_usados

        self.tiene_bono_carreteras = tiene_bono_carreteras
        self.tiene_bono_caballeros = tiene_bono_caballeros

        self.esta_preparado = esta_preparado
        self.elo = elo
        self.activo = True

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
        # self.mano.arcilla += recursos[0]
        # self.mano.madera += recursos[1]
        # self.mano.oveja += recursos[2]
        # self.mano.piedra += recursos[3]
        # self.mano.trigo += recursos[4]

        self.mano.add_recurso(Resource.CLAY, recursos[0])
        self.mano.add_recurso(Resource.WOOD, recursos[1])
        self.mano.add_recurso(Resource.SHEEP, recursos[2])
        self.mano.add_recurso(Resource.STONE, recursos[3])
        self.mano.add_recurso(Resource.WHEAT, recursos[4])
    
    def restar_recursos(self, recursos):
        #check whether the player has enough resources
        if self.mano.get_recurso(Resource.CLAY) >= recursos[0]   and \
            self.mano.get_recurso(Resource.WOOD) >= recursos[1]  and \
            self.mano.get_recurso(Resource.SHEEP) >= recursos[2] and \
            self.mano.get_recurso(Resource.STONE) >= recursos[3] and \
            self.mano.get_recurso(Resource.WHEAT) >= recursos[4]:

            self.mano.sub_recurso(Resource.CLAY, recursos[0])
            self.mano.sub_recurso(Resource.WOOD, recursos[1])
            self.mano.sub_recurso(Resource.SHEEP, recursos[2])
            self.mano.sub_recurso(Resource.STONE, recursos[3])
            self.mano.sub_recurso(Resource.WHEAT, recursos[4])
            return True
        else:
            return False
    
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
    
    def tiene_carta_desarrollo(self, tipo_carta):
        return self.mano.tiene_carta_desarrollo(tipo_carta)

    def robar_monopolio(self, recurso):
        cantidad_robada = self.mano.get_recurso(recurso)
        self.mano.sub_recurso(recurso, cantidad_robada)
        return cantidad_robada
    
    def set_preparado(self):
        self.esta_preparado = True

    def get_preparado(self):
        return self.esta_preparado

def nuevo_jugador(id : int, color : Color):
    mano_inicial = nueva_mano()

    jugador = Jugador(id, 0, color, mano_inicial, 0, False, False,
                      False, False, True)
    return jugador


