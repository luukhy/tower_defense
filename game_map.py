"""This module contains the map implementation for the Dino Defense game"""

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
        self.x_grid = x
        self.y_grid = y
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

    def set_emptiness(self, val: bool):
        self.is_empty = val

    def set_walkability(self, val: bool):
        self.is_walkable = val


class GameMap:
    def __init__(self):
        self.grid_size = GRID_SIZE
        self.grid = self.generate_map()

    def __iter__(self):
        """Allows iterating over all tiles in a flattened way."""
        for row in self.grid:
            for tile in row:
                yield tile

    def add_to_scene(self, scene):
        for row in self.grid:
            for tile in row:
                scene.addItem(tile)

    def generate_map(self):
        tiles = self.generate_tiles()
        return tiles

    def generate_tiles(self) -> list:
        num_tiles = self.grid_size[0] * self.grid_size[1]
        tiles_types = random.choices(TILES, TILES_WEIGHTS, k=num_tiles)
        # TODO: make the generation so that it creates "biomes"
        grid = []
        for tile_y in range(self.grid_size[1]):
            grid_row = []
            for tile_x in range(self.grid_size[0]):
                tile_idx = TILE_SIZE * tile_y + tile_x
                tile_type = tiles_types[tile_idx]
                grid_row.append(
                    Tile(
                        tile_x,
                        tile_y,
                        tile_type,
                    )
                )
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
