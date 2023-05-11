from typing import Iterable
from functools import reduce
from itertools import combinations
import hexgrid
from hexgrid import *
from enum import Enum, auto
import random

from .render import *

from .constants import Color, Building, Resource

class NodeDirection(Enum):
  N = 'N'
  NW = 'NW'
  SW = 'SW'
  S = 'S'
  SE = 'SE'
  NE = 'NE'


class EdgeDirection(Enum):
  NW = 'NW'
  W = 'W'
  SW = 'SW'
  SE = 'SE'
  E = 'E'
  NE = 'NE'


_tile_node_offsets = {
    # node_coord - tile_coord
    +0x01: NodeDirection.N,
    -0x10: NodeDirection.NW,
    -0x01: NodeDirection.SW,
    +0x10: NodeDirection.S,
    +0x21: NodeDirection.SE,
    +0x12: NodeDirection.NE,
}

_tile_edge_offsets = {
    # edge_coord - tile_coord
    -0x10: EdgeDirection.NW,
    -0x11: EdgeDirection.W,
    -0x01: EdgeDirection.SW,
    +0x10: EdgeDirection.SE,
    +0x11: EdgeDirection.E,
    +0x01: EdgeDirection.NE,
}

_adjacent_nodes_offsets = {
  -0x10: NodeDirection.N,
  -0x11: NodeDirection.SW,
  +0x11: NodeDirection.SE,
}

_node_edge_directions_offsets = { # Must have same identifier
  (NodeDirection.N, EdgeDirection.NW): NodeDirection.NW,
  (NodeDirection.N, EdgeDirection.NE): NodeDirection.NE,
  (NodeDirection.NW, EdgeDirection.NW): NodeDirection.N,
  (NodeDirection.NW, EdgeDirection.W): NodeDirection.SW,
  (NodeDirection.SW, EdgeDirection.W): NodeDirection.NW,
  (NodeDirection.SW, EdgeDirection.SW): NodeDirection.S,
  (NodeDirection.S, EdgeDirection.SW): NodeDirection.SW,
  (NodeDirection.S, EdgeDirection.SE): NodeDirection.SE,
  (NodeDirection.SE, EdgeDirection.SE): NodeDirection.S,
  (NodeDirection.SE, EdgeDirection.E): NodeDirection.NE,
  (NodeDirection.NE, EdgeDirection.E): NodeDirection.SE,
  (NodeDirection.NE, EdgeDirection.NE): NodeDirection.N,
}

_tile_id_to_coord = {
    # 1-19 clockwise starting from Top-Left
    1: 0x37, 12: 0x59, 11: 0x7B,
    2: 0x35, 13: 0x57, 18: 0x79, 10: 0x9B,
    3: 0x33, 14: 0x55, 19: 0x77, 17: 0x99, 9: 0xBB,
    4: 0x53, 15: 0x75, 16: 0x97, 8: 0xB9,
    5: 0x73, 6: 0x95, 7: 0xB7
}

TileType = tuple[int, Resource]
NodeType = tuple[Color | None, Building | None]
EdgeType = Color | None


def inv(d): return {v: k for k, v in d.items()}

def print_hex(it: Iterable[int]):
  print([f"{x:x}" for x in it])

class Hexgrid:
  # Numbers a tile can hold
  NUMBERS = (
    [2, ] + [3, 4, 5, 6, 8, 9, 10, 11] * 2 + [12, ]
  )
  #randomize the order of the numbers
  

  # Note this doesnt add up to 19,
  # we'll add 0 later to
  # represent desert

  def __init__(self, resources: list[Resource], thief: bool | None = None):
    # random.shuffle(resources)  # TODO: make copy?
    # TODO: puede no haber ladron
    # self.thief = random.randrange(
    #   1, len(resources) + 1) if thief is None else thief
    desert_index = resources.index(Resource.DESERT)
    self.thief = desert_index if thief is None or True else None
    random.shuffle(self.NUMBERS)
    numbers = Hexgrid.NUMBERS[:desert_index] + \
        [0, ] + Hexgrid.NUMBERS[desert_index:]

    # Dict with key=tile coord and value=(number, resource) 
    self.tiles: dict[int, TileType] = {
        val: (i, res)
        for val, i, res in zip(
            hexgrid.legal_tile_coords(), numbers, resources
        )
    }


    # Dict with key=node coord and value=(color, building)
    self.nodes: dict[int, NodeType] = {
        val: (None, None) for val in hexgrid.legal_node_coords()
    }

    # Dict with key=edge coord and value=(color)
    self.edges: dict[int, EdgeType] = {
        val: None for val in hexgrid.legal_edge_coords()
    }

    self.__tile_coord2id = {v: k for k, v in hexgrid._tile_id_to_coord.items()}
    for key in self.tiles.keys():
      values = self.tiles.get(key)
      if values[1] == Resource.DESERT:
        self.thief =  self.tile_coord2id(key) if thief is None or True else none
        break

  @property
  def thief_coord(self) -> int:
    return hexgrid._tile_id_to_coord[self.thief]

  @property
  def tile_coord_list(self) -> list[int]:
    return list(self.tiles.keys())

  @property
  def node_coord_list(self) -> list[int]:
    return list(self.nodes.keys())

  @property
  def edge_coord_list(self) -> list[int]:
    return list(self.edges.keys())

  def tile_coord2id(self, coord: int) -> int:
    return self.__tile_coord2id[coord]

  ###################
  # TILE OPERATIONS #
  ###################

  def get_tile_by_id(self, identifier: int) -> TileType:
    """ Returns the tile with the given identifier.

    Args:
        identifier (int): The identifier of the tile to return. Must range from 1 to 19.

    Raises:
        ValueError:  If the identifier is outside the range of valid tile identifiers (1-19).

    Returns:
        TileType: The tile with the given identifier.
    """
    if identifier < 1 or identifier > 19:
      raise ValueError("Identifier must range from 1 to 19")

    return self.get_tile_by_coord(hexgrid._tile_id_to_coord[identifier])

  def get_tile_by_coord(self, coord: int) -> TileType:
    """ Returns the tile with the given coordinate.

    Args:
        coord (int): The coordinate of the tile to return.

    Raises:
        ValueError: If the coordinate does not correspond to a valid tile.

    Returns:
        TileType: The tile at the given coordinate.
    """
    if coord not in hexgrid._tile_id_to_coord.values():
      raise ValueError(f"Coord (0x{coord:x}) does not exist")

    return self.tiles[coord]

  # TODO: more? maybe thief?

  ###################
  # NODE OPERATIONS #
  ###################

  def get_node_coord_by_id(self, tile_identifier: int, direction: NodeDirection) -> int:
    """ Returns the coordinate of the node adjacent to the tile 
        with the given identifier in the specified direction.

    Args:
        tile_identifier (int): The identifier of the tile to start from.
        direction (NodeDirection): The direction of the node to return.

    Returns:
        int: The coordinate of the node in the specified direction from the tile with the given identifier.
    """
    return hexgrid.node_coord_in_direction(
        tile_identifier, direction.value)
  
  def get_nodes_coords_by_id(self, tile_identifier: int) -> list[int]:
    """ Returns the coordinates of the nodes adjacent to the tile 
        with the given identifier.

    Args:
        tile_identifier (int): The identifier of the tile to start from.

    Returns:
        list[int]: The coordinates of the nodes adjacent to the tile with the given identifier.
    """
    return [self.get_node_coord_by_id(tile_identifier, direction) for direction in NodeDirection]

  def get_node_by_id(self, tile_identifier: int, direction: NodeDirection) -> NodeType:
    """ Returns the node adjacent to the tile with the given identifier in the specified direction.

    Args:
        tile_identifier (int): The identifier of the tile to start from.
        direction (NodeDirection): The direction of the node to return.

    Returns:
        NodeType: The node in the specified direction from the tile with the given identifier.
    """
    node_coord = self.get_node_coord_by_id(tile_identifier, direction)
    return self.nodes[node_coord]

  def get_adjacent_nodes_by_node_id(self, node_coord: int) -> list[NodeType]:
    """ Returns the nodes adjacent to the node with the given coordinate.

    Args:
        node_coord (int): The coordinate of the node to start from.

    Returns:
        list[NodeType]: The nodes adjacent to the node with the given coordinate.
    """
    res = []
    if node_coord % 2 == 0: # "upper triangle" form 
      north_node = node_coord - 0x10 + 0x01
      south_west_node = node_coord - 0x11
      south_east_node = node_coord + 0x11
      res.append(north_node)
      res.append(south_west_node)
      res.append(south_east_node)

    else: # "lower triangle" form
      south_node = node_coord + 0x10 - 0x01
      north_west_node = node_coord - 0x11
      north_east_node = node_coord + 0x11
      res.append(south_node)
      res.append(north_west_node)
      res.append(north_east_node)

    return res

  def get_adjacent_edges_by_node_id(self, node_coord: int) -> list[EdgeType]:
    """ Returns the edges adjacent to the node with the given coordinate.

    Args:
        node_coord (int): The coordinate of the node to start from.

    Returns:
        list[EdgeType]: The edges adjacent to the node with the given coordinate.
    """
    res = []
    if node_coord % 2 == 0: # "upper triangle" form
      north_edge = node_coord - 0x10
      south_west_edge = node_coord - 0x11
      south_east_edge = node_coord 
      res.append(north_edge)
      res.append(south_west_edge)
      res.append(south_east_edge)
    
    else: # "lower triangle" form
      south_edge = node_coord - 0x01
      north_west_edge = node_coord - 0x11
      north_east_edge = node_coord 
      res.append(south_edge)
      res.append(north_west_edge)
      res.append(north_east_edge)

    return res


  def get_adjacent_edges_by_edge_id(self, edge_coord: int) -> list[EdgeType]:
    """ Returns the edges adjacent to the node with the given coordinate.

    Args:
        edge_coord (int): The coordinate of the node to start from.

    Returns:
        list[EdgeType]: The edges adjacent to the node with the given coordinate.
    """
    res = []
    #0xYX where Y is even and X is also even
    if int((edge_coord / 0x10) % 2) == 0 and int((edge_coord % 0x10) % 2) == 0:
      north_east_edge = edge_coord + 0x01
      north_west_edge = edge_coord - 0x10
      south_east_edge = edge_coord + 0x10
      south_west_edge = edge_coord - 0x01
      res.append(north_east_edge)
      res.append(north_west_edge)
      res.append(south_east_edge)
      res.append(south_west_edge)
    #0xYX where Y is odd and X is even
    elif int((edge_coord / 0x10) % 2) == 1 and int((edge_coord % 0x10)) % 2 == 0:
      north_east_edge = edge_coord + 0x11
      north_west_edge = edge_coord - 0x10
      south_east_edge = edge_coord + 0x10
      south_west_edge = edge_coord - 0x11
      res.append(north_east_edge)
      res.append(north_west_edge)
      res.append(south_east_edge)
      res.append(south_west_edge)
    #0xYX where Y is even and X is odd
    elif int((edge_coord / 0x10)) % 2 == 0 and int((edge_coord % 0x10)) % 2 == 1:
      north_east_edge = edge_coord + 0x01
      north_west_edge = edge_coord - 0x11
      south_east_edge = edge_coord + 0x11
      south_west_edge = edge_coord - 0x01
      res.append(north_east_edge)
      res.append(north_west_edge)
      res.append(south_east_edge)
      res.append(south_west_edge)

    return res
  
  def get_adjacent_nodes_by_edge_id(self, edge_coord: int) -> list[NodeType]:
    """ Returns the nodes adjacent to the edge with the given coordinate.

    Args:
        edge_coord (int): The coordinate of the edge to start from.

    Returns:
        list[NodeType]: The nodes adjacent to the edge with the given coordinate.
    """
    res = []
    #0xYX where Y is even and X is also even
    if int((edge_coord / 0x10) % 2) == 0 and int((edge_coord % 0x10) % 2) == 0:
      north_node = edge_coord + 0x01
      south_node = edge_coord + 0x10
      res.append(north_node)
      res.append(south_node)
    #0xYX where Y is odd and X is even
    elif int((edge_coord / 0x10) % 2) == 1 and int((edge_coord % 0x10)) % 2 == 0:
      north_node = edge_coord 
      south_node = edge_coord + 0x11
      res.append(north_node)
      res.append(south_node)
    #0xYX where Y is even and X is odd
    elif int((edge_coord / 0x10)) % 2 == 0 and int((edge_coord % 0x10)) % 2 == 1:
      north_node = edge_coord + 0x11
      south_node = edge_coord 
      res.append(north_node)
      res.append(south_node)

    return res
  
  def get_adjacent_tiles_by_node_id(self, node_coord: int) -> list[TileType]:
    """ Returns the tiles adjacent to the node with the given coordinate.

    Args:
        node_coord (int): The coordinate of the node to start from.

    Returns:
        list[TileType]: The tiles adjacent to the node with the given coordinate.
    """
    res = []
    if node_coord % 2 == 1: 
      north_edge = node_coord - 0x10
      south_west_edge = node_coord - 0x12
      south_east_edge = node_coord + 0x10
      res.append(north_edge)
      res.append(south_west_edge)
      res.append(south_east_edge)
    
    else: 
      south_edge = node_coord - 0x01
      north_west_edge = node_coord - 0x21
      north_east_edge = node_coord + 0x01
      res.append(south_edge)
      res.append(north_west_edge)
      res.append(north_east_edge)

    return res

  def set_node_color_by_id(self, tile_identifier: int, direction: NodeDirection, color: Color):
    """ Sets the color of the node adjacent to the tile with the given identifier in the specified direction.

    Args:
        tile_identifier (int): The identifier of the tile to start from.
        direction (NodeDirection): The direction of the node to set the color for.
        color (Color): The color to set for the node.

    Raises:
        ValueError: If color is None.
        RuntimeError: If the node already has a color set.
    """
    if color is None:
      raise ValueError("You cant set node color to None")

    node_coord = self.get_node_coord_by_id(tile_identifier, direction)

    (ncolor, nbuilding) = self.nodes[node_coord]

    if ncolor is not None:
      raise RuntimeError(
        f"Color already exists in node ({tile_identifier}, {direction})")

    self.nodes[node_coord] = (color, nbuilding)

  def set_node_color_by_coord(self, node_coord: int, color: Color):
    """ Sets the color of the node at node_coord.

    Args:
        node_coord (int): coord
        color (Color): The color to set for the node.

    Raises:
        ValueError: If color is None.
        RuntimeError: If the node already has a color set.
    """
    if color is None:
      raise ValueError("You cant set node color to None")

    (ncolor, nbuilding) = self.nodes[node_coord]

    if ncolor is not None:
      raise RuntimeError(
        f"Color already exists in node ({node_coord:x})")

    self.nodes[node_coord] = (color, nbuilding)


  def set_node_building_by_id(self, tile_identifier: int, direction: NodeDirection, building: Building):
    """ Sets the building on the node adjacent to the tile with the given identifier in the specified direction.

    Args:
        tile_identifier (int): The identifier of the tile to start from.
        direction (NodeDirection): The direction of the node to set the building on.
        building (Building): The building to set on the node.

    Raises:
        ValueError: If building is None.
        RuntimeError: If the node already has a city building (i.e., Building.CITY).
    """
    if building is None:
      raise ValueError("You cant set node building to None")

    node_coord = self.get_node_coord_by_id(tile_identifier, direction)

    (ncolor, nbuilding) = self.nodes[node_coord]

    if nbuilding is not None and nbuilding is Building.CITY:
      raise RuntimeError(
        f"Building at node ({tile_identifier}, {direction}) is already fully upgraded")

    self.nodes[node_coord] = (ncolor, building)

  def set_node_building_by_coord(self, node_coord: int, building: Building):
    """ Sets the building on the node coord.

    Args:
        node_coord (int): Coord
        building (Building): The building to set on the node.

    Raises:
        ValueError: If building is None.
        RuntimeError: If the node already has a city building (i.e., Building.CITY).
    """
    if building is None:
      raise ValueError("You cant set node building to None")

    (ncolor, nbuilding) = self.nodes[node_coord]

    if nbuilding is not None and nbuilding is Building.CITY:
      raise RuntimeError(
        f"Building at node ({node_coord:x}) is already fully upgraded")

    self.nodes[node_coord] = (ncolor, building)

  ###################
  # EDGE OPERATIONS #
  ###################

  def get_edge_coord_by_id(self, tile_identifier: int, direction: EdgeDirection) -> int:
    """ Returns the coordinate of the edge adjacent to the tile with the given identifier in the specified direction.

    Args:
        tile_identifier (int): The identifier of the tile to start from.
        direction (EdgeDirection): The direction of the edge to get the coordinate of.

    Returns:
        int: The coordinate of the edge.
    """
    return hexgrid.edge_coord_in_direction(
        tile_identifier, direction.value)

  def get_edge_by_id(self, tile_identifier: int, direction: EdgeDirection) -> EdgeType:
    """ Returns the edge adjacent to the tile with the given identifier in the specified direction.

    Args:
        tile_identifier (int): The identifier of the tile to start from.
        direction (EdgeDirection): The direction of the edge to get.

    Returns:
        EdgeType: Edge
    """
    edge_coord = self.get_edge_coord_by_id(tile_identifier, direction)

    return self.edges[edge_coord]

  def get_edge_by_coord(self, coord: int) -> EdgeType:
    """ Returns the edge given a edge coord.

    Args:
        coord (int): The edge's coord

    Returns:
        EdgeType: Edge
    """

    if (coord not in self.edge_coord_list):
      raise ValueError(f"Edge coord {coord} does not exist")

    return self.edges[coord]

  def set_edge_by_id(self, tile_identifier: int, direction: EdgeDirection, color: Color):
    """ Sets the color of the edge adjacent to the tile with the given identifier in the specified direction.

    Args:
        tile_identifier (int): The identifier of the tile to start from.
        direction (EdgeDirection): The direction of the edge to set.
        color (Color): The color to set for the edge.

    Raises:
        ValueError: If `color` is `None`.
        RuntimeError: If the edge already has a color.
    """
    if color is None:
      raise ValueError("You cant set edge color to None")

    edge_coord = self.get_edge_coord_by_id(tile_identifier, direction)

    if self.edges[edge_coord] is not None:
      raise RuntimeError(
        f"Edge ({tile_identifier}, {direction}) already has color")

    self.edges[edge_coord] = color

  def set_edge_by_coord(self, color: Color, edge_coord: int):
    """ Sets the color of the edge at edge_coord

    Args:
        edge_coord (int): Coord
        color (Color): The color to set for the edge.

    Raises:
        ValueError: If `color` is `None`.
        RuntimeError: If the edge already has a color.
    """
    if color is None:
      raise ValueError("You cant set edge color to None")

    if self.edges[edge_coord] is not None:
      raise RuntimeError(
        f"Edge ({edge_coord:x}) already has color")
    
    #TODO: if road is not being placed next to a city or another road, raise error

    self.edges[edge_coord] = color
  #######################
  # RESOURCE OPERATIONS #
  #######################

  def __tiles_touching_node(self, identifier: int, direction: NodeDirection) -> set[int]:
    """ This is a privete method. No docstring for you 🖕"""
    coord = self.get_node_coord_by_id(identifier, direction)
    directions1, directions2 = ["N", "SE", "SW"], ["S", "NE", "NW"]

    directions = directions1 if direction.value in directions1 else directions2

    return {(coord - offset) for offset, v in hexgrid._tile_node_offsets.items()
            if v in directions}

  def resources_surrounding_node_by_id(self, identifier: int, direction: NodeDirection) -> list[Resource]:
    tile_coords = filter(
      lambda tile_coord: tile_coord in hexgrid.legal_tile_coords(
      ) and tile_coord != self.thief_coord,
      self.__tiles_touching_node(identifier, direction))

    return [self.get_tile_by_coord(tile_coord)[1] for tile_coord in tile_coords]

  ################
  # LONGEST PATH #
  ################

  def __get_edges_touching_node(self, identifier: int, direction: NodeDirection) -> set[int]:
    """ This is a privete method. No docstring for you 🖕"""
    tiles_coord = filter(
      lambda tile_coord: tile_coord in hexgrid.legal_tile_coords(),
      self.__tiles_touching_node(identifier, direction))

    tiles_id = [self.tile_coord2id(coord) for coord in tiles_coord]

    tiles_edges = [set(hexgrid.edges_touching_tile(tile)) for tile in tiles_id]

    intersect_edges = set().union(*[x.intersection(y)
                                    for x, y in combinations(tiles_edges, 2)])

    return intersect_edges
  
  # def __get_nodes_at_edge_ends(self, coord: int) -> tuple[int, int]:
  #   """ Gets the nodes (vertex) at both ends of the edge

  #     Args:
  #       coord (int): Edge's coord

  #     Returns:
  #       tuple[int, int]: Nodes at both ends of the edge
  #   """   
  #   if coord not in hexgrid._edge_node_offsets:
  #     raise pls copilot cook it

  #   return (coord - hexgrid._edge_node_offsets[coord][0], coord - hexgrid._edge_node_offsets[coord][1])

  def __dfs(self, identifier: int, direction: NodeDirection,
            color: Color, path: list[int], explored: list[int] = []) -> int:
    """ This is a privete method. No docstring for you 🖕"""
    VERBOSE = True

    # if self.get_node_coord_by_id(identifier, direction) in explored:
    #   if VERBOSE:
    #     print(f"Already explored {identifier} {direction}")
    #     print("\t-->Explored:", self.get_node_coord_by_id(identifier, direction))
    #   return 0

    # explored.append(self.get_node_coord_by_id(identifier, direction))
    
    # possible roads
    if VERBOSE:
      print("root id:", identifier, direction)
    roads_coords = self.__get_edges_touching_node(identifier, direction) 

    # same color roads
    roads = {road for road in roads_coords if self.get_edge_by_coord(road) == color and road not in explored}

    if VERBOSE:
      #print roads in hex
      print("~~~~~~~~>> roads:", [f"{road:x}" for road in roads])

    if len(roads) == 0:
      if VERBOSE:
        print("No roads")
      return 0

    xchange = { # TODO: change string for enum
      "NW": {
        NodeDirection.NW: NodeDirection.S,
        NodeDirection.N: NodeDirection.SE
      },
      "NE": {
        NodeDirection.N: NodeDirection.SW,
        NodeDirection.NE: NodeDirection.S
      },
      "SW": {
        NodeDirection.SW: NodeDirection.N,
        NodeDirection.S: NodeDirection.NE
      },
      "SE": {
        NodeDirection.S: NodeDirection.NW,
        NodeDirection.SE: NodeDirection.N
      }
    }

    depth = 0
    lst = None
    for road in roads:
      if road in explored:
        if VERBOSE:
          print(f"Already explored {road:x}")
        continue
      node_id, edge_dir = self.__edge_coord_to_id(road)
      if VERBOSE:
        print(f"-> Edge coord: {road:x}")
        print(f"-> node id: {node_id}, dir {edge_dir}")

      for off, dirx in hexgrid._tile_tile_offsets.items(): # iterate through tile-tile offsets
        x = hexgrid.tile_id_to_coord(node_id) - off # 
        y = hexgrid.tile_id_to_coord(identifier)
        if x == y and x != node_id: # 
          if VERBOSE:
            print(f"->> x:y:{y:x}")
            print(f"->> dirx:{dirx}")
          # edge_dir = EdgeDirection(dirx)
          direction = xchange[dirx][direction]
          identifier = node_id
    
      if VERBOSE:
        print("new root id:", identifier, direction)
      next_dir = _node_edge_directions_offsets[(direction, edge_dir)]
      # return (self.get_node_coord_by_id(identifier, next_dir)) Por si acaso test 

      if VERBOSE:
        print(f"explored: {[f'{x:x}' for x in explored]}")

      explored.append(road)
      new_depth = (1 + self.__dfs(identifier, next_dir, color, path, explored)) 
      argmax, depth = max(enumerate([depth, new_depth]), key=lambda x: x[1])
      lst = [lst, self.get_node_coord_by_id(identifier, next_dir)][argmax]
      path.append(lst)
      
      # explored.append(self.get_node_coord_by_id(identifier, edge_dir))
    return depth 


  def longest_path(self, color: Color) -> int:
    # Nodes (buildings) with the given color, does not include roads
    nodes = [coord for coord, (c, _) in self.nodes.items() if c == color]

    if len(nodes) == 0:
      return 0

    # print("nodes")
    # print(f"{nodes[0]:x}")

    # Node's coordenates using identifier and direction
    # Root node
    root_id, root_dir = self.__node_coord_to_id(nodes[0])
    print(f" ****** root id: {root_id}, dir: {root_dir} ******")
    path = [] # creo que ya esta, preguntame cualquiercosa y
              # si esno me dides por whatasapp
    res = self.__dfs(root_id, root_dir, color, path)
    res += self.__dfs(root_id, root_dir, color, [], path)
    return res if res > 0 else 0


    
  def __node_coord_to_id(self, coord: int) -> tuple[int, NodeDirection]:
    # TODO: improve tiles_touching_node
    tile_node_off_inv = inv(_tile_node_offsets)

    tiles_touching_node = [(coord - tile_node_off_inv[d], d) for d in tile_node_off_inv.keys()]
    print(f"tiles touching node: {tiles_touching_node}")
    tiles_touching_node = [(coord, d) for coord, d in tiles_touching_node if coord in hexgrid.legal_tile_coords()]
    print(f"tiles touching node 2222: {tiles_touching_node}")



    if tiles_touching_node == []:
      # TODO: change this
      raise ValueError("THIS SHOULD NOT HAPPEN (no tiles arround node?)")

    coord, direction = tiles_touching_node[0] 
    return self.tile_coord2id(coord), direction #? maybe return a list of possible nodes



  def __edge_coord_to_id(self, coord: int) -> tuple[int, EdgeDirection]:
    tile_edge_off_inv = inv(_tile_edge_offsets)

    tiles_touching_edge = [(coord - tile_edge_off_inv[d], d)
                           for d in tile_edge_off_inv.keys()]
    tiles_touching_edge = [
      (coord, d) for coord, d in tiles_touching_edge if coord in hexgrid.legal_tile_coords()]

    if tiles_touching_edge == []:
      raise ValueError("THIS SHOULD NOT HAPPEN (no tiles arround edge?)")
    
    coord, direction = tiles_touching_edge[0]
    return self.tile_coord2id(coord), direction #? maybe return a list of possible nodes


import math
class Board(Hexgrid):
  DEFAULT_RES_DISTRIB = (
    [Resource.DESERT, ] + [Resource.WOOD, ] * 4 + [Resource.WHEAT, ] * 4 +
    [Resource.SHEEP, ] * 4 + [Resource.STONE, ] * 3 + [Resource.CLAY, ] * 3
  )

  def __init__(self, to_assign: list[Resource] | None = None, thief: bool = True):
    # self.board = to_assign if to_assign is not None else Board.DEFAULT_RES_DISTRIB
    if to_assign is None:
      self.board = Board.DEFAULT_RES_DISTRIB
      random.shuffle(self.board)
    else:
      self.board = to_assign

    super().__init__(resources=self.board, thief=thief)

  # DEBUG / PRINT
  # I SPENT WAAAAY TOO MUCH TIME ON THIS *redacted*
  # This code sucks!
  def svg(self, filename: str):
    resource2color = {
      Resource.CLAY: "#E2725B",
      Resource.DESERT: "#C09A6B",
      Resource.SHEEP: "white",
      Resource.STONE: "#D3D3D3",
      Resource.WHEAT: "#f9f97f",
      Resource.WOOD: "#966F33"
    }

    color2color = {
      Color.BLUE: "blue",
      Color.GREEN: "green",
      Color.RED: "red",
      Color.YELLOW: "yellow",
      None: "purple"
    }

    building2str = {
      Building.CITY: "C",
      Building.VILLAGE: "V",
      None: ""
    }

    node_draw_offsets = [
      (0, -1), (-0.87, -0.5), (-0.87, 0.5),
      (0, 1), (0.87, 0.5), (0.87, -0.5)
    ]

    edge_draw_offsets = [
      (-0.87/2, -0.66), (-0.87, 0), (-0.87/2, 0.87),
      (0.87/2, 0.87), (0.87, 0), (0.87/2, -0.66),
    ]

    with open(filename, "w") as f:

      xoffsets = [3, 2, 1, 2, 3]
      xwidths = [6, 8, 10, 8, 6]
      rowcoords = [0x37, 0x35, 0x33, 0x53, 0x73]
      hexs = []
      depth = 1
      for rowcoord, offset, width in zip(rowcoords, xoffsets, xwidths):  # Iter rows
        for i in range(1, width, 2):  # iter columns
          x, y = (i + offset) * 0.87, depth

          tile_coord = rowcoord + (i - 1) * 0x22 // 2
          tile_id = self.tile_coord2id(tile_coord)
          resource = self.get_tile_by_coord(tile_coord)[1]
          resource_name = str(resource).split(
            '.')[-1] if tile_id != self.thief else "Thief"

          # TODO: eliminar comunes
          nodes_t_tile = hexgrid.nodes_touching_tile(tile_id)
          edges_t_tile = hexgrid.edges_touching_tile(tile_id)

          fnodes_t_tile = [(f"{building2str[b]}_({coord:x})", color2color[c]) for (c, b), coord in
                           ((self.nodes[coord], coord) for coord in nodes_t_tile)]

          fedges_t_tile = [(color2color[c], ("R" if c is not None else f"{coord:x}")) for c, coord in
                           ((self.edges[coord], coord) for coord in edges_t_tile)]

          nodes = [((x + xoff, y + yoff), (b, c)) for (b, c),
                   (xoff, yoff) in zip(fnodes_t_tile, node_draw_offsets)]

          edges = [((x + xoff, y + yoff), (b, c)) for (c, b),
                   (xoff, yoff) in zip(fedges_t_tile, edge_draw_offsets)]

          hexs.append(svg_hexagon(x, y, resource2color[resource]))

          hexs.append(svg_text(x, y + 0.3 / 2, f"{resource_name}({tile_coord:x})",
                               color="black", font_size=0.3))

          hexs.extend([svg_text(x, y + 0.25 / 2, text, color, font_size=0.25)
                      for (x, y), (text, color) in nodes])
          hexs.extend([svg_text(x, y, text, color, font_size=0.25)
                      for (x, y), (text, color) in edges])

          # hexs.extend([svg_rect(5, 5, 1, 0.2, angle=i, color="black")
          #             for i in range(360)])

        depth += 1.5

      # x = 5
      # y = 5
      # for degree in range(360):
      #   hexs.append(svg_rect(x, y, 1, 0.4, angle=degree, color="black"))

      f.write(svg_hexgrid(hexs))

  def place_town(self, color: Color, position: int) -> bool:
    try:
      if position in self.legal_building_nodes_second_phase(color):
        self.set_node_building_by_coord(position, Building.VILLAGE)
        self.set_node_color_by_coord(position, color)
        return True
      else: return False
    except Exception:
      return False
    
  def place_townV2(self, color: Color, position: int) -> bool:
    try:
      if position in self.legal_building_nodes(color):
        self.set_node_building_by_coord(position, Building.VILLAGE)
        self.set_node_color_by_coord(position, color)
        return True
      else: return False
    except Exception:
      return False
    

  def upgrade_town(self, position: int) -> bool:
    try:
      self.set_node_building_by_coord(position, Building.CITY)
      return True
    except Exception:
      return False

  def place_road(self, color: Color, position: int) -> bool:
    try:
      if position in self.legal_building_edges(color):
        self.set_edge_by_coord(color, position)
        return True
      else: return False
    except Exception as e:
      print(e)
      return False
    
  def move_thief(self, position: int) -> bool:
    try:
      self.thief = self.tile_coord2id(position)
      return True
    except Exception:
      return False
    
  def legal_building_nodes(self, color: Color) -> list[int]:
    uncolored_nodes = [coord for coord, (c, b) in self.nodes.items() if c is None]
    ilegal_nodes = []
    #check that all adjacent nodes are not colored
    for coord in uncolored_nodes:
      adjacent_nodes = self.get_adjacent_nodes_by_node_id(coord)
      adjacent_nodes = [node for node in adjacent_nodes if node in legal_node_coords()]
      if any([self.nodes[node][0] is not None for node in adjacent_nodes]):
        ilegal_nodes.append(coord)
      else:
        adjacent_edges = self.get_adjacent_edges_by_node_id(coord)
        adjacent_edges = [edge for edge in adjacent_edges if edge in legal_edge_coords()]
        if any([self.edges[edge] is not None and self.edges[edge] != color for edge in adjacent_edges]):
          ilegal_nodes.append(coord)
        
    return [coord for coord in uncolored_nodes if coord not in ilegal_nodes]
        
  #returns the legal nodes in which a village can be placed in the second phase of the game (next to a road)
  def legal_building_nodes_second_phase(self, color: Color) -> list[int]:
    uncolored_nodes = [coord for coord, (c, b) in self.nodes.items() if c is None]
    #check that all adjacent nodes are not colored
    ilegal_nodes = []
    for coord in uncolored_nodes:
      adjacent_nodes = self.get_adjacent_nodes_by_node_id(coord)
      adjacent_nodes = [node for node in adjacent_nodes if node in legal_node_coords()]
      adjacent_edges = self.get_adjacent_edges_by_node_id(coord)
      adjacent_edges = [edge for edge in adjacent_edges if edge in legal_edge_coords()]

      if any([self.nodes[node][0] is not None for node in adjacent_nodes]):
        ilegal_nodes.append(coord)
      elif any([self.edges[edge] is not None and self.edges[edge] != color for edge in adjacent_edges]):
        ilegal_nodes.append(coord)
      elif all([self.edges[edge] is None for edge in adjacent_edges]):
        ilegal_nodes.append(coord)

    return [coord for coord in uncolored_nodes if coord not in ilegal_nodes]

  # a road can be placed if there is a road of the same color adjacent to it or if there is a town of the same color adjacent to it
  def legal_building_edges(self, color: Color) -> list[int]:
    uncolored_edges = [coord for coord, c in self.edges.items() if c is None]
    legal_edges = []
    #check that all adjacent edges are not colored
    for coord in uncolored_edges:
      adjacent_edges = self.get_adjacent_edges_by_edge_id(coord)
      adjacent_edges = [edge for edge in adjacent_edges if edge in legal_edge_coords()]
      if any([self.edges[edge] is not None and self.edges[edge] == color for edge in adjacent_edges]):
        legal_edges.append(coord)
      else:
        adjacent_nodes = self.get_adjacent_nodes_by_edge_id(coord)
        adjacent_nodes = [node for node in adjacent_nodes if node in legal_node_coords()]
        if any([self.nodes[node][0] is not None and self.nodes[node][0] == color for node in adjacent_nodes]):
          legal_edges.append(coord)
        
    return legal_edges
  
  def return_resources(self, color: Color, dice: int) -> list[Resource]:
    resources = [0,0,0,0,0] #{CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
    # nodes of the "color" color
    nodes = [coord for coord, (c, b) in self.nodes.items() if c == color]
    for n in nodes:
      surrounding_tiles = self.get_adjacent_tiles_by_node_id(n)
      surrounding_tiles = [tile for tile in surrounding_tiles if tile in legal_tile_coords() and tile != self.thief_coord]
      print(f"surrounding tiles: {surrounding_tiles}")
      for t in surrounding_tiles:
        print(f"TILES DIAVOLIKAS --> {self.tiles[t]}")
        if self.tiles[t][0] == dice and self.tile_coord2id(t) != self.thief:
          if self.tiles[t][1] == Resource.CLAY:
            print("clay")
            resources[0] += 1
          elif self.tiles[t][1] == Resource.WOOD:
            print("wood")
            resources[1] += 1
          elif self.tiles[t][1] == Resource.SHEEP:
            print("sheep")
            resources[2] += 1
          elif self.tiles[t][1] == Resource.STONE:
            print("stone")
            resources[3] += 1
          elif self.tiles[t][1] == Resource.WHEAT:
            print("wheat")
            resources[4] += 1
          else:
            print(f"tile0: {self.tiles[t][0]} tile1: {self.tiles[t][1]}")
            print("nothing")
          #resources.append(self.tiles[t][1])
          # if the tile is a city, append the resource again
          if self.nodes[n][1] == Building.CITY:
            if self.tiles[t][1] == Resource.CLAY:
              resources[0] += 1
            elif self.tiles[t][1] == Resource.WOOD:
              resources[1] += 1
            elif self.tiles[t][1] == Resource.SHEEP:
              resources[2] += 1
            elif self.tiles[t][1] == Resource.STONE:
              resources[3] += 1
            elif self.tiles[t][1] == Resource.WHEAT:
              resources[4] += 1
            #resources.append(self.tiles[t][1])

    print(f"resources: {resources} to player {color}")
    return resources
  
  def return_resources_from_1_coord(self, color: Color, node_coord: int):
    resources = [0,0,0,0,0] #{CLAY:int, WOOD:int, SHEEP:int, STONE:int, WHEAT:int}
    # nodes of the "color" color
    print("COORD DIAVOLIKAS --> ", node_coord)
    nodes = [coord for coord, (c, b) in self.nodes.items() if c == color and coord == node_coord]
    cosa =  [coord for coord, (c, b) in self.nodes.items() if c == color]
    print("JODEEEER --> ", cosa)
    print("NODES DIAVOLIKAS --> ", nodes)
    for n in nodes:
      surrounding_tiles = self.get_adjacent_tiles_by_node_id(n)
      surrounding_tiles = [tile for tile in surrounding_tiles if tile in legal_tile_coords() and tile != self.thief_coord]
      print(f"surrounding tiles: {surrounding_tiles}")
      for t in surrounding_tiles:
        print(f"TILES DIAVOLIKAS --> {self.tiles[t]}")
        if self.tiles[t][1] == Resource.CLAY:
          print("clay")
          resources[0] += 1
        elif self.tiles[t][1] == Resource.WOOD:
          print("wood")
          resources[1] += 1
        elif self.tiles[t][1] == Resource.SHEEP:
          print("sheep")
          resources[2] += 1
        elif self.tiles[t][1] == Resource.STONE:
          print("stone")
          resources[3] += 1
        elif self.tiles[t][1] == Resource.WHEAT:
          print("wheat")
          resources[4] += 1
        else:
          print(f"tile0: {self.tiles[t][0]} tile1: {self.tiles[t][1]}")
          print("nothing")
        #resources.append(self.tiles[t][1])
        # if the tile is a city, append the resource again
        if self.nodes[n][1] == Building.CITY:
          if self.tiles[t][1] == Resource.CLAY:
            resources[0] += 1
          elif self.tiles[t][1] == Resource.WOOD:
            resources[1] += 1
          elif self.tiles[t][1] == Resource.SHEEP:
            resources[2] += 1
          elif self.tiles[t][1] == Resource.STONE:
            resources[3] += 1
          elif self.tiles[t][1] == Resource.WHEAT:
            resources[4] += 1
          #resources.append(self.tiles[t][1])

    return resources     