import math
from pathlib import Path

from PyQt6.QtGui import QColor, QPen, QPixmap
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsPixmapItem

from entities.projectile import Projectile

resources_path = Path("res/textures")

towers_textures = {"default": resources_path / Path("tower_default.png")}


class Tower(QGraphicsPixmapItem):
    def __init__(self, grid_y, grid_x, tile_size, type=None):
        super().__init__()
        self.tile_size = tile_size
        tex_path = towers_textures["default"]
        self.texture = QPixmap(str(tex_path))

        if self.texture.isNull():
            print(f"Warning: Missing tower texture at {str(tex_path)}")

        self.grid_y = grid_y
        self.grid_x = grid_x

        self.exact_x = grid_x * tile_size
        self.exact_y = grid_y * tile_size

        offset_y = self.texture.height() - tile_size

        self.setPos(self.exact_x, self.exact_y - offset_y)
        self.setPixmap(self.texture)

        self.setZValue(self.grid_y)

        # stats
        self.range = 240.0  # radius px
        self.fire_rate = 0.1  # seconds
        self.damage = 25
        self.aoe_radius = 40

        self.time_since_last_shot = 0.0

        self.center_x = self.exact_x + self.texture.width() / 2
        self.center_y = self.exact_y + tile_size / 2

        self.local_center_x = self.texture.width() / 2
        self.local_center_y = self.texture.height() - self.tile_size / 2

        diameter = self.range * 2
        top_left_x = self.local_center_x - self.range
        top_left_y = self.local_center_y - self.range

        self.range_circle = QGraphicsEllipseItem(
            top_left_x, top_left_y, diameter, diameter, self
        )

        self.range_circle.setBrush(QColor(150, 150, 150, 100))
        self.range_circle.setPen(QPen(QColor(255, 255, 255, 150)))

        self.range_circle.setZValue(-1)

        self.setAcceptHoverEvents(True)
        self.range_circle.hide()

    def hoverEnterEvent(self, event):
        self.range_circle.show()

    def hoverLeaveEvent(self, event):
        self.range_circle.hide()

    def update_logic(self, dt: float, dinos: list):
        self.time_since_last_shot += dt

        if self.time_since_last_shot >= self.fire_rate:
            target = self.find_target(dinos)

            if target:
                self.time_since_last_shot = 0.0
                return self.shoot(target)

        return None

    def find_target(self, dinos: list):
        """Finds the closest Dino within range."""
        closest_dino = None
        min_distance = self.range

        my_x = self.center_x
        my_y = self.center_y

        for dino in dinos:
            dx = dino.exact_x - my_x
            dy = dino.exact_y - my_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist <= min_distance:
                min_distance = dist
                closest_dino = dino

        return closest_dino

    def shoot(self, target):
        """Creates and returns a bullet aimed at the ground."""
        spawn_x = self.center_x
        spawn_y = self.center_y - (self.texture.height() / 2)

        target_ground_x = target.exact_x + 20
        target_ground_y = target.exact_y + 20

        new_bullet = Projectile(
            start_x=spawn_x,
            start_y=spawn_y,
            target_x=target_ground_x,
            target_y=target_ground_y,
            damage=self.damage,
            aoe_radius=self.aoe_radius,
        )
        return new_bullet
