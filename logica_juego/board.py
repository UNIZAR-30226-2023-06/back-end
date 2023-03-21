import hexgrid
from enum import Enum, auto
import random


class Color(Enum):
  RED = auto()
  BLUE = auto()
  YELLOW = auto()
  GREEN = auto()


class Resource(Enum):
  WOOD = auto()
  CLAY = auto()
  SHEEP = auto()
  STONE = auto()
  WHEAT = auto()
  DESERT = auto()


class Building(Enum):
  VILLAGE = auto()
  CITY = auto()


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


TileType = tuple[int, Resource]
NodeType = tuple[Color | None, Building | None]
EdgeType = Color | None


class Hexgrid:
  # Numbers a tile can hold, TODO, desierto y ladron
  NUMBERS = (
      [2, ] + [3, 4, 5, 6, 7, 8, 9, 10, 11] * 2 + [12, ]
  )  # 0, 1 desierto y ladron?

  def __init__(self, resources: list[Resource]):
    random.shuffle(Hexgrid.NUMBERS)

    # Dict with key=tile coord and value=(number, resource)
    self.tiles: dict[int, TileType] = {
        val: (i, res)
        for val, i, res in zip(
            hexgrid.legal_tile_coords(), Hexgrid.NUMBERS, resources
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

  # TODO: docstrings

  ###################
  # TILE OPERATIONS #
  ###################

  def get_tile_by_id(self, identifier: int) -> TileType:
    if identifier < 1 or identifier > 19:
      raise ValueError("Identifier must range from 1 to 19")

    return self.get_tile_by_coord(hexgrid._tile_id_to_coord[identifier])

  def get_tile_by_coord(self, coord: int) -> TileType:
    if coord not in hexgrid._tile_id_to_coord.values():
      raise ValueError(f"Coord (0x{coord:x}) does not exist")

    return self.tiles[coord]

  # TODO: more? maybe thief?

  ###################
  # NODE OPERATIONS #
  ###################

  # TODO: same but with coord??

  def get_node_coord_by_id(self, tile_identifier: int, direction: NodeDirection) -> int:
    return hexgrid.node_coord_in_direction(
        tile_identifier, direction.value)

  def get_node_by_id(self, tile_identifier: int, direction: NodeDirection) -> NodeType:
    node_coord = self.get_node_coord_by_id(tile_identifier, direction)
    return self.nodes[node_coord]

  def set_node_color_by_id(self, tile_identifier: int, direction: NodeDirection, color: Color):
    if color is None:
      raise ValueError("You cant set node color to None")

    node_coord = self.get_node_coord_by_id(tile_identifier, direction)

    (ncolor, nbuilding) = self.nodes[node_coord]

    if ncolor is not None:
      raise RuntimeError(
        f"Color already exists in node ({tile_identifier}, {direction})")

    self.nodes[node_coord] = (color, nbuilding)

  def set_node_building_by_id(self, tile_identifier: int, direction: NodeDirection, building: Building):
    if building is None:
      raise ValueError("You cant set node building to None")

    node_coord = self.get_node_coord_by_id(tile_identifier, direction)

    (ncolor, nbuilding) = self.nodes[node_coord]

    if nbuilding is not None and nbuilding is Building.CITY:
      raise RuntimeError(
        f"Building at node ({tile_identifier}, {direction}) is already fully upgraded")

    self.nodes[node_coord] = (ncolor, building)

  ###################
  # EDGE OPERATIONS #
  ###################

  # TODO: same but with coord??

  def get_edge_coord_by_id(self, tile_identifier: int, direction: EdgeDirection) -> int:
    return hexgrid.edge_coord_in_direction(
        tile_identifier, direction.value)

  def get_edge_by_id(self, tile_identifier: int, direction: EdgeDirection) -> EdgeType:
    edge_coord = self.get_edge_coord_by_id(tile_identifier, direction)

    return self.edges[edge_coord]

  def set_edge_by_id(self, tile_identifier: int, direction: EdgeDirection, color: Color):
    if color is None:
      raise ValueError("You cant set edge color to None")

    edge_coord = self.get_edge_coord_by_id(tile_identifier, direction)

    if self.edges[edge_coord] is not None:
      raise RuntimeError(
        f"Edge ({tile_identifier}, {direction}) already has color")

    self.edges[edge_coord] = color

  #######################
  # RESOURCE OPERATIONS #
  #######################

  def node_surrounding_resources_by_id(self, identifier: int, direction: NodeDirection) -> list[Resource]:
    node_coord = self.get_node_coord_by_id(identifier, direction)
    return []

#   def surranding_resources(self, position: int):
#     for x in self.__tiles_touching_node(position):
#       print(x)

#   def _tiles_touching_node(self, position: int):
#     for x in hexgrid._tile_node_offsets.keys():
#       print(f"{position - x}")

  ################
  # LONGEST PATH #
  ################


class Board:
  DEFAULT_RES_DISTRIB = (
    [Resource.WOOD,] * 4 + [Resource.WHEAT,] * 4 + [Resource.SHEEP,] * 4 +
    [Resource.STONE,] * 3 + [Resource.CLAY,] * 3 + [Resource.DESERT,]
  )

  def __init__(self, to_assign: list[Resource] | None = None):
    self.board = to_assign if to_assign is not None else Board.DEFAULT_RES_DISTRIB
    random.shuffle(self.board)

    self.thief = random.randrange(0, len(self.board))

#   def place_town(self, color: Color, position: int) -> bool:
#     pass

#   def upgrade_town(self, color: Color, position: int) -> bool:
#     pass

#   def place_road(self, color: Color, posiition: int) -> bool:
#     pass


# b = Board()
h = Hexgrid(Board.DEFAULT_RES_DISTRIB)
# print(len(h.tiles.keys()))
# print(h.get_tile_by_id(11))
# print(h.get_tile_by_coord(0x7B))
