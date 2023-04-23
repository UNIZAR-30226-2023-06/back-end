import random

# import cartas
# import construcciones
from .jugador import Jugador
from logica_juego.board import Board, NodeDirection
# import errores

from .constants import Errors, Color, Cards, Building, Resource, TurnPhase

class Partida:
    def __init__(self, num_jugadores: int, turno: int , fase_turno: TurnPhase, jugadores: list[Jugador],
                 tiempo_turno: int,
                 num_jugadores_activos: int, jugadores_seleccionados: int,
                 tablero: Board | None = None, hay_ladron: bool = True):

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

        # Booleano que indica si ya se han establecido los jugadores de la
        # partida y se le ha dado a comenzar la partida (aún no se han colocado
        # las construcciones iniciales)
        self.jugadores_seleccionados = jugadores_seleccionados
        self.hay_ladron = hay_ladron

        if tablero is not None:
            self.board = tablero
        else:
            self.board = Board() # TODO lo del ladron

    ################ FUNCIONES SOBRE LA GESTIÓN DE JUGADORES ################

    # Defines whether the player is "active" or not. True if the player is active, False otherwise.
    def set_player_status(self, id_jugador : int, status : bool):
        for jugador in self.jugadores:
            if jugador.get_id() == id_jugador:
                jugador.activo = status
                if status == False: self.num_jugadores_activos -= 1
                else: self.num_jugadores_activos += 1
                break

    # Obtenemos el índice del jugador en la lista de jugadores con id igual al
    # pasado por parámetro.
    def i_jugador(self, id: int) -> int:
        for i, j in enumerate(self.jugadores):
            if j.get_id() == id:
                return i
    
    # Devuelve el número de jugadores en la partida
    def get_num_jugadores_activos(self) -> int:
        return self.num_jugadores_activos
    
    # Indico que el jugador con id "id_jugador" está listo para empezar y
    # devuelvo True si todos los jugadores están listos
    def jugador_listo(self, id_jugador: int) -> bool:
        self.jugadores[self.i_jugador(id_jugador)].set_preparado()

        for j in self.jugadores:
            if not j.get_preparado():
                return False
        
        return True

    ##########################################################################

    ################# FUNCIONES SOBRE LA GESTIÓN DE RECURSOS #################

    # El jugador 1 roba un recurso aleatorio al jugador 2
    #TODO: check whether the robbed player has enough resources
    def robar_recursos(self, id_jugador1: int, id_jugador2: int):
        if self.fase_turno != TurnPhase.RESOURCE_PRODUCTION:
            raise Exception("No se pueden robar recursos en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador1:
            raise Exception("No es el turno del jugador")

        j1 = self.i_jugador(id_jugador1)
        j2 = self.i_jugador(id_jugador2)

        recurso_robado = self.jugadores[j2].robar_recurso()
        self.jugadores[j1].sumar_recursos(recurso_robado)
    
    # El jugador 1 le da sus x recursos al jugador 2, y viceversa
    # Los recursos se codifican con el formato {arcilla, madera, oveja, piedra, trigo}
    #TODO: check whether the players have enough resources
    def intercambiar_recursos(self, id_jugador1 : int , recursos_1 : list[int], id_jugador2 : int, recursos_2 : list[int]):
        #recursos_1 = {0,0,0,0,0}
        #recursos_1 = {CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
        #recursos_1[tipo_recurso_1] = cantidad_recurso_1
        #
        #recursos_2 = {0,0,0,0,0}
        #recursos_2[tipo_recurso_2] = cantidad_recurso_2

        if self.fase_turno != TurnPhase.TRADING:
            raise Exception("No se pueden intercambiar recursos en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador1:
            raise Exception("No es el turno del jugador")


        j1 = self.i_jugador(id_jugador1)
        j2 = self.i_jugador(id_jugador2)

        self.jugadores[j1].restar_recursos(recursos_1)
        self.jugadores[j1].sumar_recursos(recursos_2)
        self.jugadores[j2].restar_recursos(recursos_2)
        self.jugadores[j2].sumar_recursos(recursos_1)
    
    # Se obtienen los recursos en función de la tirada de dados
    def asignacion_recursos(self):
        dado1 = random.randint(1,6)
        dado2 = random.randint(1,6)
        tirada_dados = dado1 + dado2

        if self.fase_turno != TurnPhase.RESOURCE_PRODUCTION:
            raise Exception("No se pueden obtener recursos en esta fase del turno")

        # Consultamos en el tablero los recursos que obtiene cada jugador
        for j in self.jugadores:
            recursos = self.board.return_resources(j.color, tirada_dados)
            j.sumar_recursos(recursos)
        
        return dado1, dado2
    
    def usar_carta_desarrollo(self, id_jugador: int, tipo_carta : Cards, coords:int | None = None):
        
        if self.fase_turno != TurnPhase.BUILDING:
            raise Exception("No se puede usar una carta de desarrollo en esta fase del turno")
        
        index_jugador = self.i_jugador(id_jugador)
        jugador = self.jugadores[index_jugador]
        
        # Comprobamos que el jugador tiene la carta de desarrollo
        if jugador.tiene_carta_desarrollo(tipo_carta):
            self.sub_carta_desarrollo(tipo_carta)
        else:
            raise Exception("El jugador no tiene la carta de desarrollo")

        if tipo_carta == Cards.KNIGHT:
            self.mover_ladron(id_jugador)
            self.jugadores[self.i_jugador(id_jugador)].add_caballero()
            self.check_bono_caballeros(self.jugadores[self.i_jugador(id_jugador)])

        elif tipo_carta == Cards.INVENTION_PROGRESS:
            # Obtenemos del frontend qué 2 recursos quiere obtener el jugador
            recursos = {0,0,0,0,0}
            self.jugadores[self.i_jugador(id_jugador)].sumar_recursos(recursos)

        elif tipo_carta == Cards.ROAD_PROGRESS:
            # Indicamos al tablero dónde construimos las carreteras
            if not self.board.place_road(jugador.color, coords):
                raise Exception("No se puede construir la carretera")


        elif tipo_carta == Cards.MONOPOLY_PROGRESS:
            # Obtenemos del frontend qué recurso quiere robar el jugador
            tipo_recurso = Resource.CLAY

            recursos = {0,0,0,0,0}

            for j in self.jugadores:
                if j.get_id() != id_jugador:
                    recursos[tipo_recurso] += j.robar_monopolio(tipo_recurso)
            
            self.jugadores[self.i_jugador(id_jugador)].sumar_recursos(recursos)

        else:
            self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()

    # El jugador con el id pasado cambia X cantidad de sus recursos_1 por una
    # unidad del recurso_2
    def intercambiar_banca(self, id_jugador:int, tipo_recurso_1:Resource, cantidad_recurso:int, tipo_recurso_2:Resource):
        
        if self.fase_turno != TurnPhase.TRADING:
            raise Exception("No se pueden intercambiar recursos en esta fase del turno")
        
        recursos_1 = {0,0,0,0,0} # {CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
        recursos_1[tipo_recurso_1] = cantidad_recurso

        recursos_2 = {0,0,0,0,0} # {CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
        recursos_2[tipo_recurso_2] = 1

        j = self.i_jugador(id_jugador)

        self.jugadores[j].restar_recursos(recursos_1)
        self.jugadores[j].sumar_recursos(recursos_2)
    
    ##########################################################################
    
    ################# FUNCIONES SOBRE LA GESTIÓN DEL LADRÓN #################

    def mover_ladron(self, tileCoord:int, id_jugador:int, id_jugador_robado:int):
        # Movemos el ladrón a la posición indicada en el tablero
        jugador = self.jugadores[self.i_jugador(id_jugador)]
        jugador_robado = self.jugadores[self.i_jugador(id_jugador_robado)]

        nodes_around_thief = []
        possible_directions : NodeDirection = {NodeDirection.N, NodeDirection.NE, NodeDirection.SE, NodeDirection.S, NodeDirection.SW, NodeDirection.NW}
        for direction in possible_directions:
            tile_id = self.board.get_tile_by_id(tileCoord)
            node = self.board.get_node(tile_id, direction)
            if node != None:
                nodes_around_thief.append(node)
        possible_nodes = []
        for node in nodes_around_thief:
            if self.board.nodes[node] == (jugador_robado.color, Building.VILLAGE) or self.board.nodes[node] == (jugador_robado.color, Building.CITY):
                possible_nodes.append(node)
        if len(possible_nodes) == 0:
            raise Exception("Error: No hay ningún edificio del jugador robado en los nodos adyacentes al ladrón")

        if self.board.move_thief(tileCoord):
            self.robar_recursos(id_jugador, id_jugador_robado)
        else:
            raise Exception("Error: No se ha podido mover el ladrón")

    # especificamos si queremos que haya un ladrón en la partida
    def set_ladron(self, hay_ladron:bool):
        self.hay_ladron = hay_ladron
    
    ##########################################################################
    
    ################ FUNCIONES SOBRE LA GESTIÓN DE LOS TURNOS ################
    
    # Se pasa a la siguiente fase del turno actual, y se pasa al siguiente turno
    # si el actual ya ha acabado
    def avanzar_fase(self):
        self.fase_turno = (self.fase_turno + 1)%3
        if self.fase_turno == TurnPhase.RESOURCE_PRODUCTION:
            self.turno = (self.turno + 1)%4

    # Establecemos el tiempo de duración de los turnos en segundos
    def set_tiempo_turno(self, tiempo_turno:int):
        self.tiempo_turno = tiempo_turno

    
    
    ##########################################################################
    
    ############ FUNCIONES SOBRE LA GESTIÓN DE LAS CONSTRUCCIONES ############

    def comprar_y_construir(self, id_jugador:int, tipo_construccion:Building, coord:int):
        
        if self.fase_turno != TurnPhase.BUILDING:
            raise Exception("No se pueden construir edificios en esta fase del turno")
        
        player : Jugador = self.jugadores[self.i_jugador(id_jugador)]
        if tipo_construccion == Building.ROAD:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos({1,1,0,0,0}): # Si no tiene los recursos suficientes
                raise Exception("Error: No tienes los recursos suficientes para construir la carretera")

            if self.board.place_road(player.color, coord):
                self.check_bono_caballeros(self.jugadores[self.i_jugador(id_jugador)])
            else:
                raise Exception("Error: No se ha podido construir la carretera")

        elif tipo_construccion == Building.VILLAGE:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos({1,1,1,0,1}): # Si no tiene los recursos suficientes
                raise Exception("Error: No tienes los recursos suficientes para construir el poblado")

            if self.board.place_town(player.color, coord):
                self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()
            else:
                raise Exception("Error: No se ha podido construir el poblado")

        elif tipo_construccion == Building.CITY:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos({0,0,0,3,2}):
                raise Exception("Error: No tienes los recursos suficientes para construir la ciudad")

            if self.board.upgrade_town(coord):
                self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()
            else:
                raise Exception("Error: No se ha podido construir la ciudad")

        elif tipo_construccion == Building.DEV_CARD:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos({0,0,1,1,1}): # Si no tiene los recursos suficientes
                raise Exception("Error: No tienes los recursos suficientes para comprar la carta de desarrollo")
            carta_robada = Cards.pick_random_card()
            self.jugadores[self.i_jugador(id_jugador)].add_carta_desarrollo(carta_robada)

    #!#########################################################################

    ########## FUNCIONES SOBRE LA GESTIÓN DE LOS PUNTOS DE VICTORIA ##########

    # Comprueba si un jugador ha ganado, si es así devolverá su id, si no,
    # devolverá -1
    def check_ganador(self) -> int:
        for j in self.jugadores:
            if j.get_puntos_victoria() >= 10:
                return j.get_id()
        return -1
    
    # Checkea si el jugador indicado puede obtener el bono por carreteras
    def check_bono_carreteras(self, jugador:Jugador):

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
            num_carreteras_jugador = self.board.longest_path(jugador.color)
            if num_carreteras_jugador >= 5:
                jugador.otorgar_bono_carreteras()
        else:
            # consulto en el tablero el número de carreteras consecutivas del
            # jugador "jugador" y el jugador que posee el bono actualmente.
            num_carreteras_jugador = self.board.longest_path(jugador.color)
            num_carreteras_poseedor_bono = self.board.longest_path(self.jugadores[indice_poseedor_bono_actual].color)
            
            if num_carreteras_jugador > num_carreteras_poseedor_bono:
                jugador.otorgar_bono_carreteras()
                self.jugadores[indice_poseedor_bono_actual].quitar_bono_carreteras()
    
    # Checkea si el jugador indicado puede obtener el bono por carreteras
    def check_bono_caballeros(self, jugador:Jugador):

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
                if j.elo > max_elo:
                    max_elo = j.elo

            for j in jugadores:
                if j.elo == max_elo:
                    ranking[i].append(j)
                    jugadores_a_descartar.append(j)

            for j in jugadores_a_descartar:
                jugadores.remove(j)
        
        for j in ranking[0]:
            # Sumo 50 de elo al jugador j
            j.elo += 50
        
        for j in ranking[1]:
            # Sumo 25 de elo al jugador j
            j.elo += 25

        for j in ranking[2]:
            # Resto 25 de elo al jugador j
            j.elo -= 25

        for j in ranking[3]:
            # Resto 50 de elo al jugador j
            j.elo -= 50
            
    ##########################################################################

    ####################### FUNCIONES PONER CONSTRUCCIONES ############################

    def place_town(self, node_coord : int, id_jugador : int) -> bool:
        """
        Función que permite a un jugador poner una ciudad en el tablero
        """
        jugador : Jugador = self.jugadores[self.i_jugador(id_jugador)]
        if not self.board.place_town(jugador.color, node_coord):
            return False
        return True

    def place_road(self, edge_coord : int, id_jugador : int) -> bool:
        """
        Función que permite a un jugador poner una carretera en el tablero
        """
        jugador : Jugador = self.jugadores[self.i_jugador(id_jugador)]
        if not self.board.place_road(jugador.color, edge_coord):
            return False
        return True
    
    def upgrade_town(self, node_coord : int, id_jugador : int) -> bool:
        """
        Función que permite a un jugador poner una ciudad en el tablero
        """
        jugador : Jugador = self.jugadores[self.i_jugador(id_jugador)]
        if not self.board.upgrade_town(jugador.color, node_coord):
            return False
        return True