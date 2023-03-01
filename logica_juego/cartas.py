import random

############################ CARTAS DE DESARROLLO ############################
CABALLERO = 0

# Obtener 2 recursos cualesquiera
PROGRESO_INVENTO = 1
# Construir 2 carreteras
PROGRESO_CARRETERAS = 2
# Robar todos los recursos de un tipo a los jugadores
PROGRESO_MONOPOLIO = 3

# Los 5 tipos de puntos de victoria
AYUNTAMIENTO = 4
BIBLIOTECA = 5
MERCADO = 6
IGLESIA = 7
UNIVERSIDAD = 8

CARTAS_TOTALES = {
    CABALLERO, CABALLERO, CABALLERO, CABALLERO, CABALLERO, CABALLERO, CABALLERO,
    CABALLERO, CABALLERO, CABALLERO, CABALLERO, CABALLERO, CABALLERO, CABALLERO,

    PROGRESO_CARRETERAS, PROGRESO_CARRETERAS,

    PROGRESO_INVENTO, PROGRESO_INVENTO,

    PROGRESO_MONOPOLIO, PROGRESO_MONOPOLIO,

    AYUNTAMIENTO, BIBLIOTECA, MERCADO, IGLESIA, UNIVERSIDAD
}
    
def random_carta_desarrollo():
    return random.choice(CARTAS_TOTALES)

################################## RECURSOS ##################################
ARCILLA = 0
MADERA = 1
OVEJA = 2
PIEDRA = 3
TRIGO = 4