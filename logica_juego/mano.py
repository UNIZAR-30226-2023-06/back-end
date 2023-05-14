import random

from .constants import Resource, Cards

# Representación de la mano de un jugador, es decir, qué cartas tiene, qué
# recursos y cartas de desarrollo
class Mano:
    def __init__(self, cartas_desarrollo : list[Cards], arcilla : int,
                  madera : int, trigo : int, piedra : int, oveja : int):
        self.cartas_desarrollo = cartas_desarrollo

        self.arcilla = arcilla
        self.madera = madera
        self.trigo = trigo
        self.piedra = piedra
        self.oveja = oveja

    # get para cada atributo
    def get_cartas_desarrollo(self):
        return self.cartas_desarrollo
    
    def get_arcilla(self):
        return self.arcilla
    
    def get_madera(self):
        return self.madera
    
    def get_oveja(self):
        return self.oveja
    
    def get_piedra(self):
        return self.piedra
    
    def get_trigo(self):
        return self.trigo

    def get_recurso(self, tipo_recurso):
        if tipo_recurso == Resource.CLAY:
            return self.arcilla
        elif tipo_recurso == Resource.WOOD:
            return self.madera
        elif tipo_recurso == Resource.SHEEP:
            return self.oveja
        elif tipo_recurso == Resource.STONE:
            return self.piedra
        elif tipo_recurso == Resource.WHEAT:
            return self.trigo
    
    # add para cada atributo
    def add_recurso(self, tipo_recurso:Resource, cantidad:int =1):
        if tipo_recurso == Resource.CLAY:
            self.arcilla += cantidad
        elif tipo_recurso == Resource.WOOD:
            self.madera += cantidad
        elif tipo_recurso == Resource.SHEEP:
            self.oveja += cantidad
        elif tipo_recurso == Resource.STONE:
            self.piedra += cantidad
        elif tipo_recurso == Resource.WHEAT:
            self.trigo += cantidad
    
    def add_carta_desarrollo(self, tipo_carta: Cards):
        self.cartas_desarrollo[tipo_carta.value] += 1
    
    def sub_carta_desarrollo(self, tipo_carta: Cards):
        if self.cartas_desarrollo[tipo_carta.value] > 0:
            self.cartas_desarrollo[tipo_carta.value] -= 1
        else:
            raise Exception("No tiene cartas de desarrollo de ese tipo")

    def tiene_carta_desarrollo(self, tipo_carta : Cards):
        return self.cartas_desarrollo[tipo_carta.value] > 0
    
    # sub para cada atributo
    def sub_recurso(self, tipo_recurso, cantidad=1):
        if tipo_recurso == Resource.CLAY:
            self.arcilla -= cantidad
        elif tipo_recurso == Resource.WOOD:
            self.madera -= cantidad
        elif tipo_recurso == Resource.SHEEP:
            self.oveja -= cantidad
        elif tipo_recurso == Resource.STONE:
            self.piedra -= cantidad
        elif tipo_recurso == Resource.WHEAT:
            self.trigo -= cantidad
    
    def num_total_recursos(self):
        return [self.arcilla, self.madera, self.oveja, self.piedra, self.trigo]

    # Se extrae un recurso aleatorio de entre todos los que hay en la mano (esto
    # se utiliza con el tema del ladrón)
    def extraer_recurso_aleatorio(self):
        index = random.randint(0, 4)
        recursos = self.num_total_recursos()
        recurso_robado = [0,0,0,0,0]
        i = 0
        while recursos[index] == 0 and i < 5:
            index = (index + 1) % 5
            i += 1
        recursos[index] -= 1
        recurso_robado[index] += 1

        self.arcilla = recursos[0]
        self.madera = recursos[1]
        self.oveja = recursos[2]
        self.piedra = recursos[3]
        self.trigo = recursos[4]

        return recurso_robado

def nueva_mano():
    mano = Mano([0,0,0,0,0,0,0,0,0],0,0,0,0,0)
    return mano