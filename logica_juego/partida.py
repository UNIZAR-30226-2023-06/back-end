import random
import hexgrid
# import cartas
# import construcciones
from .jugador import Jugador
from logica_juego.board import Board, NodeDirection
# import errores

from .constants import Errors, Color, Cards, Building, Resource, TurnPhase, pick_random_card

## COSAS DE LOS TURNOS ##
#counter = 0

class Partida:

    jugadores: list[Jugador] = []
    num_jugadores: int = 4
    num_jugadores_activos: int = 0
    turno: int = 0
    fase_turno: TurnPhase = TurnPhase.RESOURCE_PRODUCTION
    tiempo_turno: int = 60
    jugadores_seleccionados: int = 0
    hay_ladron: bool = True
    board: Board = Board()

    initial_buildings_done: bool = False

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

        self.initial_buildings_done = False
        self.__counter = 0
        self.initial_turns = []
        i = 0
        while i < len(self.jugadores):
            self.initial_turns.append(i)
            i += 1
        i = len(self.jugadores) - 1 
        while i > 0:
            self.initial_turns.append(i)
            i -= 1

        if tablero is not None:
            self.board = tablero
        else:
            self.board = Board() # TODO lo del ladron

    ################ FUNCIONES SOBRE LA GESTIÓN DE JUGADORES ################

    def get_fase_turno(self) -> TurnPhase:
        return self.fase_turno
    
    def get_turno(self) -> int:
        return self.turno
    
    def get_jugador(self, i:int) -> Jugador:
        return self.jugadores[i]
    
    def get_tiempo_turno(self) -> int:
        return self.tiempo_turno
    
    def get_hay_ladron(self) -> bool:
        return self.hay_ladron
    
    def get_board(self) -> Board:
        return self.board

    # Defines whether the player is "active" or not. True if the player is active, False otherwise.
    def set_player_status(self, id_jugador : int, status : bool):
        for jugador in self.jugadores:
            if jugador.get_id() == id_jugador:
                jugador.activo = status
                if status == False: self.num_jugadores_activos -= 1
                else: self.num_jugadores_activos += 1
                break

    def actualizar_initial_turns(self):
        self.initial_turns = []
        i = 0
        while i < len(self.jugadores):
            self.initial_turns.append(i)
            i += 1
        i = len(self.jugadores) - 1 
        while i > 0:
            self.initial_turns.append(i)
            i -= 1

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

        i = 0
        self.initial_turns = []
        while i < len(self.jugadores):
            self.initial_turns.append(i)
            i += 1
        i = len(self.jugadores) - 1 
        while i > 0:
            self.initial_turns.append(i)
            i -= 1

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

        # Comprobamos que los jugadores tienen los recursos que quieren intercambiar
        if self.jugadores[j1].mano.arcilla < recursos_1[0] or self.jugadores[j1].mano.madera < recursos_1[1] or self.jugadores[j1].mano.oveja < recursos_1[2] or self.jugadores[j1].mano.piedra < recursos_1[3] or self.jugadores[j1].mano.trigo < recursos_1[4]:
            raise Exception("El jugador 1 no tiene los recursos que quiere intercambiar")

        if self.jugadores[j2].mano.arcilla < recursos_2[0] or self.jugadores[j2].mano.madera < recursos_2[1] or self.jugadores[j2].mano.oveja < recursos_2[2] or self.jugadores[j2].mano.piedra < recursos_2[3] or self.jugadores[j2].mano.trigo < recursos_2[4]:
            raise Exception("El jugador 2 no tiene los recursos que quiere intercambiar")

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
    
    def asignacion_recursos_a_jugador(self, id_jugador: int, coord:int):
        jugador = self.jugadores[self.i_jugador(id_jugador)]
        recursos = self.board.return_resources_from_1_coord(jugador.color, coord)
        print("recursos: ", recursos)
        jugador.sumar_recursos(recursos)

        return recursos
        

    def usar_carta_caballero(self, id_jugador:int, id_jugador_robado: int, coord: int):
        if self.fase_turno != TurnPhase.RESOURCE_PRODUCTION:
            raise Exception("No se pueden usar cartas de caballero en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador:
            raise Exception("No es el turno del jugador")

        index_jugador = self.i_jugador(id_jugador)
        jugador = self.jugadores[index_jugador]

        # Comprobamos que el jugador tiene la carta de desarrollo
        if jugador.tiene_carta_desarrollo(Cards.KNIGHT):
            jugador.sub_carta_desarrollo(Cards.KNIGHT)
        else:
            raise Exception("El jugador no tiene la carta de desarrollo")

        try:
            self.mover_ladron(coord, id_jugador, id_jugador_robado)
            self.jugadores[self.i_jugador(id_jugador)].add_caballero()
            self.check_bono_caballeros(self.jugadores[self.i_jugador(id_jugador)])
        except Exception as e:
            raise e

    def usar_carta_invention_progress(self, id_jugador: int, recurso1: Resource, recurso2: Resource):
        if self.fase_turno != TurnPhase.BUILDING:
            raise Exception("No se puede usar una carta de desarrollo en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador:
            raise Exception("No es el turno del jugador")

        index_jugador = self.i_jugador(id_jugador)
        jugador = self.jugadores[index_jugador]

        # Comprobamos que el jugador tiene la carta de desarrollo
        if jugador.tiene_carta_desarrollo(Cards.INVENTION_PROGRESS):
            jugador.sub_carta_desarrollo(Cards.INVENTION_PROGRESS)
        else:
            raise Exception("El jugador no tiene la carta de desarrollo")
    
        # añaadimos los recursos al jugador
        jugador.mano.add_recurso(recurso1, 1)
        jugador.mano.add_recurso(recurso2, 1)

    def usar_carta_road_progress(self, id_jugador: int, coords: int):
        if self.fase_turno != TurnPhase.BUILDING:
            raise Exception("No se puede usar una carta de desarrollo en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador:
            raise Exception("No es el turno del jugador")

        index_jugador = self.i_jugador(id_jugador)
        jugador = self.jugadores[index_jugador]

        # Comprobamos que el jugador tiene la carta de desarrollo
        if jugador.tiene_carta_desarrollo(Cards.ROAD_PROGRESS):
            jugador.sub_carta_desarrollo(Cards.ROAD_PROGRESS)
        else:
            raise Exception("El jugador no tiene la carta de desarrollo")

        # Indicamos al tablero dónde construimos las carreteras
        if not self.board.place_road(jugador.color, coords):
            raise Exception("No se puede construir la carretera")
        
    def usar_carta_monopoly_progress(self, id_jugador: int, tipo_recurso: Resource):
        if self.fase_turno != TurnPhase.BUILDING:
            raise Exception("No se puede usar una carta de desarrollo en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador:
            raise Exception("No es el turno del jugador")

        index_jugador = self.i_jugador(id_jugador)
        jugador = self.jugadores[index_jugador]

        # Comprobamos que el jugador tiene la carta de desarrollo
        if jugador.tiene_carta_desarrollo(Cards.MONOPOLY_PROGRESS):
            jugador.sub_carta_desarrollo(Cards.MONOPOLY_PROGRESS)
        else:
            raise Exception("El jugador no tiene la carta de desarrollo")

        for j in self.jugadores:
            if j.get_id() != id_jugador:
                cartas_robadas = j.robar_monopolio(tipo_recurso)
                jugador.mano.add_recurso(tipo_recurso, cartas_robadas)
        
    def usar_carta_victory_progress(self, id_jugador: int):
        if self.fase_turno != TurnPhase.BUILDING:
            raise Exception("No se puede usar una carta de desarrollo en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador:
            raise Exception("No es el turno del jugador")

        index_jugador = self.i_jugador(id_jugador)
        jugador = self.jugadores[index_jugador]

        # Comprobamos que el jugador tiene la carta de desarrollo
        if jugador.tiene_carta_desarrollo(Cards.TOWN_HALL):
            jugador.sub_carta_desarrollo(Cards.TOWN_HALL)
        elif jugador.tiene_carta_desarrollo(Cards.LIBRARY):
            jugador.sub_carta_desarrollo(Cards.LIBRARY)
        elif jugador.tiene_carta_desarrollo(Cards.MARKET):
            jugador.sub_carta_desarrollo(Cards.MARKET)
        elif jugador.tiene_carta_desarrollo(Cards.CHURCH):
            jugador.sub_carta_desarrollo(Cards.CHURCH)
        elif jugador.tiene_carta_desarrollo(Cards.UNIVERSITY):
            jugador.sub_carta_desarrollo(Cards.UNIVERSITY)
        else:
            raise Exception("El jugador no tiene la carta de desarrollo")

        # Añadimos un punto de victoria al jugador
        jugador.add_puntos_victoria(1)

    # El jugador con el id pasado cambia X cantidad de sus recursos_1 por una
    # unidad del recurso_2
    def intercambiar_banca(self, id_jugador:int, tipo_recurso_1:Resource, cantidad_recurso:int, tipo_recurso_2:Resource):
        
        if self.fase_turno != TurnPhase.TRADING:
            raise Exception("No se pueden intercambiar recursos en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador:
            raise Exception("No es el turno del jugador")

        recursos_1 = [0,0,0,0,0] # {CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
        index = None
        if tipo_recurso_1 == Resource.CLAY: index = 0
        elif tipo_recurso_1 == Resource.WOOD: index = 1
        elif tipo_recurso_1 == Resource.SHEEP: index = 2
        elif tipo_recurso_1 == Resource.STONE: index = 3
        elif tipo_recurso_1 == Resource.WHEAT: index = 4

        recursos_1[index] = cantidad_recurso

        recursos_2 = [0,0,0,0,0] # {CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
        if tipo_recurso_2 == Resource.CLAY: index = 0
        elif tipo_recurso_2 == Resource.WOOD: index = 1
        elif tipo_recurso_2 == Resource.SHEEP: index = 2
        elif tipo_recurso_2 == Resource.STONE: index = 3
        elif tipo_recurso_2 == Resource.WHEAT: index = 4

        recursos_2[index] = 1

        j = self.i_jugador(id_jugador)

        if not self.jugadores[j].restar_recursos(recursos_1):
            raise Exception("El jugador no tiene los recursos que quiere intercambiar")
        self.jugadores[j].sumar_recursos(recursos_2)
    
    ##########################################################################
    
    ################# FUNCIONES SOBRE LA GESTIÓN DEL LADRÓN #################

    def mover_ladron(self, tileCoord:int, id_jugador:int, id_jugador_robado:int):
        # Movemos el ladrón a la posición indicada en el tablero
        jugador = self.jugadores[self.i_jugador(id_jugador)]
        jugador_robado = self.jugadores[self.i_jugador(id_jugador_robado)]

        if self.hay_ladron == False:
            raise Exception("Error: No hay ladrón en la partida")

        nodes_around_thief = []
        possible_directions : NodeDirection = {NodeDirection.N, NodeDirection.NE, NodeDirection.SE, NodeDirection.S, NodeDirection.SW, NodeDirection.NW}
        for direction in possible_directions:
            tile_id = self.board.tile_coord2id(tileCoord)
            node = self.board.get_node_by_id(tile_id, direction)
            if node != None:
                nodes_around_thief.append(node)
        possible_nodes = []
        for node in nodes_around_thief:
            if self.board.nodes[node] == (jugador_robado.color, Building.VILLAGE) or self.board.nodes[node] == (jugador_robado.color, Building.CITY):
                possible_nodes.append(node)
        if len(possible_nodes) == 0:
            raise Exception("Error: No hay ningún edificio del jugador robado en los nodos adyacentes al ladrón")
        if tileCoord in hexgrid.legal_node_coords():
            self.board.thief = tileCoord
            self.robar_recursos(id_jugador, id_jugador_robado)
        else:
            raise Exception("Error: La coordenada del ladrón no es válida")

    # especificamos si queremos que haya un ladrón en la partida
    def set_ladron(self, hay_ladron:bool):
        self.hay_ladron = hay_ladron
    
    ##########################################################################
    
    ################ FUNCIONES SOBRE LA GESTIÓN DE LOS TURNOS ################
    
    # Se pasa a la siguiente fase del turno actual, y se pasa al siguiente turno
    # si el actual ya ha acabado
    
    def avanzar_fase(self):
        
        if self.fase_turno == TurnPhase.INITIAL_TURN1:
            self.turno = self.initial_turns.pop()
            self.__counter += 1
            if self.__counter == len(self.jugadores):
                self.fase_turno = TurnPhase.INITIAL_TURN2
                #self.asignacion_recursos_a_jugador(self.jugadores[self.turno].id)
                self.__counter = 0
        elif self.fase_turno == TurnPhase.INITIAL_TURN2:
            if self.__counter < len(self.jugadores):
                self.turno = self.initial_turns.pop() if len(self.initial_turns) > 0 else 0
                #self.asignacion_recursos_a_jugador(self.jugadores[self.turno].id)
            self.__counter += 1
            if self.__counter == len(self.jugadores):
                self.fase_turno = TurnPhase.RESOURCE_PRODUCTION
                self.__counter = 0
        elif self.fase_turno == TurnPhase.RESOURCE_PRODUCTION:
            self.fase_turno = TurnPhase.TRADING
        elif self.fase_turno == TurnPhase.TRADING:
            self.fase_turno = TurnPhase.BUILDING
        elif self.fase_turno == TurnPhase.BUILDING:
            self.fase_turno = TurnPhase.RESOURCE_PRODUCTION
            self.turno = (self.turno + 1) % len(self.jugadores)

    # Establecemos el tiempo de duración de los turnos en segundos
    def set_tiempo_turno(self, tiempo_turno:int):
        self.tiempo_turno = tiempo_turno

    
    
    ##########################################################################
    
    ############ FUNCIONES SOBRE LA GESTIÓN DE LAS CONSTRUCCIONES ############

    def comprar_y_construir(self, id_jugador:int, tipo_construccion:Building, coord:int):
        
        if self.fase_turno != TurnPhase.BUILDING:
            raise Exception("No se pueden construir edificios en esta fase del turno")
        if self.jugadores[self.turno].get_id() != id_jugador:
            raise Exception("No es el turno del jugador")
        
        player : Jugador = self.jugadores[self.i_jugador(id_jugador)]
        if tipo_construccion == Building.ROAD:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos([1,1,0,0,0]): # Si no tiene los recursos suficientes
                raise Exception("Error: No tienes los recursos suficientes para construir la carretera")

            if self.board.place_road(player.color, coord):
                self.check_bono_caballeros(self.jugadores[self.i_jugador(id_jugador)])
            else:
                raise Exception("Error: No se ha podido construir la carretera")

        elif tipo_construccion == Building.VILLAGE:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos([1,1,1,0,1]): # Si no tiene los recursos suficientes
                raise Exception("Error: No tienes los recursos suficientes para construir el poblado")

            if self.board.place_town(player.color, coord):
                self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()
            else:
                raise Exception("Error: No se ha podido construir el poblado")

        elif tipo_construccion == Building.CITY:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos([0,0,0,3,2]):
                raise Exception("Error: No tienes los recursos suficientes para construir la ciudad")

            if self.board.upgrade_town(coord):
                self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()
            else:
                raise Exception("Error: No se ha podido construir la ciudad")

        elif tipo_construccion == Building.DEV_CARD:
            if not self.jugadores[self.i_jugador(id_jugador)].restar_recursos([0,0,1,1,1]): # Si no tiene los recursos suficientes
                raise Exception("Error: No tienes los recursos suficientes para comprar la carta de desarrollo")
            carta_robada = pick_random_card()
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

        print("INDICE JUGADOR: ", self.i_jugador(id_jugador))
        jugador : Jugador = self.jugadores[self.i_jugador(id_jugador)]
        if not self.board.place_townV2(jugador.color, node_coord):
            return False
        self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()
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
        self.jugadores[self.i_jugador(id_jugador)].add_puntos_victoria()
        return True