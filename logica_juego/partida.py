import random

import cartas
import construcciones
import jugador
import errores

class Partida:
    def __init__(self, num_jugadores, turno, fase_turno, codigo, jugadores,
                 partida_empezada, tablero, chat, hay_ladron, tiempo_turno,
                 num_jugadores_activos, jugadores_seleccionados):

        # Código de la sala de juego
        self.codigo = codigo

        # Un array de datos de tipo "Jugador"
        self.jugadores = jugadores

        self.num_jugadores = num_jugadores

        self.num_jugadores_activos = num_jugadores_activos

        # El turno: cuál de los 4 jugadores tiene la prioridad
        self.turno = turno

        # Fases del turno: obtención de recursos, uso de cartas de desarrollo,
        # negociación y compra
        self.fase_turno = fase_turno

        # Duración de un turno en segundos
        self.tiempo_turno = tiempo_turno

        # Booleano que indica si la partida ha sido empezada, es decir, los
        # jugadores han elegido color, se ha determinado el orden de los turnos,
        # y cada jugador ha colocado sus dos primeras aldeas y carreteras
        self.partida_empezada = partida_empezada

        # Booleano que indica si ya se han establecido los jugadores de la
        # partida y se le ha dado a comenzar la partida (aún no se han colocado
        # las construcciones iniciales)
        self.jugadores_seleccionados = jugadores_seleccionados

        self.tablero = tablero

        # El chat es un array de strings, puede que este atributo al final no
        # sea necesario
        self.chat = chat

        # Una de las opciones de configuración de una partida es si se juega con
        # ladrón o no
        self.hay_ladron = hay_ladron

    ################ FUNCIONES SOBRE LA GESTIÓN DE JUGADORES ################

    # Añade un nuevo jugador a la partida. Devuelve true si todo ha ido bien o
    # false si la partida ya está llena o si ya ha comenzado.
    def anadir_jugador(self, id_jugador):
        if self.jugadores_seleccionados:
            return errores.PARTIDA_COMENZADA
        for i in range(self.num_jugadores):
            if self.jugadores[i] == None:
                self.jugadores[i] = jugador.nuevo_jugador(id_jugador)
                self.num_jugadores_activos = self.num_jugadores_activos + 1
                return errores.PARTIDA_LLENA
        return errores.SIN_ERRORES
    
    # Resta un jugador al contador de jugadores en la partida. Si la partida
    # aún no ha empezado, lo elimina por completo. Si sí ha empezado simplemente
    # lleva la cuenta de que hay un juagor activo menos, pero cuenta como que
    # el jugador sigue formando parte de la partida.
    def restar_jugador(self, id_jugador):
        if not self.partida_empezada:
            for i in range(self.num_jugadores):
                if self.jugadores[i] == id_jugador:

                    # Elimino al jugador del registro 
                    self.jugadores[i] = None

                    # Reorganizao la lista de jugadores
                    for j in range(i+1, self.num_jugadores + 1):
                        if j == self.num_jugadores:
                            self.jugadores[j-1] = None
                        else:
                            self.jugadores[j-1] = self.jugadores[j]

                    self.num_jugadores_activos = self.num_jugadores_activos - 1

                    break
        
        self.num_jugadores_activos = self.num_jugadores_activos - 1

    # Obtenemos el índice del jugador en la lista de jugadores con id igual al
    # pasado por parámetro.
    def i_jugador(self, id):
        c = 0
        for j in self.jugadores:
            if j.get_id() == id:
                return c
            else:
                c += 1
    
    # Devuelve el número de jugadores en la partida
    def get_num_jugadores_activos(self):
        return self.num_jugadores_activos
    

    ##########################################################################

    ################# FUNCIONES SOBRE LA GESTIÓN DE RECURSOS #################

    # El jugador 1 roba un recurso aleatorio al jugador 2
    def robar_recursos(self, id_jugador1, id_jugador2):
        j1 = self.i_jugador(id_jugador1)
        j2 = self.i_jugador(id_jugador2)

        recurso_robado = self.jugadores[j2].robar_recurso()
        self.jugadores[j1].sumar_recursos(recurso_robado)
    
    # El jugador 1 le da sus x recursos al jugador 2, y viceversa
    # Los recursos se codifican con el formato {arcilla, madera, oveja, piedra, trigo}
    def intercambiar_recursos(self, id_jugador1, recursos_1, id_jugador2, recursos_2):
        #recursos_1 = {0,0,0,0,0}
        #recursos_1[tipo_recurso_1] = cantidad_recurso_1
        #
        #recursos_2 = {0,0,0,0,0}
        #recursos_2[tipo_recurso_2] = cantidad_recurso_2

        j1 = self.i_jugador(id_jugador1)
        j2 = self.i_jugador(id_jugador2)

        self.jugadores[j1].restar_recursos(recursos_1)
        self.jugadores[j1].sumar_recursos(recursos_2)
        self.jugadores[j2].restar_recursos(recursos_2)
        self.jugadores[j2].sumar_recursos(recursos_1)
    
    # Se obtienen los recursos en función de la tirada de dados
    def asignacion_recursos(self):
        tirada_dados = random.randint(1,6) + random.randint(1,6)

        # Se avisa al frontend de la tirada de dados
        #

        # Consultamos en el tablero los recursos que obtiene cada jugador
        for j in self.jugadores:
            # recursos = tablero.recursos_obtenidos(j.get_id(), tirada_dados)
            recursos = {0,0,0,0,0}

            j.sumar_recursos(recursos)
    
    def usar_carta_desarrollo(self, id_jugador, tipo_carta):
        self.sub_carta_desarrollo(tipo_carta)

        if tipo_carta == cartas.CABALLERO:
            self.mover_ladron(id_jugador)
            self.jugadores[self.i_jugador(id_jugador)].add_caballero()
            self.check_bono_caballeros(self.jugadores[self.i_jugador(id_jugador)])

        elif tipo_carta == cartas.PROGRESO_INVENTO:
            # Obtenemos del frontend qué 2 recursos quiere obtener el jugador
            recursos = {0,0,0,0,0}
            self.jugadores[self.i_jugador(id_jugador)].sumar_recursos(recursos)

        elif tipo_carta == cartas.PROGRESO_CARRETERAS:
            # Obtenemos del frontend dónde quiere construir el jugador las carreteras
            coordenadas_1 = 0
            coordenadas_2 = 0

            # Indicamos al tablero dónde construimos las carreteras

        elif tipo_carta == cartas.PROGRESO_MONOPOLIO:
            # Obtenemos del frontend qué recurso quiere robar el jugador
            tipo_recurso = cartas.ARCILLA

            recursos = {0,0,0,0,0}

            for j in self.jugadores:
                if j.get_id() != id_jugador:
                    recursos[tipo_recurso] += j.robar_monopolio(tipo_recurso)
            
            self.jugadores[self.i_jugador(id_jugador)].sumar_recursos(recursos)

        else:
            self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()

    # El jugador con el id pasado cambia X cantidad de sus recursos_1 por una
    # unidad del recurso_2
    def intercambiar_banca(self, id_jugador, tipo_recurso_1, cantidad_recurso, tipo_recurso_2):
        recursos_1 = {0,0,0,0,0}
        recursos_1[tipo_recurso_1] = cantidad_recurso

        recursos_2 = {0,0,0,0,0}
        recursos_2[tipo_recurso_2] = 1

        j = self.i_jugador(id_jugador)

        self.jugadores[j].restar_recursos(recursos_1)
        self.jugadores[j].sumar_recursos(recursos_2)
    
    ##########################################################################
    
    ################# FUNCIONES SOBRE LA GESTIÓN DEL LADRÓN #################

    def mover_ladron(self, id_jugador):
        # Obtenemos del frontend la posición a la que el jugador quiere mover
        # el ladrón

        # Movemos el ladrón a la posición indicada en el tablero

        # Obtenemos los jugadores a los que el jugador que ha movido el ladrón
        # puede robar

        # Indicamos al frontend dichos usuarios para que el jugador seleccione
        # uno
        id_jugador_robado = 0

        self.robar_recursos(id_jugador, id_jugador_robado)
    
    # especificamos si queremos que haya un ladrón en la partida
    def set_ladron(self, hay_ladron):
        self.hay_ladron = hay_ladron
    
    ##########################################################################
    
    ################ FUNCIONES SOBRE LA GESTIÓN DE LOS TURNOS ################
    
    # Se pasa a la siguiente fase del turno actual, y se pasa al siguiente turno
    # si el actual ya ha acabado
    def avanzar_fase(self):
        self.fase_turno = (self.fase_turno + 1)%4
        if self.fase_turno == 0:
            self.turno = (self.turno + 1)%4

    # Establecemos el tiempo de duración de los turnos en segundos
    def set_tiempo_turno(self, tiempo_turno):
        self.tiempo_turno = tiempo_turno
    
    ##########################################################################
    
    ############ FUNCIONES SOBRE LA GESTIÓN DE LAS CONSTRUCCIONES ############

    def comprar(self, id_jugador, tipo_construccion):
        if tipo_construccion == construcciones.CARRETERA:
            self.jugadores[self.i_jugador(id_jugador)].restar_recursos({1,1,0,0,0})

            # Pregunto al frontend dónde quiere el jugador colocar la construcción
            coordenadas = 0

            # Indico al tablero que coloque la construcción de dicho tipo
            # tablero.colocar_carretera(coordenadas)

            self.check_bono_caballeros(self.jugadores[self.i_jugador(id_jugador)])

        elif tipo_construccion == construcciones.POBLADO:
            self.jugadores[self.i_jugador(id_jugador)].restar_recursos({1,1,1,0,1})

            # Pregunto al frontend dónde quiere el jugador colocar la construcción
            coordenadas = 0

            # Indico al tablero que coloque la construcción de dicho tipo
            # tablero.colocar_poblado(coordenadas)

            self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()

        elif tipo_construccion == construcciones.CIUDAD:
            self.jugadores[self.i_jugador(id_jugador)].restar_recursos({0,0,0,3,2})

            # Pregunto al frontend dónde quiere el jugador colocar la construcción
            coordenadas = 0

            # Indico al tablero que coloque la construcción de dicho tipo
            # tablero.colocar_ciudad(coordenadas)

            self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()

        elif tipo_construccion == construcciones.CARTA_DESARROLLO:
            self.jugadores[self.i_jugador(id_jugador)].restar_recursos({0,0,1,1,1})

            carta_robada = cartas.random_carta_desarrollo()

            # informo a frontend de la carta robada

            self.jugadores[self.i_jugador(id_jugador)].add_carta_desarrollo(carta_robada)

    ##########################################################################

    ########## FUNCIONES SOBRE LA GESTIÓN DE LOS PUNTOS DE VICTORIA ##########

    # Comprueba si un jugador ha ganado, si es así devolverá su id, si no,
    # devolverá -1
    def check_ganador(self):
        for j in self.jugadores:
            if j.get_puntos_victoria() <= 10:
                return j.get_id()
        return -1
    
    # Checkea si el jugador indicado puede obtener el bono por carreteras
    def check_bono_carreteras(self, jugador):

        # Comprobamos quién tiene actualmente el bono de las carreteras (si no
        # lo tiene nadie esta variable se queda como -1), se guarda su id
        poseeder_bono_actual = -1
        indice_poseedor_bono_actual = 0

        for j in self.jugadores:
            if j.bono_carreteras():
                poseeder_bono_actual = j.get_id()
                break
            indice_poseedor_bono_actual += 1
        
        if poseeder_bono_actual == -1:
            # consulto en el tablero el número de carreteras consecutivas del
            # jugador "jugador".
            num_carreteras = random(0,1)

            if num_carreteras >= 5:
                jugador.otorgar_bono_carreteras()
        
        else:
            # consulto en el tablero el número de carreteras consecutivas del
            # jugador "jugador" y el jugador que posee el bono actualmente.
            num_carreteras_jugador = random(0,1)
            num_carreteras_poseedor_bono = random(0,1)
            
            if num_carreteras_jugador > num_carreteras_poseedor_bono:
                jugador.otorgar_bono_carreteras()
                self.jugadores[indice_poseedor_bono_actual].quitar_bono_carreteras()
    
    # Checkea si el jugador indicado puede obtener el bono por carreteras
    def check_bono_caballeros(self, jugador):

        # Comprobamos quién tiene actualmente el bono de las caballeros (si no
        # lo tiene nadie esta variable se queda como -1), se guarda su id
        poseeder_bono_actual = -1
        indice_poseedor_bono_actual = 0

        for j in self.jugadores:
            if j.bono_caballeros():
                poseeder_bono_actual = j.get_id()
                break
            indice_poseedor_bono_actual += 1
        
        if poseeder_bono_actual == -1:
            num_caballeros = jugador.get_caballeros_usados()

            if num_caballeros >= 3:
                jugador.otorgar_bono_caballeros()
        
        else:
            num_caballeros_jugador = jugador.jugador.get_caballeros_usados()
            num_caballeros_poseedor_bono = self.jugadores[indice_poseedor_bono_actual].get_caballeros_usados()
            
            if num_caballeros_jugador > num_caballeros_poseedor_bono:
                jugador.otorgar_bono_caballeros()
                self.jugadores[indice_poseedor_bono_actual].quitar_bono_caballeros()
    
    ##########################################################################

    ########### FUNCIONES SOBRE LA GESTIÓN DEL ELO DE LOS JUGADORES ###########
    
    def repartir_elo(self):
        ranking = {{},{},{},{}}

        jugadores = self.jugadores

        # Obtengo el orden en que han acabado los jugadores (puede haber empates
        # en puestos que no sean el primero por puntos de victoria)
        for i in range(4):
            max_elo = 0
            jugadores_a_descartar = {}

            for j in jugadores:
                # Consulto el elo del jugador en la base de datos
                elo = random(0,1)

                if elo > max_elo:
                    max_elo = elo

            for j in jugadores:
                # Consulto el elo del jugador en la base de datos
                elo = random(0,1)

                if elo == max_elo:
                    ranking[i].append(j)
                    jugadores_a_descartar.append(j)

            for j in jugadores_a_descartar:
                jugadores.remove(j)
        
        for j in ranking[0]:
            # Sumo 50 de elo al jugador j
            jugadores = {}
        
        for j in ranking[1]:
            # Sumo 25 de elo al jugador j
            jugadores = {}
        
        for j in ranking[2]:
            # Resto 25 de elo al jugador j
            jugadores = {}
        
        for j in ranking[3]:
            # Resto 50 de elo al jugador j
            jugadores = {}

    ##########################################################################

    ############################# OTRAS FUNCIONES #############################

    # Devuelve true si la partida está en curso, es decir, se ha iniciado la
    # partida y los jugadores ya han colocado sus construcciones iniciales
    def get_partida_empezada(self):
        return self.partida_empezada

    ###########################################################################

# Crea un instancia inicializada de una partida y la devuelve
def nueva_partida():
    codigo = obtener_codigo_libre()
    # tablero = Tablero.nuevo_tablero()
    tablero = None

    partida = Partida(4, 0, 0, codigo, {None, None, None, None}, False, tablero,
                      {}, True, 30, 0, False)
    
    return partida, codigo

# Busca en la base de datos un código que no esté siendo utilizado por ninguna
# partida y lo devuelve
def obtener_codigo_libre():
    return 1

