import random

import cartas

# Representación de la mano de un jugador, es decir, qué cartas tiene, qué
# recursos y cartas de desarrollo
class Mano:
    def __init__(self, cartas_desarrollo, arcilla, madera, trigo, piedra, oveja):
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
        if tipo_recurso == cartas.ARCILLA:
            return self.arcilla
        elif tipo_recurso == cartas.MADERA:
            return self.madera
        elif tipo_recurso == cartas.OVEJA:
            return self.oveja
        elif tipo_recurso == cartas.PIEDRA:
            return self.piedra
        elif tipo_recurso == cartas.TRIGO:
            return self.trigo
    
    # add para cada atributo
    def add_recurso(self, tipo_recurso, cantidad=1):
        if tipo_recurso == cartas.ARCILLA:
            self.arcilla += cantidad
        elif tipo_recurso == cartas.MADERA:
            self.arcilla += cantidad
        elif tipo_recurso == cartas.OVEJA:
            self.arcilla += cantidad
        elif tipo_recurso == cartas.PIEDRA:
            self.arcilla += cantidad
        elif tipo_recurso == cartas.TRIGO:
            self.arcilla += cantidad
    
    def add_carta_desarrollo(self, tipo_carta):
        self.cartas_desarrollo.append(tipo_carta)
    
    def sub_carta_desarrollo(self, tipo_carta):
        self.cartas_desarrollo.remove(tipo_carta)
    
    # sub para cada atributo
    def sub_recurso(self, tipo_recurso, cantidad=1):
        if tipo_recurso == cartas.ARCILLA:
            self.arcilla -= cantidad
        elif tipo_recurso == cartas.MADERA:
            self.arcilla -= cantidad
        elif tipo_recurso == cartas.OVEJA:
            self.arcilla -= cantidad
        elif tipo_recurso == cartas.PIEDRA:
            self.arcilla -= cantidad
        elif tipo_recurso == cartas.TRIGO:
            self.arcilla -= cantidad
    
    def num_total_recursos(self):
        return self.arcilla + self.piedra + self.madera + self.trigo + self.oveja

    # Se extrae un recurso aleatorio de entre todos los que hay en la mano (esto
    # se utiliza con el tema del ladrón)
    def extraer_recurso_aleatorio(self):
        a = random.randint(1, self.num_total_recursos())

        for i in range(self.arcilla):
            a -= 1
            if a == 0:
                self.arcilla -= 1
                return {1,0,0,0,0}
        
        for i in range(self.madera):
            a -= 1
            if a == 0:
                self.madera -= 1
                return {0,1,0,0,0}
        
        for i in range(self.oveja):
            a -= 1
            if a == 0:
                self.oveja -= 1
                return {0,0,1,0,0}
        
        for i in range(self.piedra):
            a -= 1
            if a == 0:
                self.piedra -= 1
                return {0,0,0,1,0}
        
        for i in range(self.trigo):
            a -= 1
            if a == 0:
                self.trigo -= 1
                return {0,0,0,0,1}

def nueva_mano():
    mano = Mano({},0,0,0,0,0)
    return mano