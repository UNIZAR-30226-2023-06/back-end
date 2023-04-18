from functools import reduce
from itertools import combinations
import hexgrid
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


TileType = tuple[int, Resource]
NodeType = tuple[Color | None, Building | None]
EdgeType = Color | None


def inv(d): return {v: k for k, v in d.items()}


class Hexgrid:
  # Numbers a tile can hold
  NUMBERS = (
    [2, ] + [3, 4, 5, 6, 8, 9, 10, 11] * 2 + [12, ]
  )
  # Note this doesnt add up to 19,
  # we'll add 0 later to
  # represent desert

  def __init__(self, resources: list[Resource], thief: int | None = None):
    random.shuffle(resources)  # TODO: make copy?
    # TODO: puede no haber ladron
    self.thief = random.randrange(
      1, len(resources) + 1) if thief is None else thief

    desert_index = resources.index(Resource.DESERT)
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

  def __edges_touching_node(self, identifier: int, direction: NodeDirection) -> set[int]:
    """ This is a privete method. No docstring for you 🖕"""
    tiles_coord = filter(
      lambda tile_coord: tile_coord in hexgrid.legal_tile_coords(),
      self.__tiles_touching_node(identifier, direction))

    tiles_id = [self.tile_coord2id(coord) for coord in tiles_coord]

    tiles_edges = [set(hexgrid.edges_touching_tile(tile)) for tile in tiles_id]

    intersect_edges = set().union(*[x.intersection(y)
                                    for x, y in combinations(tiles_edges, 2)])

    return intersect_edges

  def __bfs(self, node: int, color: Color, n: int) -> int:
    """ This is a privete method. No docstring for you 🖕"""
    return -1

  def longest_path(self, color: Color) -> int:
    nodes = [coord for coord, (c, _) in self.nodes.items() if c == color]

    if len(nodes) == 0:
      raise ValueError(f"No hay nodos con color {color} en el tablero")

    print("nodes")
    print(f"{nodes[0]:x}")

    a = self.__node_coord_to_id(nodes[0])
    print(a)


    return -1

  def __node_coord_to_id(self, coord: int) -> tuple[int, NodeDirection]:
    # TODO: improve tiles_touching_node
    tile_node_off_inv = inv(_tile_node_offsets)

    tiles_touching_node = [(coord - tile_node_off_inv[d], d)
                           for d in tile_node_off_inv.keys()]
    tiles_touching_node = [
      (coord, d) for coord, d in tiles_touching_node if coord in hexgrid.legal_tile_coords()]

    if tiles_touching_node == []:
      # TODO: change this
      raise ValueError("THIS SHOULD NOT HAPPEN (no tiles arround node?)")

    return tiles_touching_node[0]


import math
class Board(Hexgrid):
  DEFAULT_RES_DISTRIB = (
    [Resource.DESERT, ] + [Resource.WOOD, ] * 4 + [Resource.WHEAT, ] * 4 +
    [Resource.SHEEP, ] * 4 + [Resource.STONE, ] * 3 + [Resource.CLAY, ] * 3
  )

  def __init__(self, to_assign: list[Resource] | None = None):
    self.board = to_assign if to_assign is not None else Board.DEFAULT_RES_DISTRIB
    random.shuffle(self.board)

    super().__init__(self.board)

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
      self.set_node_building_by_coord(position, Building.VILLAGE)
      self.set_node_color_by_coord(position, color)
      return True
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
      self.set_edge_by_coord(color, position)
      return True
    except Exception as e:
      print(e)
      return False
    
  def move_thief(self, position: int) -> bool:
    try:
      self.thief = self.tile_coord2id(position)
      return True
    except Exception:
      return False
