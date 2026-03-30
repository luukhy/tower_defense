"""This module contains the map implementation for the Dino Defense game"""

import heapq
import random

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem

GRID_SIZE = (80, 80)  # y-width, x-width
TILE_SIZE = 40  # px

MAP_SIZE = (GRID_SIZE[0] * TILE_SIZE, GRID_SIZE[1] * TILE_SIZE)

# TODO: change the TILES to be a dictionary
TILES = ["grass", "sand"]
TILES_WEIGHTS = [6, 1]

TILE_TEXTURES = {"grass": "res/textures/grass.png", "sand": "res/textures/sand.png"}


class Tile(QGraphicsPixmapItem):
    def __init__(self, x: int, y: int, tile_type: str, size: int = TILE_SIZE):
        super().__init__()
        self.setPos(x * size, y * size)
        self.grid_x = x
        self.grid_y = y
        self.texture = QPixmap(TILE_TEXTURES[tile_type]).scaled(TILE_SIZE, TILE_SIZE)
        self.setPixmap(self.texture)
        self.setZValue(-1)
        self.is_walkable = True
        self.is_empty = True
        self.tile_type = tile_type
        self.setAcceptHoverEvents(True)

        self.overlay = QGraphicsRectItem(0, 0, size, size, self)
        self.overlay.setBrush(QColor(200, 200, 200, 100))
        self.overlay.setPen(QPen(Qt.PenStyle.NoPen))
        self.overlay.hide()

    def hoverEnterEvent(self, event):
        if self.is_empty and self.tile_type == "grass":
            self.overlay.show()

    def hoverLeaveEvent(self, event):
        self.overlay.hide()


class GameMap:
    def __init__(self, map_file_path=None):
        if map_file_path:
            self.grid = self.load_from_file(map_file_path)
        else:
            self.grid_size = GRID_SIZE
            self.grid = self.generate_tiles()

    def load_from_file(self, filepath: str) -> list:
        grid = []

        char_to_type = {"G": "grass", "S": "sand"}

        with open(filepath, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        self.grid_size = (len(lines[0]), len(lines))

        global GRID_SIZE, MAP_SIZE
        GRID_SIZE = self.grid_size
        MAP_SIZE = (GRID_SIZE[0] * TILE_SIZE, GRID_SIZE[1] * TILE_SIZE)

        for tile_y, row_str in enumerate(lines):
            grid_row = []
            for tile_x, char in enumerate(row_str):
                tile_type = char_to_type.get(char.upper(), "grass")
                grid_row.append(Tile(tile_x, tile_y, tile_type))
            grid.append(grid_row)

        return grid

    def __iter__(self):
        """Allows iterating over all tiles in a flattened way."""
        for row in self.grid:
            for tile in row:
                yield tile

    def add_to_scene(self, scene):
        for row in self.grid:
            for tile in row:
                scene.addItem(tile)

    def generate_tiles(self) -> list:
        num_tiles = self.grid_size[0] * self.grid_size[1]
        tiles_types = random.choices(TILES, TILES_WEIGHTS, k=num_tiles)
        grid = []
        for tile_y in range(self.grid_size[1]):
            grid_row = []
            for tile_x in range(self.grid_size[0]):
                tile_idx = self.grid_size[0] * tile_y + tile_x
                tile_type = tiles_types[tile_idx]
                grid_row.append(Tile(tile_x, tile_y, tile_type))
            grid.append(grid_row)
        return grid

    def get_walkable_tiles_num(self):
        num = 0
        for tile in self:
            if tile.is_walkable:
                num += 1
        return num

    def get_walkable_tiles(self):
        tiles_walk = []
        for tile in self:
            tiles_walk.append(tile)
        return tiles_walk

    def get_path_a_star(self, start_x, start_y, target_x, target_y):
        """Returns a list of pixel coordinates [(px_x, px_y), ...] from start to target. Using A* Manhattan Distance.
        If no path exists returns an empty list.
        """
        open_set = []
        heapq.heappush(open_set, (0, start_x, start_y))

        came_from = {}
        g_score = {(start_x, start_y): 0}

        def heuristic(x1, y1, x2, y2):
            return abs(x1 - x2) + abs(y1 - y2)

        while open_set:
            _, current_x, current_y = heapq.heappop(open_set)

            if current_x == target_x and current_y == target_y:
                path = []
                curr = (current_x, current_y)
                while curr in came_from:
                    path.append(curr)
                    curr = came_from[curr]
                path.reverse()

                return [(x * TILE_SIZE, y * TILE_SIZE) for x, y in path]

            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                neighbor_x = current_x + dx
                neighbor_y = current_y + dy

                if (
                    0 <= neighbor_x < self.grid_size[0]
                    and 0 <= neighbor_y < self.grid_size[1]
                ):
                    if self.grid[neighbor_y][neighbor_x].is_walkable:
                        tentative_g_score = g_score[(current_x, current_y)] + 1

                        if (
                            neighbor_x,
                            neighbor_y,
                        ) not in g_score or tentative_g_score < g_score[
                            (neighbor_x, neighbor_y)
                        ]:
                            came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                            g_score[(neighbor_x, neighbor_y)] = tentative_g_score

                            f_score = tentative_g_score + heuristic(
                                neighbor_x, neighbor_y, target_x, target_y
                            )
                            heapq.heappush(open_set, (f_score, neighbor_x, neighbor_y))

        # if we exit the loop no path exists
        return []
