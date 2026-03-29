import math
from pathlib import Path

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem

resources_path = Path("res/textures")

towers_textures = {"default": resources_path / Path("tower_default.png")}


class Tower(QGraphicsPixmapItem):
    def __init__(self, grid_y, grid_x, tile_size, type=None):
        super().__init__()
        tex_path = towers_textures["default"]
        self.texture = QPixmap(str(tex_path))

        if self.texture.isNull():
            print(f"Warning: Missing tower texture at {str(tex_path)}")

        self.grid_y = grid_y
        self.grid_x = grid_x

        pos_x = grid_x * tile_size
        pos_y = grid_y * tile_size

        offset_y = self.texture.height() - tile_size

        self.setPos(pos_x, pos_y - offset_y)
        self.setPixmap(self.texture)

        self.setZValue(self.grid_y)

        self.range = 120.0  # radius px
        self.fire_rate = 1.5  # seconds
        self.damage = 25
        self.aoe_radius = 0.0

        self.time_since_last_shot = 0.0

    def udate_logic(self, dt: float, dinos: list):
        self.time_since_last_shot += dt

        if self.time_since_last_shot >= self.fire_rate:
            target = self.find_target(dinos)

            if target:
                self.shoot(target)
                self.time_since_last_shot = 0.0

    def find_target(self, dinos: list):
        """Finds the closest Dino within range."""
        closest_dino = None
        min_distance = self.range

        my_x = self.x()
        my_y = self.y()

        for dino in dinos:
            # Calculate distance using Pythagorean theorem
            dx = dino.exact_x - my_x
            dy = dino.exact_y - my_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist <= min_distance:
                min_distance = dist
                closest_dino = dino

        return closest_dino

    def shoot(self, target):
        """Creates a bullet."""
        print(f"Tower fired at Dino! Target HP: {target.hp}")
        # TODO: Spawning an object
